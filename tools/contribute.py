"""One bounded contribution from the current local incumbent archive."""
from pathlib import Path
import argparse,json,sys,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from model import read_instance
from repair import improve,VARIANTS
from verify import check
p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--variant',choices=list(VARIANTS),default='random4');p.add_argument('--seed',type=int,required=True);p.add_argument('--nodes',type=int,default=30000);p.add_argument('--out',required=True);a=p.parse_args()
if not 1<=a.nodes<=1000000:raise SystemExit('Use 1–1,000,000 popped states for this bounded command')
dest=(ROOT/a.out).resolve()
if not dest.is_relative_to(ROOT/'research') or dest.exists():raise SystemExit('Choose a new research/<session> directory')
case=next(c for c in json.loads((ROOT/'discover/incumbents.json').read_text()) if c['case']==a.case);start=case['pareto_candidates'][0]
ip=ROOT/case['instance'];source=ROOT/start['path'];assert hashlib.sha256(source.read_bytes()).hexdigest()==start['sha256'];base=json.loads(source.read_text());check(ip,base)
r=improve(read_instance(ip),base['paths'],a.variant,a.seed,node_budget=a.nodes);cert={'instance_sha256':hashlib.sha256(ip.read_bytes()).hexdigest(),'paths':r['paths'],'metrics':r['metrics'],'method':a.variant,'seed':a.seed}
result=check(ip,cert)
for item in r['improvements']:check(ip,{**cert,'paths':item['paths'],'metrics':item['metrics']})
dest.mkdir();(dest/'candidate.json').write_text(json.dumps(cert)+'\n');(dest/'trace.json').write_text(json.dumps(r)+'\n');(dest/'handoff.json').write_text(json.dumps({'case':a.case,'inherited':start,'candidate_metrics':result,'budget':r['budget'],'agent_provenance':'Fill in before review','independent_review':False,'exposed_inputs':True},indent=2)+'\n');print(json.dumps({'saved':str(dest),'initial':base['metrics'],'candidate':result,'budget':r['budget']}))
