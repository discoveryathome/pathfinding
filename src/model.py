"""Pilot model and efficient metrics. Independent verifier lives in verify.py."""
from collections import deque
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]

def read_map(path):
    lines=Path(path).read_text().splitlines();h=int(lines[1].split()[1]);w=int(lines[2].split()[1]);rows=lines[4:]
    if len(rows)!=h or any(len(row)!=w for row in rows):raise ValueError('Bad map dimensions')
    free={y*w+x for y,row in enumerate(rows) for x,c in enumerate(row) if c in '.GS'}
    adj={v:tuple(u for u in (v-w,v+w,v-1,v+1) if u in free and abs(u%w-v%w)+abs(u//w-v//w)==1) for v in sorted(free)}
    return {'w':w,'h':h,'rows':rows,'adj':adj}

def read_instance(path):
    ins=json.loads(Path(path).read_text());grid=read_map(ROOT/ins['map']);ins['grid']=grid;return ins

def distances(grid,goal):
    dist={goal:0};q=deque([goal])
    while q:
        v=q.popleft()
        for u in grid['adj'][v]:
            if u not in dist:dist[u]=dist[v]+1;q.append(u)
    return dist

def at(path,t):return path[min(t,len(path)-1)]

def trim(path):
    path=list(path)
    while len(path)>1 and path[-2]==path[-1]:path.pop()
    return path

def path_loss(p):
    g=p[-1];return sum(a!=g or b!=g for a,b in zip(p,p[1:]))

def metrics(paths):return {'soc':sum(len(trim(p))-1 for p in paths),'sol':sum(path_loss(p) for p in paths),'makespan':max(len(trim(p))-1 for p in paths)}

def dominates(a,b):return a['soc']<=b['soc'] and a['sol']<=b['sol'] and a['makespan']<=b['makespan'] and (a['soc']<b['soc'] or a['sol']<b['sol'])
