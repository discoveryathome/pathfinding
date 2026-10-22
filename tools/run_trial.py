from pathlib import Path
import sys,json,hashlib,time,platform
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from model import read_instance
from repair import improve,VARIANTS
from verify import check
BASE=json.loads((ROOT/'results/baselines.json').read_text());SEEDS=[17,29];out=ROOT/'results/repair';out.mkdir(exist_ok=True);records=[];start=time.time()

def run_case(case,variant,seed):
    ip=ROOT/case['instance'];ins=read_instance(ip);inc=json.loads((ROOT/case['inherited']).read_text());result=improve(ins,inc['paths'],variant,seed)
    key=f'{case["id"]}-{variant}-s{seed}';cert={'instance_sha256':hashlib.sha256(ip.read_bytes()).hexdigest(),'paths':result['paths'],'metrics':result['metrics'],'method':variant,'seed':seed}
    verified=check(ip,cert)
    # Every accepted intermediate route is checked, not just the final result.
    for item in result['improvements']:check(ip,{**cert,'paths':item['paths'],'metrics':item['metrics']})
    (out/f'{key}.json').write_text(json.dumps(cert)+'\n');(out/f'{key}-trace.json').write_text(json.dumps(result)+'\n')
    row={'case':case['id'],'split':case['split'],'variant':variant,'seed':seed,'initial_metrics':inc['metrics'],'metrics':verified,'budget':result['budget'],'elapsed_seconds':result['elapsed_seconds'],'accepted_repairs':len(result['improvements']),'certificate':str((out/f'{key}.json').relative_to(ROOT)),'trace':str((out/f'{key}-trace.json').relative_to(ROOT))};records.append(row)
    (ROOT/'results/runs.json').write_text(json.dumps(records,indent=2)+'\n');print(key,inc['metrics'],'->',cert['metrics'],'states',result['budget']['nodes_used'],flush=True)
    return result

for case in BASE:
    if case['split']!='development' or not case['inherited']:continue
    for variant in VARIANTS:
        for seed in SEEDS:run_case(case,variant,seed)
scores={}
for v in VARIANTS:
    rr=[r for r in records if r['variant']==v];scores[v]={'sol':sum(r['metrics']['sol'] for r in rr),'soc':sum(r['metrics']['soc'] for r in rr),'runs':len(rr)}
pair=lambda v:(scores[v]['sol'],scores[v]['soc'])
selected=min(VARIANTS,key=lambda v:(*pair(v),v));selected=selected if pair(selected)<pair('random4') else 'random4'
selection={'selected':selected,'development_scores':scores,'rule':'lowest total SOL then SOC across development runs; promote only if lexicographically better than random4; frozen before held-out repair','heldout_started_at_selection':False}
(ROOT/'results/selection.json').write_text(json.dumps(selection,indent=2)+'\n');print('SELECTED',selected,flush=True)
for case in BASE:
    if case['split']!='heldout' or not case['inherited']:continue
    for variant in sorted(set(['random4',selected])):
        for seed in SEEDS:run_case(case,variant,seed)
# Repeat a completed run without choosing based on performance; compare deterministic fields.
first=next(c for c in BASE if c['inherited']);ip=ROOT/first['instance'];inc=json.loads((ROOT/first['inherited']).read_text());repeat=improve(read_instance(ip),inc['paths'],'random4',17)
original=json.loads((out/f'{first["id"]}-random4-s17-trace.json').read_text())
assert all(repeat[k]==original[k] for k in ['paths','metrics','history','budget','improvements'])
report={'kind':'author-run bounded MAPF repair trial','selected':selected,'development_scores':scores,'runs':records,'deterministic_replay':True,'total_elapsed_seconds':time.time()-start,'machine':platform.platform(),'baseline_failures':[c['id'] for c in BASE if not c['inherited']],'limitations':['Known neighborhood repair, no novelty claim','Fixed search states are not equal CPU or all-operation budgets','LaCAM baseline and context runs are wall-deadline-limited and asynchronous; exact witnesses are frozen','No global optimality unless independently proved; individual BFS bound may be loose','Synthetic grids and discrete point agents, not robot safety validation']}
(ROOT/'results/trial.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'selected':selected,'runs':len(records),'elapsed_seconds':report['total_elapsed_seconds']}))
