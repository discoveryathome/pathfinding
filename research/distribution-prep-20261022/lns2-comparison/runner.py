"""Optional pinned LNS2 context comparison; internal objectives differ explicitly."""
from pathlib import Path
import argparse,hashlib,json,os,random,re,resource,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from model import read_instance,metrics,trim
from verify import check

def run(out):
    out=(ROOT/out).resolve()
    if out.exists() or not out.is_relative_to(ROOT/'research'):raise ValueError('Use a new research directory')
    pin=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT/'vendor/mapf-lns2',text=True).strip()
    assert pin=='1369823985a15944f9a339226d521f61605a6d17'
    out.mkdir(parents=True);rng=random.Random(221042);rows=[]
    cases=[sorted((ROOT/'data/round2').glob(prefix+'*-n*.json'))[0] for prefix in ['empty-','room-','maze-']]
    for ip in cases:
        ins=read_instance(ip);n=len(ins['starts']);w=ins['grid']['w']
        for seed in [419,503]:
            methods=['lns2','lacam3'];rng.shuffle(methods)
            for method in methods:
                stem=f'{ip.stem}-{seed}-{method}';raw=out/(stem+'.txt')
                if method=='lns2':
                    cmd=[str(ROOT/'build/lns2/lns'),'-m',str(ROOT/ins['map']),'-a',str(ROOT/ins['scenario']),
                         '-k',str(n),'-t','6','--seed',str(seed),'--outputPaths',str(raw),'-o',str(out/stem)]
                else:
                    cmd=[str(ROOT/'build/upstream/main'),'-m',str(ROOT/ins['map']),'-i',str(ROOT/ins['scenario']),
                         '-N',str(n),'-t','6','-s',str(seed),'-o',str(raw),'-v','0']
                t=time.perf_counter();usage=resource.getrusage(resource.RUSAGE_CHILDREN)
                row={'case':ip.stem,'instance':str(ip.relative_to(ROOT)),'method':method,'seed':seed,'command':cmd,
                     'requested_seconds':6,'internal_objective':'SOC' if method=='lns2' else 'SOL'}
                try:
                    result=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
                    (out/(stem+'.log')).write_text(result.stdout+result.stderr)
                    if result.returncode:raise ValueError('solver exit '+str(result.returncode))
                    text=raw.read_text()
                    if method=='lns2':
                        lines=[line for line in text.splitlines() if line.startswith('Agent ')]
                        assert [int(re.match(r'Agent (\d+):',line)[1]) for line in lines]==list(range(n))
                        paths=[trim([int(y)*w+int(x) for y,x in re.findall(r'\((\d+),(\d+)\)',line)]) for line in lines]
                    else:
                        states=[[int(y)*w+int(x) for x,y in re.findall(r'\((\d+),(\d+)\)',line)]
                                for line in text.splitlines() if re.match(r'^\d+:',line)]
                        assert states and all(len(s)==n for s in states)
                        paths=[trim([s[i] for s in states]) for i in range(n)]
                    cert={'instance_sha256':hashlib.sha256(ip.read_bytes()).hexdigest(),'paths':paths,
                          'metrics':metrics(paths),'method':method,'seed':seed}
                    verified=check(ip,cert);cp=out/(stem+'.json');cp.write_text(json.dumps(cert)+'\n')
                    row.update(status='verified',metrics=verified,certificate=str(cp.relative_to(ROOT)))
                except (subprocess.TimeoutExpired,ValueError,AssertionError,OSError) as e:
                    row.update(status='failed',error=str(e))
                after=resource.getrusage(resource.RUSAGE_CHILDREN)
                row.update(elapsed_seconds=time.perf_counter()-t,child_cpu_seconds=after.ru_utime+after.ru_stime-usage.ru_utime-usage.ru_stime)
                rows.append(row);print(ip.stem,seed,method,row['status'],flush=True)
                report={'kind':'exposed author-run baseline context','lns2_commit':pin,'matched_internal_objective':False,
                        'load_average':os.getloadavg(),'rows':rows,'claim':'Common verified metrics, not a matched-objective or equal-CPU ranking.'}
                (out/'results.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
