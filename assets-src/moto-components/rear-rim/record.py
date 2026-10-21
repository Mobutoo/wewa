"""Seal the explicit A-authored proof allowlist after actual final-image review."""
from pathlib import Path
import json,hashlib
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/rear-rim-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=sha(H/'rear-rim-v1.blend');g=sha(H/'rear-rim-inspection.glb');a=json.loads((O/'source-geometry-check.json').read_text());b=json.loads((O/'geometry-check.json').read_text());r=json.loads((O/'render-report.json').read_text());v=json.loads((O/'source-render-review.json').read_text());names={'quarter','reverse','spoke-root-detail','rim-channel-detail'}
assert a['source_sha256']==b['source_sha256']==r['source_sha256']==v['source_sha256']==s and a['export_sha256']==b['sha256']==r['export_sha256']==v['export_sha256']==g and b['technical_passed']
assert r['samples']==96 and {x['name'] for x in r['views']}==set(v['images_actually_read'])==names
for name in names:
 p=O/(name+'.png');q=json.loads((O/('checkpoint-'+name+'.json')).read_text());assert q['source_sha256']==s and q['export_sha256']==g and q['PNG_sha256']==sha(p) and q['view']['camera_preflight']['technical_preflight_passed']
 with Image.open(p)as im:assert im.size==(1200,1100)
hnames=['README.md','build.py','parameters.json','rear-rim-v1.blend','rear-rim-inspection.glb','build-report.json','render.py','check_export.mjs','material.py','check_material_preservation.mjs','inspect_material.py','provenance.json','record.py','textures/rear-rim-original-normal.png','textures/rear-rim-original-metallic-roughness.png']
onames=['README.md','source-geometry-check.json','geometry-check.json','source-freeze.json','gray-review.json','material-build-report.json','material-preservation-check.json','material-buffer-check.json','material-preview-review.json','conditional-interface-limits.json','render-report.json','source-render-review.json']
for name in ['quarter','reverse','side-proportions','reflection-spoke-root-detail','reflection-rim-channel-detail']:
 for ext in ['png','json']:onames.append('gray-'+name+'.'+ext)
for name in ['quarter','spoke-root-detail']:
 for ext in ['png','json']:onames.append('preview-'+name+'.'+ext)
for name in names:onames.extend([name+'.png','checkpoint-'+name+'.json'])
files=[H/n for n in hnames]+[O/n for n in onames]+[R/'creative/research/rear-wheel-16'/n for n in ['reference-search-v1.json','README.md','rim-preparation-v1.json','rim-material-plan-v1.json']]
assert len(files)==len(set(files))
m={'component_id':a['component_id'],'revision':a['revision'],'source_sha256':s,'export_sha256':g,'scope':'Outer rim, five observed branches and partial annular outer hub envelope. No hidden centre web or functional hub, tyre, carrier or axial stack.','proof_ownership':'Explicit allowlist of A-authored sources/proofs only. Parent runtime reports/captures excluded, not recursively collected.','files':[{'path':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size}for p in sorted(files)],'all_physical_profiles_estimated':True,'current_RDC_mould_identity_verified':False,'complete_hub_modelled':False,'assembly_verified':False,'art_accepted':False,'physical_iphone_tested':False};(O/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('WEWA_REAR_RIM_SEALED',len(files),sha(O/'manifest.json'))
