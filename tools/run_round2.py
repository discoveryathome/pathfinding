"""Prespecified development/evaluation repairs with separately verified routes."""
from pathlib import Path
import hashlib, json, os, sys, time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from model import read_instance
from repair_round2 import run
from verify import check
DEST=ROOT/'research/round2'
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def main():
    if (DEST/'trial.json').exists():raise SystemExit('Frozen round exists; replay in a copy')
    cases=json.loads((DEST/'baselines.json').read_text());outdir=DEST/'repair';outdir.mkdir(exist_ok=True)
    rows=[];selected=None;start=time.perf_counter()
    for split in ['development','heldout']:
        variants=['random4','proximity4','corridor4','joint2'] if split=='development' else ['random4',selected if selected!='random4' else 'proximity4']
        for case in cases:
            if case['split']!=split:continue
            if not case['inherited']:
                rows.append({'case':case['id'],'split':split,'status':'no_feasible_start'});continue
            ip=ROOT/case['instance'];ins=read_instance(ip)
            base=json.loads((ROOT/case['inherited']).read_text());check(ip,base)
            for variant in variants:
                for seed in [101,211,307]:
                    r=run(ins,base['paths'],variant,seed)
                    cert={'instance_sha256':hashlib.sha256(ip.read_bytes()).hexdigest(),'paths':r['paths'],
                          'metrics':r['metrics'],'method':variant,'seed':seed}
                    verified=check(ip,cert)
                    for step in r['improvements']:check(ip,{**cert,'paths':step['paths'],'metrics':step['metrics']})
                    stem=case['id']+'-'+variant+'-'+str(seed)
                    cp=outdir/(stem+'.json');trace=outdir/(stem+'-trace.json')
                    cp.write_text(json.dumps(cert)+'\n');trace.write_text(json.dumps(r)+'\n')
                    row={'case':case['id'],'split':split,'status':'verified','variant':variant,'seed':seed,
                         'instance':case['instance'],'inherited':case['inherited'],'before':base['metrics'],
                         'after':r['metrics'],'certificate':str(cp.relative_to(ROOT)),
                         'trace':str(trace.relative_to(ROOT)),'budget':r['budget'],
                         'elapsed_seconds':r['elapsed_seconds'],'improvements':len(r['improvements']),
                         'failed_attempts':sum(x['status']!='complete' for x in r['history'])}
                    rows.append(row);save(DEST/'runs-progress.json',rows)
                    print(case['id'],variant,seed,base['metrics']['sol'],'->',r['metrics']['sol'],flush=True)
        if split=='development':
            totals={v:tuple(sum(r['after'][metric] for r in rows if r.get('variant')==v) for metric in ['sol','soc']) for v in variants}
            selected=min(variants,key=lambda v:(totals[v],v))
            if totals[selected]>=totals['random4']:selected='random4'
            save(DEST/'selection.json',{'selected':selected,'totals':totals,'rule':'protocol lexicographic SOL then SOC; strict improvement over random4 required'})
            print('FROZEN SELECTION',selected,totals,flush=True)
    # Replay one full run including every accepted intermediate path and history.
    first=next(r for r in rows if r['status']=='verified')
    before=json.loads((ROOT/first['inherited']).read_text())
    replay=run(read_instance(ROOT/first['instance']),before['paths'],first['variant'],first['seed'])
    original=json.loads((ROOT/first['trace']).read_text())
    assert all(replay[k]==original[k] for k in ['paths','metrics','history','budget','improvements'])
    save(DEST/'trial.json',{'selected':selected,'runs':rows,'replay_equal':True,'elapsed_seconds':time.perf_counter()-start,
                          'load_average':os.getloadavg(),'author_run':True,'independent_review':False})
    print('round two complete',flush=True)
if __name__=='__main__':main()
