import itertools
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from model import distances, metrics
from repair_round2 import joint_astar, run
from repair import reservations

def grid():
    # Six-cell loop permits a swap by routing around the other agent.
    free=set(range(6));w=3
    return {'w':w,'h':2,'adj':{v:tuple(u for u in free if abs(u%w-v%w)+abs(u//w-v//w)==1) for v in free}}

def exact_sol(g,starts,goals,horizon):
    # Independent finite-horizon dynamic program, no heuristic or search queue.
    states={tuple(starts):0};answer=float('inf')
    for _ in range(horizon+1):
        answer=min(answer,states.get(tuple(goals),float('inf')))
        nxt={}
        for pos,cost in states.items():
            for q in itertools.product(*(g['adj'][v]+(v,) for v in pos)):
                if q[0]==q[1] or (q[0]==pos[1] and q[1]==pos[0]):continue
                value=cost+sum(a!=goal or b!=goal for a,b,goal in zip(pos,q,goals))
                nxt[q]=min(nxt.get(q,float('inf')),value)
        states=nxt
    return answer

def test_joint_matches_exact_dynamic_program():
    g=grid();starts=[0,2];goals=[2,0];horizon=6
    ds=[distances(g,v) for v in goals]
    paths,used,status=joint_astar(g,starts,goals,ds,[set() for _ in range(7)],[set() for _ in range(7)],horizon,10000)
    assert status=='found' and used<=10000
    assert metrics(paths)['sol']==exact_sol(g,starts,goals,horizon)==6
    for a,b in zip(zip(*paths),list(zip(*paths))[1:]):
        assert b[0]!=b[1] and not(a[0]==b[1] and a[1]==b[0])

def test_joint_future_goal_block_and_cap():
    g=grid();ds=[distances(g,v) for v in [1,2]]
    occ=[set() for _ in range(7)];occ[3]={1}
    paths,_,status=joint_astar(g,[0,5],[1,2],ds,occ,[set() for _ in range(7)],6,10000)
    assert status=='found' and paths[0][3]!=1 and paths[0][-1]==1
    assert joint_astar(g,[0,5],[1,2],ds,occ,[set() for _ in range(7)],6,0)==(None,0,'budget')

def test_round2_deterministic_replay_and_no_regression():
    g=grid();ins={'grid':g,'starts':[0,2],'goals':[2,0]}
    initial=[[0,0,1,2,2],[2,5,4,3,0]]
    for variant in ['corridor4','joint2']:
        a=run(ins,initial,variant,17,node_budget=500,attempts=8,agent_cap=100)
        b=run(ins,initial,variant,17,node_budget=500,attempts=8,agent_cap=100)
        assert a['paths']==b['paths'] and a['history']==b['history'] and a['budget']==b['budget']
        assert a['budget']['nodes_used']<=500
        assert all(a['metrics'][k]<=metrics(initial)[k] for k in ['sol','soc','makespan'])
