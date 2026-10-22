"""Summarize all outcomes and promote verified local witnesses, not novelty claims."""
from pathlib import Path
import hashlib, json
ROOT=Path(__file__).resolve().parents[1];DEST=ROOT/'research/round2'
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def key(m):return tuple(m[k] for k in ['sol','soc','makespan'])
def dominates(a,b):return all(a[k]<=b[k] for k in ['sol','soc','makespan']) and any(a[k]<b[k] for k in ['sol','soc','makespan'])
def main():
    bases=json.loads((DEST/'baselines.json').read_text());trial=json.loads((DEST/'trial.json').read_text())
    rows=[r for r in trial['runs'] if r['status']=='verified'];groups={}
    for split in ['development','heldout']:
        for variant in sorted(set(r['variant'] for r in rows if r['split']==split)):
            chosen=[r for r in rows if r['split']==split and r['variant']==variant]
            groups[split+'/'+variant]={'runs':len(chosen),
                'before':{k:sum(r['before'][k] for r in chosen) for k in ['sol','soc']},
                'after':{k:sum(r['after'][k] for r in chosen) for k in ['sol','soc']},
                'primary_improved_runs':sum(r['after']['sol']<r['before']['sol'] for r in chosen),
                'any_improved_runs':sum(r['improvements']>0 for r in chosen),
                'elapsed_seconds':sum(r['elapsed_seconds'] for r in chosen),
                'nodes_used':sum(r['budget']['nodes_used'] for r in chosen),
                'failed_attempts':sum(r['failed_attempts'] for r in chosen)}
    archive=json.loads((ROOT/'discover/incumbents.json').read_text())
    old=[c for c in archive if c['case'] not in {c['id'] for c in bases}]
    percase=[];trial_primary_gain=0
    smoke_path=ROOT/'research/round2-smoke/candidate.json'
    smoke_handoff=json.loads((ROOT/'research/round2-smoke/handoff.json').read_text()) if smoke_path.exists() else None
    for case in bases:
        paths=[r['certificate'] for r in case['runs'] if r['status']=='verified']
        paths += [r['certificate'] for r in rows if r['case']==case['id']]
        best_native_sol=min(r['metrics']['sol'] for r in case['runs'] if r['status']=='verified')
        best_trial_sol=min(json.loads((ROOT/p).read_text())['metrics']['sol'] for p in paths)
        trial_primary_gain+=best_native_sol-best_trial_sol
        if smoke_handoff and smoke_handoff['case']==case['id']:
            paths.append(str(smoke_path.relative_to(ROOT)))
        candidates=[]
        for path in paths:
            cp=ROOT/path;cert=json.loads(cp.read_text());m=cert['metrics']
            if any(c['metrics']==m for c in candidates):continue
            candidates.append({'path':path,'sha256':hashlib.sha256(cp.read_bytes()).hexdigest(),'metrics':m})
        keep=[c for c in candidates if not any(dominates(other['metrics'],c['metrics']) for other in candidates)]
        keep.sort(key=lambda c:key(c['metrics']))
        old.append({'case':case['id'],'instance':case['instance'],'pareto_candidates':keep})
        native=min((r['metrics'] for r in case['runs'] if r['status']=='verified'),key=key)
        percase.append({'case':case['id'],'native_best':{k:native[k] for k in ['sol','soc','makespan']},
                        'archive_best':keep[0]['metrics'],'primary_gain':native['sol']-keep[0]['metrics']['sol'],
                        'best_path':keep[0]['path'],'pareto_candidates':len(keep)})
    summary={'selected':trial['selected'],'instances':len(bases),'repair_runs':len(rows),'aggregates':groups,
             'native_runs':sum(len(c['runs']) for c in bases),
             'native_verified':sum(r['status']=='verified' for c in bases for r in c['runs']),
             'native_failures':[{'case':c['id'],**r} for c in bases for r in c['runs'] if r['status']!='verified'],
             'cases_with_primary_archive_gain':sum(c['primary_gain']>0 for c in percase),
             'sum_best_case_primary_gains':sum(c['primary_gain'] for c in percase),
             'trial_only_sum_primary_gains':trial_primary_gain,
             'additional_author_smoke_primary_gain':sum(c['primary_gain'] for c in percase)-trial_primary_gain,
             'cases':percase,'replay_equal':trial['replay_equal']}
    save(DEST/'summary.json',summary);save(ROOT/'discover/incumbents.json',old)
    print(json.dumps({k:v for k,v in summary.items() if k not in ['cases','native_failures']},indent=2))
if __name__=='__main__':main()
