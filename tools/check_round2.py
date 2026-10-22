"""Recheck all native, final, intermediate and inherited round-two witnesses."""
from pathlib import Path
import hashlib, json, sys, time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from verify import check
def main():
    start=time.perf_counter();count=0
    for case in json.loads((ROOT/'research/round2/baselines.json').read_text()):
        for row in case['runs']:
            if row['status']=='verified':
                result=check(ROOT/case['instance'],json.loads((ROOT/row['certificate']).read_text()))
                assert result==row['metrics'];count+=1
    for row in json.loads((ROOT/'research/round2/trial.json').read_text())['runs']:
        if row['status']!='verified':continue
        ip=ROOT/row['instance'];cert=json.loads((ROOT/row['certificate']).read_text())
        checked=check(ip,cert)
        assert all(checked[k]==row['after'][k] for k in ['soc','sol','makespan'])
        assert all(row['after'][k]<=row['before'][k] for k in ['soc','sol','makespan'])
        assert row['budget']['nodes_used']<=row['budget']['node_limit'];count+=1
        trace=json.loads((ROOT/row['trace']).read_text())
        for item in trace['improvements']:
            check(ip,{**cert,'paths':item['paths'],'metrics':item['metrics']});count+=1
    for case in json.loads((ROOT/'discover/incumbents.json').read_text()):
        for row in case['pareto_candidates']:
            source=ROOT/row['path'];assert hashlib.sha256(source.read_bytes()).hexdigest()==row['sha256']
            result=check(ROOT/case['instance'],json.loads(source.read_text()))
            assert all(result[k]==row['metrics'][k] for k in ['soc','sol','makespan'])
    smoke=ROOT/'research/round2-smoke'
    if smoke.exists():
        handoff=json.loads((smoke/'handoff.json').read_text())
        case=next(c for c in json.loads((ROOT/'discover/incumbents.json').read_text()) if c['case']==handoff['case'])
        cert=json.loads((smoke/'candidate.json').read_text());check(ROOT/case['instance'],cert);count+=1
        for item in json.loads((smoke/'trace.json').read_text())['improvements']:
            check(ROOT/case['instance'],{**cert,'paths':item['paths'],'metrics':item['metrics']});count+=1
    print(json.dumps({'passed':True,'round2_certificates':count,'elapsed_seconds':time.perf_counter()-start}))
if __name__=='__main__':main()
