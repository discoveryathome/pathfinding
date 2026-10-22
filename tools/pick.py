from pathlib import Path
import argparse,json,random
root=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--seed',type=int,default=42);a=p.parse_args();r=random.Random(a.seed)
c=json.loads((root/'discover/catalog.json').read_text());t=r.choices(c['tracks'],weights=[t['weight'] for t in c['tracks']])[0]
print(json.dumps({'intake':'open','track':t['id'],'task':r.choice(t['tasks']),'incumbents':'discover/incumbents.json'},indent=2))
