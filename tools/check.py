from pathlib import Path
import argparse,hashlib,json,subprocess,sys,time
from jsonschema import Draft202012Validator,FormatChecker
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));from verify import check
p=argparse.ArgumentParser();p.add_argument('--quick',action='store_true');a=p.parse_args();start=time.perf_counter()
for name,path in [('manifest','discover.json'),('catalog','discover/catalog.json'),('frontier','discover/frontier.json')]:
 Draft202012Validator(json.loads((ROOT/f'spec/{name}.schema.json').read_text()),format_checker=FormatChecker()).validate(json.loads((ROOT/path).read_text()))
assert sum(t['weight'] for t in json.loads((ROOT/'discover/catalog.json').read_text())['tracks'])==100
for path,h in json.loads((ROOT/'research/manifest.json').read_text())['sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,f'Frozen artifact changed: {path}'
assert json.loads((ROOT/'discover.json').read_text())['review']['paused'] is False
count=0
if not a.quick:
 subprocess.run([sys.executable,'-m','pytest','-q','tests'],cwd=ROOT,check=True)
 cases=json.loads((ROOT/'results/baselines.json').read_text());byid={c['id']:c for c in cases}
 for c in cases:
  for r in c['runs'].values():
   if r['status']=='verified':check(ROOT/c['instance'],json.loads((ROOT/r['certificate']).read_text()));count+=1
 for r in json.loads((ROOT/'results/trial.json').read_text())['runs']:
  ip=ROOT/byid[r['case']]['instance'];cert=json.loads((ROOT/r['certificate']).read_text());check(ip,cert);count+=1
  trace=json.loads((ROOT/r['trace']).read_text())
  for item in trace['improvements']:check(ip,{**cert,'paths':item['paths'],'metrics':item['metrics']});count+=1
print(json.dumps({'passed':True,'intake':'open','scientific_review':'pending','certificates_checked':count,'elapsed_seconds':time.perf_counter()-start}))
