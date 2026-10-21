"""Stage exact completed review manifests and shared metadata, verify index bytes, commit and push.
No artistic receipt or package completion is inferred. Run only after other Git writers finish.
"""
import argparse,json,hashlib,subprocess,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('reviews',nargs='+');p.add_argument('--message',required=True);a=p.parse_args();sha=lambda b:hashlib.sha256(b).hexdigest();paths=set();rows=[]
for rev in a.reviews:
 m=R/'creative/reviews'/rev/'production-manifest.json';d=json.loads(m.read_text());rows+=d['files'];paths.add(str(m.relative_to(R)));paths.add('WEWA_Developpement_Web/validation/'+rev+'.json');paths.add('creative/workflow/records/'+d['component_id'].lower()+'.json')
 for f in d['files']:
  q=R/f['path'];assert q.is_file()and sha(q.read_bytes())==f['sha256']and q.stat().st_size==f['bytes'],('Working manifest mismatch',f['path']);paths.add(f['path'])
paths.update(['LIVRAISONS_MOTO.md','WEWA_Developpement_Web/validation/STATUS.json','creative/library/component-production.json','creative/workflow/coverage.json','creative/workflow/motorcycle-execution-18.json','creative/workflow/motorcycle-exterior-completion-v1.json','tools/motorcycle-lab/catalog.json','tools/save_exterior_delivery_v1.py'])
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=R).strip(),'Other staged work exists'
subprocess.run(['git','add','--sparse','--',*sorted(paths)],cwd=R,check=True)
for f in rows:
 b=subprocess.check_output(['git','show',':'+f['path']],cwd=R);assert len(b)==f['bytes']and sha(b)==f['sha256'],('Index mismatch',f['path'])
changed=subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=R).decode().split('\0')
for s in changed:
 if not s:continue
 b=subprocess.check_output(['git','show',':'+s],cwd=R);assert len(b)<100*1024**2,('GitHub file limit',s)
 if s.endswith('.json'):json.loads(b)
indexed=set(subprocess.check_output(['git','ls-files','-z'],cwd=R).decode().split('\0'));catalog=json.loads(subprocess.check_output(['git','show',':tools/motorcycle-lab/catalog.json'],cwd=R))
for key,c in catalog['assets'].items():
 for s in [c['source'],*c['files']]:assert 'assets-src/moto-components/'+s in indexed,('Catalog source not indexed',key,s)
subprocess.run(['git','diff','--cached','--check'],cwd=R,check=True);subprocess.run(['git','commit','-m',a.message],cwd=R,check=True,stdout=subprocess.DEVNULL);env=dict(os.environ,GIT_NO_LAZY_FETCH='1',GIT_TERMINAL_PROMPT='0');subprocess.run(['git','-c','pack.window=0','push','origin','HEAD:main'],cwd=R,env=env,check=True);print('PUSHED',subprocess.check_output(['git','rev-parse','--short','HEAD'],cwd=R,text=True).strip(),a.reviews)
