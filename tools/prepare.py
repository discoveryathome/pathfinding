from pathlib import Path
import sys,json,hashlib,subprocess,time,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from model import read_map,trim,metrics
from verify import check
specs=[('development','empty-32-32',[128,256]),('development','random-32-32-20',[96,192]),('heldout','room-32-32-4',[96,160]),('heldout','maze-32-32-4',[64,128])]
(ROOT/'data/instances').mkdir(exist_ok=True);(ROOT/'results/baselines').mkdir(exist_ok=True)
records=[]
for split,mapname,counts in specs:
 mp=ROOT/f'data/maps/{mapname}.map';sc=ROOT/f'data/scenarios/{mapname}-random-1.scen';grid=read_map(mp);rows=[line.split() for line in sc.read_text().splitlines()[1:] if line.strip()]
 for n in counts:
  id=f'{mapname}-n{n}';selected=rows[:n];assert len(selected)==n
  ins={'id':id,'split':split,'map':str(mp.relative_to(ROOT)),'map_sha256':hashlib.sha256(mp.read_bytes()).hexdigest(),'scenario':str(sc.relative_to(ROOT)),'scenario_sha256':hashlib.sha256(sc.read_bytes()).hexdigest(),'scenario_rows':list(range(1,n+1)),'starts':[int(r[5])*grid['w']+int(r[4]) for r in selected],'goals':[int(r[7])*grid['w']+int(r[6]) for r in selected],'movement':'four-neighbor + wait; scenario octile-distance column deliberately unused'}
  ip=ROOT/f'data/instances/{id}.json';ip.write_text(json.dumps(ins,indent=2)+'\n');ih=hashlib.sha256(ip.read_bytes()).hexdigest();rec={'id':id,'split':split,'instance':str(ip.relative_to(ROOT)),'runs':{}}
  for secs in [3,6]:
   output=ROOT/f'results/baselines/{id}-{secs}s.txt';cmd=[str(ROOT/'build/upstream/main'),'-m',str(mp),'-i',str(sc),'-N',str(n),'-s','0','-t',str(secs),'-o',str(output)]
   start=time.time()
   try:
    run=subprocess.run(cmd,capture_output=True,text=True,timeout=45);elapsed=time.time()-start
    (ROOT/f'results/baselines/{id}-{secs}s.log').write_text(run.stdout+run.stderr)
    text=output.read_text() if output.exists() else ''
    state_lines=[line for line in text.splitlines() if re.match(r'^\d+:',line)]
    states=[[int(y)*grid['w']+int(x) for x,y in re.findall(r'\((\d+),(\d+)\)',line)] for line in state_lines]
    if run.returncode or not states or any(len(q)!=n for q in states):rec['runs'][str(secs)]={'status':'failed','returncode':run.returncode,'elapsed_seconds':elapsed};continue
    paths=[trim([q[i] for q in states]) for i in range(n)]
    cert={'instance_sha256':ih,'method':'unmodified LaCAM3 defaults','deadline_seconds':secs,'seed':0,'paths':paths,'metrics':metrics(paths)}
    verified=check(ip,cert)
    for key,native in [('soc','soc'),('sol','sum_of_loss'),('makespan','makespan')]:
     val=re.search(rf'^{native}=(\d+)$',text,re.M);assert val and int(val[1])==verified[key],(id,key,val,verified)
    out=ROOT/f'results/baselines/{id}-{secs}s.json';out.write_text(json.dumps(cert)+'\n')
    rec['runs'][str(secs)]={'status':'verified','certificate':str(out.relative_to(ROOT)),'metrics':verified,'elapsed_seconds':elapsed,'command':cmd}
   except subprocess.TimeoutExpired:rec['runs'][str(secs)]={'status':'timeout','wall_limit':45}
  rec['inherited']=next((rec['runs'][str(sec)]['certificate'] for sec in [3,6] if rec['runs'][str(sec)]['status']=='verified'),None)
  records.append(rec);(ROOT/'results/baselines.json').write_text(json.dumps(records,indent=2)+'\n');print(id,{s:r['status'] for s,r in rec['runs'].items()},flush=True)
