"""Resolve exact closed component inputs; no generation or geometry edit."""
from pathlib import Path
import json,hashlib,datetime
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/rear-sns-rest-assembly-v1';O.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=json.loads((R/'creative/research/rear-sns-rest-assembly/G0-G2-rest-review-plan-v1.json').read_text());rows=[]
for old in p['inputs']:
 u=old['unit'];rev='v2' if u=='damper-body' else 'v1';d=R/('creative/reviews/rear-sns-'+u+'-'+rev);b=json.loads((d/'build-report.json').read_text());fm=d/'freeze-manifest.json';f=json.loads(fm.read_text())
 for a in f['files']:
  q=R/a['path'];assert sha(q)==a['sha256'],str(q)
 source=R/old['source'];glb=R/old['GLB'];assert sha(source)==b['source_sha256'] and sha(glb)==b['export_sha256'];assert f['source_sha256']==b['source_sha256']
 rows.append({'unit':u,'source':old['source'],'GLB':old['GLB'],'source_sha256':b['source_sha256'],'GLB_sha256':b['export_sha256'],'collection':b['collection'],'root':b['root'],'closed_manifest':str(fm.relative_to(R)),'closed_manifest_sha256':sha(fm),'closed_files_verified':len(f['files'])})
j={'schema':1,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Composite exact-source rest review, not a new physical component','inputs':rows,'geometry_transforms':'None; exact shared unplaced source frame','material_override':'Only scene override for first gray review; linked material data untouched','art_accepted':False}
(O/'exact-inputs-v1.json').write_text(json.dumps(j,indent=2)+'\n');print('VERIFIED_CLOSED_INPUTS',len(rows))
