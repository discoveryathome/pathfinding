"""Valid lower bound from disjoint pairs with unavoidable shortest-path conflicts."""
from pathlib import Path
import argparse, hashlib, json, sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from model import read_instance, distances

def bound(ins, horizon=32):
    grid=ins['grid'];forced=[];ds=[]
    for s,g in zip(ins['starts'],ins['goals']):
        a,b=distances(grid,s),distances(grid,g);d=a[g];ds.append(d)
        levels={t:[] for t in range(min(d,horizon)+1)}
        for v,t in a.items():
            if t in levels and v in b and t+b[v]==d:levels[t].append(v)
        forced.append([g if t>=d else (levels[t][0] if len(levels[t])==1 else None)
                       for t in range(horizon+1)])
    edges=[]
    for i in range(len(ds)):
        for j in range(i):
            for t in range(1,horizon+1):
                a,b=forced[i][t],forced[j][t]
                vertex=a is not None and a==b
                swap=(a is not None and b is not None and
                      forced[i][t-1]==b and forced[j][t-1]==a)
                if vertex or swap:
                    edges.append({'agents':[j,i],'time':t,'kind':'vertex' if vertex else 'edge-swap'});break
    # Any disjoint matching gives a valid additive bound; maximal does not mean maximum.
    used=set();matching=[]
    for edge in edges:
        i,j=edge['agents']
        if i not in used and j not in used:used.update([i,j]);matching.append(edge)
    return {'individual_distance_bound':sum(ds),'pair_conflict_bound':sum(ds)+len(matching),
            'disjoint_pair_witnesses':matching,'conflicting_pairs':len(edges),'horizon':horizon,
            'claim':'Lower bound on both SOL and SOC; remaining gap is not necessarily attainable.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args()
    out=(ROOT/a.out).resolve()
    if out.exists() or not out.is_relative_to(ROOT/'research'):p.error('Use a new research output file')
    rows=[]
    for case in json.loads((ROOT/'discover/incumbents.json').read_text()):
        ip=ROOT/case['instance'];data=bound(read_instance(ip));inc=case['pareto_candidates'][0]
        m=json.loads((ROOT/inc['path']).read_text())['metrics'];assert data['pair_conflict_bound']<=min(m['sol'],m['soc'])
        rows.append({'case':case['case'],'instance_sha256':hashlib.sha256(ip.read_bytes()).hexdigest(),
                     'incumbent':inc,'metrics':m,**data,'sol_gap':m['sol']-data['pair_conflict_bound']})
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(sorted(rows,key=lambda r:-r['sol_gap']),indent=2)+'\n')
    print(json.dumps({'cases':len(rows),'bound_improved_cases':sum(r['pair_conflict_bound']>r['individual_distance_bound'] for r in rows),'out':str(out)}))

if __name__=='__main__':main()
