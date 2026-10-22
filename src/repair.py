"""Bounded prioritized neighborhood repair (known MAPF/LNS technique)."""
from heapq import heappush,heappop
import random,time
from model import at,trim,path_loss,metrics,dominates,distances
VARIANTS={'random4':('random',4),'regret1':('regret',1),'regret4':('regret',4),'proximity4':('proximity',4),'proximity8':('proximity',8)}

def reservations(paths,removed,T):
    occupied=[set() for _ in range(T+1)];edges=[set() for _ in range(T+1)]
    for i,p in enumerate(paths):
        if i in removed:continue
        for t in range(T+1):
            v=at(p,t);occupied[t].add(v)
            if t:edges[t].add((at(p,t-1),v))
    return occupied,edges

def add_path(p,occupied,edges,T):
    for t in range(T+1):
        v=at(p,t);occupied[t].add(v)
        if t:edges[t].add((at(p,t-1),v))

def space_time_astar(grid,start,goal,dist,occupied,edges,T,budget):
    if start in occupied[0] or start not in dist:return None,0,'blocked_start'
    last_block=max((t for t,s in enumerate(occupied) if goal in s),default=-1)
    queue=[(dist[start],0,start)];seen={(start,0)};parent={};pops=0
    while queue and pops<budget:
        _,minus_t,v=heappop(queue);t=-minus_t;pops+=1
        if v==goal and t>last_block:
            state=(v,t);path=[v]
            while state in parent:state=parent[state];path.append(state[0])
            return list(reversed(path)),pops,'found'
        if t==T:continue
        nt=t+1
        for u in grid['adj'][v]+(v,):
            if u in occupied[nt] or (u,v) in edges[nt] or u not in dist or nt+dist[u]>T:continue
            state=(u,nt)
            if state in seen:continue
            seen.add(state);parent[state]=(v,t);heappush(queue,(nt+dist[u],-nt,u))
    return None,pops,'budget' if queue else 'exhausted'

def choose(paths,distances_by_agent,grid,style,k,rng):
    n=len(paths);regret=[len(p)-1-distances_by_agent[i][p[0]] for i,p in enumerate(paths)]
    if style=='random':return rng.sample(range(n),min(k,n))
    anchor=rng.choices(range(n),weights=[r+1 for r in regret])[0]
    if k==1:return [anchor]
    if style=='regret':
        others=[i for i in range(n) if i!=anchor];jitter={i:rng.random() for i in others}
        others.sort(key=lambda i:(-regret[i],jitter[i],i));group=[anchor]+others[:k-1]
    else:
        w=grid['w'];pa=paths[anchor];score={}
        for i,p in enumerate(paths):
            if i==anchor:continue
            score[i]=sum(abs(at(p,t)%w-at(pa,t)%w)+abs(at(p,t)//w-at(pa,t)//w)<=1 for t in range(min(64,max(len(p),len(pa)))))
        jitter={i:rng.random() for i in score}
        group=[anchor]+sorted(score,key=lambda i:(-score[i],-regret[i],jitter[i],i))[:k-1]
    rng.shuffle(group);return group

def improve(ins,initial,variant,seed,node_budget=30000,attempts=64,agent_cap=3000):
    start=time.perf_counter();paths=[trim(p) for p in initial];rng=random.Random(seed);grid=ins['grid']
    dist=[distances(grid,g) for g in ins['goals']];preprocess=time.perf_counter()-start
    style,k=VARIANTS[variant];used=0;history=[];improvements=[]
    for attempt in range(attempts):
        if used>=node_budget:break
        before=metrics(paths);T=before['makespan'];group=choose(paths,dist,grid,style,k,rng)
        occupied,edges=reservations(paths,set(group),T);candidate=[p[:] for p in paths];popped=0;status='complete'
        for i in group:
            remaining=min(agent_cap,node_budget-used)
            if remaining<=0:status='total_budget';break
            p,work,status_i=space_time_astar(grid,ins['starts'][i],ins['goals'][i],dist[i],occupied,edges,T,remaining)
            used+=work;popped+=work
            if p is None:status=status_i;break
            candidate[i]=trim(p);add_path(candidate[i],occupied,edges,T)
        after=metrics(candidate) if status=='complete' else before
        accepted=status=='complete' and dominates(after,before)
        if accepted:
            paths=candidate;improvements.append({'attempt':attempt,'metrics':after,'paths':[p[:] for p in paths]})
        history.append({'attempt':attempt,'agents':group,'popped':popped,'status':status,'accepted':accepted,'before':before,'proposed':after})
    return {'paths':paths,'metrics':metrics(paths),'variant':variant,'seed':seed,'budget':{'node_limit':node_budget,'nodes_used':used,'attempt_limit':attempts,'attempts_used':len(history),'per_agent_limit':agent_cap},'preprocess_seconds':preprocess,'elapsed_seconds':time.perf_counter()-start,'history':history,'improvements':improvements}
