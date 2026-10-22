"""Create a shareable source archive and full-history Git bundle from a clean commit."""
from pathlib import Path
import argparse, hashlib, json, subprocess
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args()
out=Path(a.out).resolve()
if out.is_relative_to(ROOT):raise SystemExit('Use an output directory outside the project')
if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True):raise SystemExit('Commit the reviewed package before release')
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
out.mkdir(parents=True,exist_ok=True);name=ROOT.name+'-'+commit[:12]
archive=out/(name+'.tar.gz');bundle=out/(name+'.bundle')
if archive.exists() or bundle.exists():raise SystemExit('Release files already exist; choose a new output directory')
subprocess.run(['git','archive','--format=tar.gz','--prefix='+ROOT.name+'/', '-o',str(archive),commit],cwd=ROOT,check=True)
subprocess.run(['git','bundle','create',str(bundle),'--all'],cwd=ROOT,check=True)
subprocess.run(['git','bundle','verify',str(bundle)],cwd=ROOT,check=True,capture_output=True)
receipt={'project':ROOT.name,'commit':commit,'stage':'pre-release contributor/expert review','canonical_repo':json.loads((ROOT/'discover.json').read_text())['canonical_repo'],
         'intake':'open','independent_review':'pending','artifacts':[]}
for file in [archive,bundle]:receipt['artifacts'].append({'file':file.name,'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
(out/(name+'-receipt.json')).write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
