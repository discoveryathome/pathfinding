from pathlib import Path
import json,hashlib,shutil,subprocess,platform
ROOT=Path(__file__).resolve().parents[1];SIB=ROOT.parent/'computational-geometry';(ROOT/'discover').mkdir(exist_ok=True);(ROOT/'spec').mkdir(exist_ok=True)
for name in ['LICENSE','PARTICIPATION.md']:
 shutil.copyfile(SIB/name,ROOT/name)
for p in (SIB/'spec').iterdir():shutil.copyfile(p,ROOT/'spec'/p.name)
trial=json.loads((ROOT/'results/trial.json').read_text());baselines=json.loads((ROOT/'results/baselines.json').read_text());archive=[]
for case in baselines:
 candidates=[]
 for t,r in case['runs'].items():
  if r['status']=='verified':candidates.append({'source':f'LaCAM3-{t}s','path':r['certificate'],'metrics':{k:r['metrics'][k] for k in ['soc','sol','makespan']}})
 for r in trial['runs']:
  if r['case']==case['id']:candidates.append({'source':f'{r["variant"]}-seed{r["seed"]}','path':r['certificate'],'metrics':{k:r['metrics'][k] for k in ['soc','sol','makespan']}})
 unique={}
 for c in candidates:
  key=tuple(c['metrics'][k] for k in ['sol','soc','makespan'])
  if key not in unique:unique[key]=c
 candidates=list(unique.values());pareto=[]
 for c in candidates:
  m=c['metrics']
  if not any(all(d['metrics'][k]<=m[k] for k in m) and any(d['metrics'][k]<m[k] for k in m) for d in candidates):
   c['sha256']=hashlib.sha256((ROOT/c['path']).read_bytes()).hexdigest();pareto.append(c)
 archive.append({'instance':case['instance'],'case':case['id'],'status':'author-checked local candidates; not literature records or scientific acceptance','pareto_candidates':sorted(pareto,key=lambda c:(c['metrics']['sol'],c['metrics']['soc'],c['metrics']['makespan']))})
(ROOT/'discover/incumbents.json').write_text(json.dumps(archive,indent=2)+'\n')
summary={}
for split in ['development','heldout']:
 summary[split]={}
 for v in ['random4',trial['selected']]:
  rr=[r for r in trial['runs'] if r['split']==split and r['variant']==v]
  summary[split][v]={'runs':len(rr),'initial':{k:sum(r['initial_metrics'][k] for r in rr) for k in ['soc','sol']},'final':{k:sum(r['metrics'][k] for r in rr) for k in ['soc','sol']},'runs_with_improvement':sum(r['accepted_repairs']>0 for r in rr),'nodes_used':sum(r['budget']['nodes_used'] for r in rr)}
(ROOT/'results/summary.json').write_text(json.dumps({'paired_totals':summary,'selected':trial['selected'],'trials':len(trial['runs']),'all_certificates_valid':True,'deterministic_replay':trial['deterministic_replay'],'global_optimality_claimed':False,'heldout_primary_advantage':False},indent=2)+'\n')
(ROOT/'research/environment.json').write_text(json.dumps({'platform':platform.platform(),'python':platform.python_version(),'compiler':subprocess.check_output(['clang','--version'],text=True).strip(),'load':subprocess.check_output(['uptime'],text=True).strip(),'trial_kind':'fixed search-state budget; no timing superiority claim','dependencies':subprocess.check_output(['uv','pip','freeze','--python',str(ROOT/'.venv/bin/python')],text=True).splitlines()},indent=2)+'\n')
(ROOT/'.gitignore').write_text('.venv/\n/vendor/\n/build/\n__pycache__/\n.pytest_cache/\n*.pyc\n.DS_Store\n')
(ROOT/'requirements.txt').write_text('cmake==4.4.4\npytest==9.1.1\njsonschema==4.26.0\n')
(ROOT/'requirements-visual.txt').write_text('playwright=='+__import__('importlib.metadata').metadata.version('playwright')+'\n')
(ROOT/'research/review.json').write_text(json.dumps({'status':'pending','scientific_owner':None,'independent_review':False,'human_signoff':False,'scope':'collision/cost semantics, competitive baseline and useful workloads, transfer, review of open local candidate archive','reviewed_commit':None,'findings':[]},indent=2)+'\n')
manifest={'schema':'discover/v0','title':'Multi-agent pathfinding — local pilot','summary':'Improve collision-free grid plans under bounded search budgets. Local trials and expert-agent reviews are open.','domains':['algorithms','multi-agent planning','combinatorial optimization'],'license':'MIT','maintainers':[{'name':'Douglas Colkitt','github':'Mister-Meeseeks'}],'canonical_repo':ROOT.as_uri(),'entry':{'agents':'AGENTS.md','project':'DISCOVERY.md','brief':'research/ASSESSMENT.md'},'frontier':'discover/frontier.json','catalog':'discover/catalog.json','priority_log':'discover/priority-log.md','ledger':'discover/ledger.jsonl','packages':'research/*/','session':{'default_minutes':30,'orient_fraction':0.2,'verify_fraction':0.3},'permissions':{'post_messages':False,'open_prs':False,'maintainer_only':['accept-results','publish','change-frontier']},'verification_profile':'exact-certificate','hubs':[],'credit':{'policy':'Credit original solvers, methods, Moving AI benchmarks and substantive contributors. Disclose agent assistance; preserve source/data notices.'},'review':{'paused':False,'note':'Open for local trials and expert-agent reviews. Scientific acceptance pending; no remote exists.'},'picker':{'command':['python','tools/pick.py','--seed','{seed}']}}
(ROOT/'discover.json').write_text(json.dumps(manifest,indent=2)+'\n')
tracks=[]
spec=[('repair',35,'Can a bounded repair improve an inherited Pareto candidate without worsening another recorded metric?','Start from discover/incumbents.json, not the old 3-second plan. Propose one new neighborhood rule and freeze new evaluation cases before selection.'),('verification',25,'Can a minimized input expose a collision or cost-accounting error?','Audit goal revisits, future goal occupancy, edge swaps, map identity and independent lower bounds; retain a failing certificate.'),('workloads',25,'Does the chosen method transfer to a useful workload or a larger problem?','Source new maps/scenarios or dynamic tasks with provenance; compare against MAPF-LNS2 and newer PIBT preference methods.'),('expert-review',15,'Is there useful research headroom beyond known neighborhood repair?','Review the exact source/instance hashes and literature; distinguish verified route improvements from algorithm novelty and robot applicability.')]
for name,weight,question,exp in spec:
 tracks.append({'id':name,'weight':weight,'tasks':[{'id':name,'question':question,'starting_points':['research/ASSESSMENT.md','discover/incumbents.json','research/PROTOCOL.md'],'methods':['bounded experiment','independent certificate check','scoped review'],'acceptance_gate':'Correct input binding and all route checks; report SOC, SOL, makespan, failure rates, budget and all attempts. Scientific acceptance remains separate.','first_step':{'command':['python','tools/check.py','--quick'],'expected':'Pinned artifacts and schemas pass; intake open.'},'bottleneck_link':'research/ASSESSMENT.md','first_experiment':exp,'scope_change_triggers':['Stop at 30 minutes and hand off with all failures; request a separate larger experiment if required.']} ]})
(ROOT/'discover/catalog.json').write_text(json.dumps({'schema':'discover-catalog/v0','priority_revision':1,'assessed_on':'2026-10-22','status':'Open for local contributions and expert-agent review','tracks':tracks},indent=2)+'\n')
(ROOT/'discover/priority-log.md').write_text('# Initial priorities\n\n2026-10-22: Known-method bounded repair trial complete. Selected proximity-four failed held-out primary superiority; do not treat it as a universal policy. Inherit the nondominated local witness archive and use new unseen instances for future transfer tests.\n')
(ROOT/'discover/ledger.jsonl').write_text(json.dumps({'date':'2026-10-22','kind':'author-run trial','runs':56,'status':'author-checked','independent_review':False,'accepted_algorithmic_improvement':False,'package':'results/trial.json'})+'\n')
artifacts=['results/trial.json','results/summary.json','discover/incumbents.json','research/PROTOCOL.md']
frontier={'schema':'discover-frontier/v0','statement':'Eight benchmark instances have independently implemented feasibility/cost checks for LaCAM3 witnesses and 56 bounded repair runs. Local route gains exist; selected policy failed held-out primary superiority.','status':'Author-checked local candidate archive; local intake open; scientific acceptance pending.','evidence_level':['author-checked'],'scope':'Four-neighbor discrete point agents on 32x32 benchmark grids, 64–256 agents, static goals, fixed recorded search allowances; no novelty, optimality or physical robot claims.','review':'research/review.json','updated_on':'2026-10-22','artifacts':[{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in artifacts],'reproduce':'python tools/check.py','reproduce_full':'python tools/prepare.py; python tools/run_trial.py (in a copy; native deadline runs may differ)','assumptions':[{'id':'baseline','statement':'LaCAM3 and local random-neighborhood repair are substantive baselines but are not an exhaustive current-state-of-the-art comparison.','status':'open'},{'id':'transfer','statement':'Selected proximity heuristic did not improve the primary held-out aggregate; fresh validation needed.','status':'open'}]}
(ROOT/'discover/frontier.json').write_text(json.dumps(frontier,indent=2)+'\n')
