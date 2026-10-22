from pathlib import Path
import hashlib, json, sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from model import read_instance
from verify import check
base=json.loads((ROOT/'research/round2/baselines.json').read_text())
trial=json.loads((ROOT/'research/round2/trial.json').read_text())
archive={r['case']:r for r in json.loads((ROOT/'discover/incumbents.json').read_text())}
data=[]
for case in base:
    ip=ROOT/case['instance'];ins=read_instance(ip)
    sources={'Inherited LaCAM3 plan':case['inherited']}
    pibt=[r for r in case['runs'] if r['method']=='pibt-preference' and r['status']=='verified']
    if pibt:sources['PIBT preference · best observed seed']=min(pibt,key=lambda r:r['metrics']['sol'])['certificate']
    for variant in ['random4','proximity4']:
        row=next(r for r in trial['runs'] if r['case']==case['id'] and r.get('variant')==variant and r['seed']==101)
        sources[variant+' · seed 101']=row['certificate']
    sources['Current archive best']=archive[case['id']]['pareto_candidates'][0]['path']
    methods={}
    for label,path in sources.items():
        cert=json.loads((ROOT/path).read_text());check(ip,cert)
        methods[label]={'paths':cert['paths'],'metrics':cert['metrics'],'source':path,
                        'sha256':hashlib.sha256((ROOT/path).read_bytes()).hexdigest()}
    data.append({'id':case['id'],'split':case['split'],'width':ins['grid']['w'],'height':ins['grid']['h'],
                 'rows':ins['grid']['rows'],'goals':ins['goals'],'methods':methods})
template=(ROOT/'visuals/template.html').read_text()
template=template.replace('Selected repair · seed 17','Current archive best')
template=template.replace('Small local improvements were found. The selected repair rule did not beat random repair on the primary cost across held-out maps.',
 'Round two improved the local archive on all 12 cases. Random repair won development selection; no generally superior new method was established.')
template=template.replace('Displayed repair runs use the fixed seed 17.',
 'The two named repair views use seed 101. The archive view shows the best observed primary-cost witness across all recorded runs, not a single-policy result.')
template=template.replace('Discovery@Home · Local pilot','Discovery@Home · Round two')
template=template.replace('/*DATA*/',json.dumps(data,separators=(',',':')))
(ROOT/'visuals/round2.html').write_text(template)
print(json.dumps({'cases':len(data),'views':sum(len(d['methods']) for d in data),'bytes':len(template)}))
