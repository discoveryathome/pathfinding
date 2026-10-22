from pathlib import Path
import sys,json,hashlib,itertools,heapq
import pytest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import model,verify,repair

def fixture(tmp_path,monkeypatch,starts,goals,paths):
    monkeypatch.setattr(verify,'ROOT',tmp_path);monkeypatch.setattr(model,'ROOT',tmp_path)
    mp=tmp_path/'tiny.map';mp.write_text('type octile\nheight 2\nwidth 3\nmap\n...\n...\n')
    ip=tmp_path/'instance.json';ip.write_text(json.dumps({'map':'tiny.map','map_sha256':hashlib.sha256(mp.read_bytes()).hexdigest(),'starts':starts,'goals':goals}))
    cert={'instance_sha256':hashlib.sha256(ip.read_bytes()).hexdigest(),'paths':paths,'metrics':model.metrics(paths)}
    return ip,cert,model.read_instance(ip)

def test_valid_detour_and_goal_holding(tmp_path,monkeypatch):
    ip,c,_=fixture(tmp_path,monkeypatch,[0,2],[2,0],[[0,3,4,5,2],[2,1,0]])
    assert verify.check(ip,c)=={'soc':6,'sol':6,'makespan':4,'individual_distance_lower_bound':4,'agents':2,'checked_timesteps':5}

@pytest.mark.parametrize('kind',['empty','teleport','wrong_goal','wrong_cost','wrong_binding','obstacle'])
def test_reject_bad_certificate(tmp_path,monkeypatch,kind):
    ip,c,_=fixture(tmp_path,monkeypatch,[0,2],[2,0],[[0,3,4,5,2],[2,1,0]])
    if kind=='empty':c['paths']=[]
    if kind=='teleport':c['paths'][0]=[0,2]
    if kind=='wrong_goal':c['paths'][0][-1]=1
    if kind=='wrong_cost':c['metrics']['soc']-=1
    if kind=='wrong_binding':c['instance_sha256']='0'*64
    if kind=='obstacle':c['paths'][0][1]=-1
    with pytest.raises((ValueError,IndexError)):verify.check(ip,c)

def test_vertex_collision(tmp_path,monkeypatch):
    ip,c,_=fixture(tmp_path,monkeypatch,[0,2],[2,0],[[0,1,2],[2,1,0]])
    with pytest.raises(ValueError,match='Vertex'):verify.check(ip,c)

def test_edge_swap(tmp_path,monkeypatch):
    ip,c,_=fixture(tmp_path,monkeypatch,[0,1],[1,0],[[0,1],[1,0]])
    with pytest.raises(ValueError,match='Edge swap'):verify.check(ip,c)

def test_goal_revisit_metrics(tmp_path,monkeypatch):
    ip,c,_=fixture(tmp_path,monkeypatch,[0,5],[1,4],[[0,1,1,0,1],[5,4]])
    r=verify.check(ip,c);assert r['soc']==5 and r['sol']==4 and r['makespan']==4

def joint_optimum(ins):
    starts=tuple(ins['starts']);goals=tuple(ins['goals']);dist={starts:0};queue=[(0,starts)]
    while queue:
        cost,q=heapq.heappop(queue)
        if cost!=dist[q]:continue
        if q==goals:return cost
        for nxt in itertools.product(*[ins['grid']['adj'][v]+(v,) for v in q]):
            if len(set(nxt))<len(q) or any(q[i]==nxt[j] and q[j]==nxt[i] for i in range(len(q)) for j in range(i)):continue
            new=cost+sum(q[i]!=goals[i] or nxt[i]!=goals[i] for i in range(len(q)))
            if new<dist.get(nxt,10**9):dist[nxt]=new;heapq.heappush(queue,(new,nxt))
    return None

def test_exact_joint_control_and_lower_bound(tmp_path,monkeypatch):
    ip,c,ins=fixture(tmp_path,monkeypatch,[0,2],[2,0],[[0,3,4,5,2],[2,1,0]])
    assert joint_optimum(ins)==6
    assert verify.check(ip,c)['individual_distance_lower_bound']==4

def test_astar_future_goal_block_and_budget(tmp_path,monkeypatch):
    _,_,ins=fixture(tmp_path,monkeypatch,[0],[1],[[0,1]])
    grid=ins['grid'];d=model.distances(grid,1);occ=[set(),{1},set(),set()];edges=[set() for _ in occ]
    p,n,status=repair.space_time_astar(grid,0,1,d,occ,edges,3,100)
    assert p==[0,0,1] and status=='found'
    assert repair.space_time_astar(grid,0,1,d,occ,edges,3,0)[2]=='budget'

@pytest.mark.parametrize('variant',repair.VARIANTS)
def test_repair_budget_determinism_and_no_regression(tmp_path,monkeypatch,variant):
    ip,c,ins=fixture(tmp_path,monkeypatch,[0,2],[2,0],[[0,0,3,4,5,2],[2,1,1,0]])
    a=repair.improve(ins,c['paths'],variant,17,node_budget=200,attempts=6)
    b=repair.improve(ins,c['paths'],variant,17,node_budget=200,attempts=6)
    assert a['paths']==b['paths'] and a['history']==b['history']
    assert a['budget']['nodes_used']<=200
    assert all(a['metrics'][k]<=c['metrics'][k] for k in ['soc','sol','makespan'])
    verify.check(ip,{**c,'paths':a['paths'],'metrics':a['metrics']})
