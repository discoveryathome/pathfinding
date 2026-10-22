"""Acquire fresh cases and retain native baseline witnesses; never overwrite."""
from pathlib import Path
import hashlib, io, json, re, subprocess, sys, time, urllib.request, zipfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from model import read_map, trim, metrics
from verify import check
DEST = ROOT/'research/round2'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, x): p.write_text(json.dumps(x, indent=2)+'\n')

def main():
    if (DEST/'baselines.json').exists():
        raise SystemExit('Round already exists; replay in a copy with a fresh output package')
    rawdir = DEST/'native'
    rawdir.mkdir(exist_ok=True)
    datadir = ROOT/'data/round2'
    datadir.mkdir(exist_ok=True)
    specs = [('empty-32-32',256), ('random-32-32-20',192), ('room-32-32-4',160),
             ('maze-32-32-4',128), ('empty-48-48',256), ('random-64-64-20',192)]
    sources = []
    for filename in ['mapf-map.zip','mapf-scen-random.zip']:
        url = 'https://movingai.com/benchmarks/mapf/'+filename
        raw = urllib.request.urlopen(url, timeout=120).read()
        archive = zipfile.ZipFile(io.BytesIO(raw))
        record = {'url':url, 'sha256':hashlib.sha256(raw).hexdigest(), 'members':[]}
        for name,_ in specs:
            members = [name+'.map'] if filename=='mapf-map.zip' else [f'scen-random/{name}-random-{s}.scen' for s in [2,3]]
            for member in members:
                p = datadir/Path(member).name
                p.write_bytes(archive.read(member))
                record['members'].append({'member':member,'path':str(p.relative_to(ROOT)),'sha256':sha(p)})
        sources.append(record)
        print('Downloaded', filename, flush=True)
    save(DEST/'data-sources.json', sources)
    cases = []
    for name,n in specs:
        for scen in [2,3]:
            mp, sp = datadir/(name+'.map'), datadir/f'{name}-random-{scen}.scen'
            grid = read_map(mp)
            rows = [line.split() for line in sp.read_text().splitlines()[1:] if line.strip()][:n]
            assert len(rows)==n
            cid = f'{name}-s{scen}-n{n}'
            split = 'development' if scen==2 and name in [s[0] for s in specs[:3]] else 'heldout'
            ins = {'id':cid,'split':split,'map':str(mp.relative_to(ROOT)),'map_sha256':sha(mp),
                   'scenario':str(sp.relative_to(ROOT)), 'scenario_sha256':sha(sp),
                   'scenario_rows':list(range(1,n+1)),
                   'starts':[int(r[5])*grid['w']+int(r[4]) for r in rows],
                   'goals':[int(r[7])*grid['w']+int(r[6]) for r in rows],
                   'movement':'four-neighbor + wait; scenario octile column unused'}
            ip = datadir/(cid+'.json')
            save(ip, ins)
            case = {'id':cid,'split':split,'instance':str(ip.relative_to(ROOT)),'runs':[]}
            configs = [('lacam3',6,0),('lacam3',12,0)]+[('pibt-preference',6,s) for s in [0,1,2]]
            for method,secs,seed in configs:
                stem = f'{cid}-{method}-{secs}s-seed{seed}'
                output = rawdir/(stem+'.txt')
                binary = 'build/upstream/main' if method=='lacam3' else 'build/pibt/main'
                cmd = [str(ROOT/binary),'-m',str(mp),'-i',str(sp),'-N',str(n),'-s',str(seed),'-t',str(secs),'-o',str(output),'-v','0']
                row = {'method':method,'deadline_seconds':secs,'seed':seed,'command':cmd}
                start = time.perf_counter()
                try:
                    result = subprocess.run(cmd,capture_output=True,text=True,timeout=45)
                    (rawdir/(stem+'.log')).write_text(result.stdout+result.stderr)
                    text = output.read_text() if output.exists() else ''
                    states = [[int(y)*grid['w']+int(x) for x,y in re.findall(r'\((\d+),(\d+)\)',line)]
                              for line in text.splitlines() if re.match(r'^\d+:',line)]
                    if result.returncode or not states or any(len(q)!=n for q in states):
                        row.update(status='failed',returncode=result.returncode)
                    else:
                        paths = [trim([q[i] for q in states]) for i in range(n)]
                        cert = {'instance_sha256':sha(ip),'paths':paths,'metrics':metrics(paths),'method':method,'seed':seed}
                        verified = check(ip,cert)
                        for key,field in [('soc','soc'),('sol','sum_of_loss'),('makespan','makespan')]:
                            val = re.search(rf'^{field}=(\d+)$',text,re.M)
                            assert val and int(val[1])==verified[key],(cid,key,verified)
                        cp = rawdir/(stem+'.json')
                        cp.write_text(json.dumps(cert)+'\n')
                        row.update(status='verified',certificate=str(cp.relative_to(ROOT)),metrics=verified)
                except subprocess.TimeoutExpired:
                    row['status']='timeout'
                row['elapsed_seconds']=time.perf_counter()-start
                case['runs'].append(row)
            feasible = [r for r in case['runs'] if r['status']=='verified']
            case['inherited'] = min(feasible,key=lambda r:tuple(r['metrics'][k] for k in ['sol','soc','makespan']))['certificate'] if feasible else None
            cases.append(case)
            save(DEST/'baselines-progress.json', cases)
            print(cid, [(r['method'],r['status'],r.get('metrics',{}).get('sol')) for r in case['runs']],flush=True)
    save(DEST/'baselines.json',cases)
    source = {'url':'https://github.com/HirokiNagai-39/pibt-tiebreaking',
              'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT/'vendor/pibt-tiebreaking',text=True).strip(),
              'submodules':subprocess.check_output(['git','submodule','status'],cwd=ROOT/'vendor/pibt-tiebreaking',text=True).strip(),
              'license':'MIT','configuration':'one-shot defaults; hindrance and regret preference enabled'}
    save(DEST/'baseline-source.json', source)
if __name__=='__main__': main()
