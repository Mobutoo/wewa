"""Resolve exact closed component inputs; no generation or geometry edit."""
from pathlib import Path
import json,hashlib,datetime
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/rear-sns-rest-assembly-v3';O.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
diagnostic=json.loads((R/'creative/reviews/rear-sns-rest-assembly-v1/diagnostic-freeze-manifest.json').read_text())
for proof in diagnostic['files']:assert sha(R/proof['path'])==proof['sha256']
base=json.loads((R/'creative/reviews/rear-sns-rest-assembly-v1/exact-inputs-v1.json').read_text());rows=[]
for q in base['inputs']:
 f=json.loads((R/q['closed_manifest']).read_text());assert sha(R/q['closed_manifest'])==q['closed_manifest_sha256']
 for a in f['files']:assert sha(R/a['path'])==a['sha256']
 rows.append(q)
for u in ['opposite-end-closure','body-end-closure']:
 d=R/('creative/reviews/rear-sns-'+u+'-v1');b=json.loads((d/'build-report.json').read_text());fm=d/'source-freeze-manifest.json';f=json.loads(fm.read_text())
 for a in f['files']:assert sha(R/a['path'])==a['sha256']
 source=R/('assets-src/moto-components/rear-sns/'+u+'/rear-sns-'+u+'-v1.blend');glb=source.with_suffix('.glb');assert sha(source)==b['source_sha256'] and sha(glb)==b['export_sha256']
 rows.append({'unit':u,'source':str(source.relative_to(R)),'GLB':str(glb.relative_to(R)),'source_sha256':b['source_sha256'],'GLB_sha256':b['export_sha256'],'collection':b['collection'],'root':b['root'],'closed_manifest':str(fm.relative_to(R)),'closed_manifest_sha256':sha(fm),'closed_files_verified':len(f['files']),'material_status':'Original black source frozen, final96 proof separate; no finish approval'})
j={'schema':1,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Composite exact-source rest review, not a new physical component','inputs':rows,'geometry_transforms':'None; exact shared unplaced source frame','material_override':'None: actual fourteen original source material proposals, no edits','art_accepted':False}
(O/'exact-inputs-v3.json').write_text(json.dumps(j,indent=2)+'\n');print('VERIFIED_CLOSED_INPUTS',len(rows))
