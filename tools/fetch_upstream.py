from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[1];s=json.loads((root/'research/sources.json').read_text())['upstream'];p=root/'vendor/lacam3'
if not (p/'.git').exists():
 subprocess.run(['git','clone',s['url'],str(p)],check=True)
 subprocess.run(['git','checkout','--detach',s['commit']],cwd=p,check=True)
 subprocess.run(['git','submodule','update','--init','--recursive'],cwd=p,check=True)
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=p,text=True).strip()==s['commit'],'Existing upstream revision differs'
assert subprocess.check_output(['git','submodule','status'],cwd=p,text=True).strip()==s['submodules'],'Pinned submodule mismatch'
subprocess.run(['git','diff','--exit-code','HEAD'],cwd=p,check=True)
