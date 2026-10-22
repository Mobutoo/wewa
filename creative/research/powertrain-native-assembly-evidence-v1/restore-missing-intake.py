"""Coordinator-dispatched exact missing-file restoration within user-authorized autonomous motorcycle completion, pinned Git blobs, no staging."""
from pathlib import Path
import subprocess,json,hashlib
R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent;pin='7d93dfa5a248a21343cd9f2ee70f3abc4591c302';base='assets-src/moto-components/';spec={'engine-intake-insulator':['engine-intake-insulator-v2.blend','engine-intake-insulator-v2-inspection.glb','build.py','build_v2.py','parameters.json','parameters-v2.json','build-report-v2.json','README_v2.md','check_interface_v2.py'],'engine-intake-manifold':['engine-intake-manifold-v1.blend','engine-intake-manifold-inspection.glb','build.py','parameters.json','interfaces.json','build-report.json','README.md'],'engine-intake-sleeve':['engine-intake-sleeve-v1.blend','engine-intake-sleeve-inspection.glb','build.py','parameters.json','interfaces.json','build-report.json','README.md'],'engine-intake-clamp-band':['engine-intake-clamp-band-v1.blend','engine-intake-clamp-band-inspection.glb','build.py','parameters.json','interfaces.json','build-report.json','README.md']};rows=[]
for folder,names in spec.items():
 for n in names:
  rel=base+folder+'/'+n;p=R/rel;blob=subprocess.check_output(['git','rev-parse',pin+':'+rel],cwd=R,text=True).strip()
  if p.exists():rows.append(dict(path=rel,action='PRESERVED_EXISTING_NOT_WRITTEN',git_blob=blob));continue
  b=subprocess.check_output(['git','show',pin+':'+rel],cwd=R);actual=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest();assert actual==blob
  p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('xb')as f:f.write(b)
  assert p.read_bytes()==b;rows.append(dict(path=rel,action='RESTORED_EXACT_MISSING_ONLY',git_blob=blob,actual_git_blob_sha1=actual,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b)))
(D/'intake-exact-restoration.json').write_text(json.dumps(dict(schema=1,pinned_commit=pin,authorization='Coordinator dispatch within user-authorized autonomous motorcycle completion',files=rows,geometry_rebuilt=False,existing_overwritten=False,index_or_refs_modified=False),indent=2)+'\n');print(json.dumps(dict(restored=sum(x['action']=='RESTORED_EXACT_MISSING_ONLY' for x in rows),bytes=sum(x.get('bytes',0)for x in rows),pinned_commit=pin)))
