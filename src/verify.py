"""Standalone pairwise certificate checker; no search-engine imports."""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[1]

def check(instance_file,certificate):
    raw=Path(instance_file).read_bytes();ins=json.loads(raw)
    if certificate.get('instance_sha256')!=hashlib.sha256(raw).hexdigest():raise ValueError('Wrong instance binding')
    map_bytes=(ROOT/ins['map']).read_bytes()
    if hashlib.sha256(map_bytes).hexdigest()!=ins['map_sha256']:raise ValueError('Wrong map binding')
    lines=map_bytes.decode().splitlines();height=int(lines[1].split()[1]);width=int(lines[2].split()[1]);rows=lines[4:]
    if len(rows)!=height or any(len(r)!=width for r in rows):raise ValueError('Malformed grid')
    paths=certificate['paths'];starts=ins['starts'];goals=ins['goals'];n=len(starts)
    if n==0 or len(paths)!=n or len(goals)!=n or len(set(starts))!=n or len(set(goals))!=n:raise ValueError('Agent count or duplicate endpoints')
    def legal(v):return type(v) is int and 0<=v<width*height and rows[v//width][v%width] in '.GS'
    for i,p in enumerate(paths):
        if not p or p[0]!=starts[i] or p[-1]!=goals[i]:raise ValueError('Empty path or wrong endpoint')
        if not all(legal(v) for v in p):raise ValueError('Obstacle or out-of-range cell')
        if any(abs(a%width-b%width)+abs(a//width-b//width)>1 for a,b in zip(p,p[1:])):raise ValueError('Illegal move')
    T=max(map(len,paths))-1
    def pos(i,t):return paths[i][min(t,len(paths[i])-1)]
    previous=None
    for t in range(T+1):
        current=[pos(i,t) for i in range(n)]
        for i in range(n):
            for j in range(i):
                if current[i]==current[j]:raise ValueError(f'Vertex collision at {t}')
                if t and current[i]==previous[j] and current[j]==previous[i]:raise ValueError(f'Edge swap at {t}')
        previous=current
    arrivals=[];loss=0;lower=0
    for i,p in enumerate(paths):
        arrival=max((t+1 for t,v in enumerate(p) if v!=goals[i]),default=0);arrivals.append(arrival)
        loss+=sum(p[t-1]!=goals[i] or p[t]!=goals[i] for t in range(1,len(p)))
        # Independently implement wavefront distance with coordinate bounds, not optimizer adjacency.
        frontier={starts[i]};seen=set(frontier);d=0
        while goals[i] not in frontier:
            nxt=set()
            for v in frontier:
                x,y=v%width,v//width
                for xx,yy in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
                    u=yy*width+xx
                    if 0<=xx<width and 0<=yy<height and legal(u) and u not in seen:nxt.add(u)
            if not nxt:raise ValueError('Disconnected start/goal')
            seen.update(nxt);frontier=nxt;d+=1
        lower+=d
    m={'soc':sum(arrivals),'sol':loss,'makespan':max(arrivals)}
    if certificate.get('metrics')!=m:raise ValueError(f'Incorrect claimed metrics: {certificate.get("metrics")} != {m}')
    if min(m['soc'],m['sol'])<lower:raise ValueError('Impossible lower-bound violation')
    return {**m,'individual_distance_lower_bound':lower,'agents':n,'checked_timesteps':T+1}

def main():
    p=argparse.ArgumentParser();p.add_argument('instance');p.add_argument('candidate');a=p.parse_args()
    result=check(a.instance,json.loads(Path(a.candidate).read_text()));print(json.dumps({'verified':True,**result}))
if __name__=='__main__':main()
