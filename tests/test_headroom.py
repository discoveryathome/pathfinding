from pathlib import Path
import heapq,importlib.util,itertools,random
spec=importlib.util.spec_from_file_location('headroom',Path(__file__).resolve().parents[1]/'tools/headroom.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)

def optimum(adj, starts, goals):
    goals=tuple(goals);starts=tuple(starts);queue=[(0,starts)];best={starts:0}
    while queue:
        cost,p=heapq.heappop(queue)
        if cost!=best[p]:continue
        if p==goals:return cost
        for n in itertools.product(*[(v,*adj[v]) for v in p]):
            if len(set(n))<len(n) or n[0]==p[1] and n[1]==p[0]:continue
            c=cost+sum(a!=g or b!=g for a,b,g in zip(p,n,goals))
            if c<best.get(n,10**9):best[n]=c;heapq.heappush(queue,(c,n))
    return 10**9

def test_pair_bound_against_exact_joint_search():
    adj={0:(1,),1:(0,2,4),2:(1,),4:(1,)}
    ins={'grid':{'adj':adj},'starts':[0,2],'goals':[2,0]}
    b=h.bound(ins);assert b['pair_conflict_bound']>b['individual_distance_bound']
    assert b['pair_conflict_bound']<=optimum(adj,ins['starts'],ins['goals'])
    rng=random.Random(41);pairs=list(itertools.permutations(adj,2))
    for _ in range(40):
        ins['starts']=rng.choice(pairs);ins['goals']=rng.choice(pairs)
        assert h.bound(ins)['pair_conflict_bound']<=optimum(adj,ins['starts'],ins['goals'])
