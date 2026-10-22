from pathlib import Path
import argparse,json,random
p=argparse.ArgumentParser();p.add_argument('--seed',type=int,default=42);p.add_argument('--task');a=p.parse_args()
root=Path(__file__).resolve().parents[1];catalog=json.loads((root/'discover/catalog.json').read_text());r=random.Random(a.seed)
if a.task:
 pairs=[(t,x) for t in catalog['tracks'] for x in t['tasks'] if x['id']==a.task]
 if len(pairs)!=1:p.error('Unknown task; read FIRST_TASKS.md')
 t,x=pairs[0]
else:
 t=r.choices(catalog['tracks'],weights=[t['weight'] for t in catalog['tracks']])[0];x=r.choice(t['tasks'])
print(json.dumps({'intake':'open','track':t['id'],'task':x},indent=2))
