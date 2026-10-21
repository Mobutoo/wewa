"""Explicit A-owned input/proof allowlists; never adopt ROOT engine artifacts."""
from pathlib import Path
import json,hashlib,sys
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/swingarm-pivot-bush-v1';D=R/'creative/research/swingarm-pivot-bush';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=lambda files:[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(files)]
hn=['README.md','requirements.txt','provenance.json','parameters.json','build.py','check_export.mjs','check_material_preservation.mjs','inspect_interfaces.py','inspect_material.py','material.py','render.py','record.py','build-report.json','swingarm-pivot-bush-v1.blend','swingarm-pivot-bush-inspection.glb','g3-master-v1/README.md','g3-master-v1/swingarm-pivot-bush-v1.blend','g3-master-v1/swingarm-pivot-bush-inspection.glb','g3-master-v1/source-geometry-check.json','g3-master-v1/geometry-check.json']
for n in ['outer-clear','inner-clear','dark-annulus']:
 for role in ['normal','metallic-roughness']:hn.append('textures/pivot-bush-'+n+'-'+role+'.png')
inputs=[H/n for n in hn]+[D/'preparation-v1.json',D/'material-plan-v1.json'];s=sha(H/'swingarm-pivot-bush-v1.blend');g=sha(H/'swingarm-pivot-bush-inspection.glb');a=json.loads((O/'source-geometry-check.json').read_text());b=json.loads((O/'geometry-check.json').read_text());assert a['source_sha256']==b['source_sha256']==s and a['export_sha256']==b['export_sha256']==g and b['technical_passed'];assert len(set(inputs))==len(inputs)
if '--freeze'in sys.argv:
 assert not(O/'source-freeze.json').exists(),'Existing source freeze must not be replaced'
 r={'component_id':'MOTO-SWINGARM-PIVOT-BUSH-001','revision':'swingarm-pivot-bush-v1','source_sha256':s,'export_sha256':g,'scope':'Explicit original source input allowlist; G3 baseline and preparation included. No private reference pixels or ROOT engine proofs.','files':rows(inputs),'art_accepted':False};(O/'source-freeze.json').write_text(json.dumps(r,indent=2)+'\n');print('PIVOT_BUSH_FROZEN',len(inputs),s,g);raise SystemExit
assert json.loads((O/'source-freeze.json').read_text())['files']==rows(inputs),'Frozen input changed'
r=json.loads((O/'render-report.json').read_text());v=json.loads((O/'source-render-review.json').read_text());names={'quarter','front','lip-detail'};assert r['source_sha256']==v['source_sha256']==s and r['export_sha256']==v['export_sha256']==g and r['samples']==96 and{x['name']for x in r['views']}==set(v['images_actually_read'])==names
for n in names:
 p=O/(n+'.png');q=json.loads((O/('checkpoint-'+n+'.json')).read_text());assert q['source_sha256']==s and q['export_sha256']==g and q['PNG_sha256']==sha(p)and q['view']['camera_preflight']['technical_preflight_passed']
 with Image.open(p)as im:assert im.size==(1000,900)
on=['README.md','source-freeze.json','source-geometry-check.json','geometry-check.json','source-interface-check.json','gray-review.json','material-build-report.json','material-preservation-check.json','material-buffer-check.json','material-preview-review.json','conditional-interface-limits.json','render-report.json','source-render-review.json']
for n in ['gray-quarter','gray-front','reflection-lip-detail','preview-quarter','preview-lip-detail']:
 for e in ['png','json']:on.append(n+'.'+e)
for n in names:on.extend([n+'.png','checkpoint-'+n+'.json'])
files=inputs+[O/n for n in on];assert len(set(files))==len(files);m={'component_id':'MOTO-SWINGARM-PIVOT-BUSH-001','revision':'swingarm-pivot-bush-v1','source_sha256':s,'export_sha256':g,'scope':'One DP171006-related visible bushing unit, three separately closed envelopes and true throughbore. All metrics and reverse continuation estimated. No extra count for internal sleeves; no body, shaft, nut or instancing.','proof_ownership':'Explicit A-owned source and proof allowlists only; ROOT engine checks remain independently attributed.','files':rows(files),'all_metric_parameters_estimated':True,'current_RDC_identity_verified':False,'body_and_shaft_fit_verified':False,'bonding_or_stiffness_qualified':False,'mobile_LOD_qualified':False,'physical_iphone_tested':False,'art_accepted':False};(O/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('PIVOT_BUSH_SEALED',len(files),sha(O/'manifest.json'))
