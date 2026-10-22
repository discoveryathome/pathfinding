from pathlib import Path
import json, subprocess
ROOT=Path(__file__).resolve().parents[1]
s=json.loads((ROOT/'research/round2/baseline-source.json').read_text())
p=ROOT/'vendor/pibt-tiebreaking'
if not (p/'.git').exists():
    subprocess.run(['git','clone',s['url'],str(p)],check=True)
    subprocess.run(['git','checkout','--detach',s['commit']],cwd=p,check=True)
    subprocess.run(['git','submodule','update','--init','--recursive'],cwd=p,check=True)
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=p,text=True).strip()==s['commit']
assert subprocess.check_output(['git','submodule','status'],cwd=p,text=True).strip()==s['submodules']
subprocess.run(['git','diff','--exit-code','HEAD'],cwd=p,check=True)
