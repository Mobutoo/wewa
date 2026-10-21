"""Explicit A author inputs/proofs; attributed documentary addendum, no ROOT proofs."""
from pathlib import Path
import json,hashlib,sys
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-protection-terminal-a-v1';D=R/'creative/research/engine-protection-terminal-A-15';S=R/'creative/research/crash-guard-15-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=lambda ps:[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(set(ps))]
hn=['README.md','requirements.txt','provenance.json','parameters.json','profile_shape.py','build.py','build-report.json','probes.json','check_export.mjs','inspect_interfaces.py','inspect_self.py','camera_preflight.py','material.py','check_material_preservation.mjs','inspect_material.py','render.py','record.py','diagnostics/render-initial-gray.py','diagnostics/material-before-relative-remap.py','engine-protection-terminal-a-v1.blend','engine-protection-terminal-a-inspection.glb','textures/engine-protection-terminal-a-original-normal.png','textures/engine-protection-terminal-a-original-metallic-roughness.png']
hn+=['g3-master-v1/'+n for n in ['README.md','engine-protection-terminal-a-v1.blend','engine-protection-terminal-a-inspection.glb','source-geometry-check.json','geometry-check.json','source-interface-check.json','self-surface-check.json']]
dn=['README.md','initial-observations.json','working-study-v1.json','chosen-parameters-before-geometry-v1.json','material-plan-v1.json','relative-image-path-diagnostic-v1.json']
inputs=[H/n for n in hn]+[D/n for n in dn]+[S/n for n in ['README.md','report.json','terminal-small-dark-point-v1/README.md','terminal-small-dark-point-v1/report.json']]+[O/n for n in ['gray-review.json','source-geometry-check.json','geometry-check.json','source-interface-check.json','self-surface-check.json','material-preservation-check.json','material-preview-review.json']]
s=sha(H/'engine-protection-terminal-a-v1.blend');g=sha(H/'engine-protection-terminal-a-inspection.glb')
for name in ['source-geometry-check','geometry-check','source-interface-check','self-surface-check','material-preview-review']:
 q=json.loads((O/(name+'.json')).read_text());assert q['source_sha256']==s and q['export_sha256']==g,name
assert json.loads((O/'geometry-check.json').read_text())['technical_passed']
assert json.loads((O/'material-preview-review.json').read_text())['ready_for_final_candidate_views']
if '--freeze'in sys.argv:
 assert not(O/'source-freeze.json').exists(),'Do not replace a freeze'
 r={'component_id':'MOTO-ENGINE-PROTECTION-TERMINAL-A-001','revision':'engine-protection-terminal-a-v1','source_sha256':s,'export_sha256':g,'scope':'First photographed terminal-A twohole formed sheet only. Explicit author inputs + separately attributed documentary source. No private sourcephoto pixels or ROOT independent QA.','files':rows(inputs),'complete_guard_assembly':False,'all_metric_parameters_estimated':True,'art_accepted':False};(O/'source-freeze.json').write_text(json.dumps(r,indent=2)+'\n');print('TERMINAL_A_FROZEN',len(r['files']),s,g);raise SystemExit
assert json.loads((O/'source-freeze.json').read_text())['files']==rows(inputs),'Frozen input changed'
names={'quarter','reverse-quarter','doublebend-detail','upper-bore-detail','lower-bore-detail'};r=json.loads((O/'render-report.json').read_text());v=json.loads((O/'source-render-review.json').read_text());assert r['source_sha256']==v['source_sha256']==s and r['export_sha256']==v['export_sha256']==g and r['samples']==96 and{x['name']for x in r['views']}==set(v['images_actually_read'])==names
proof=['README.md','source-freeze.json','gray-initial-reading.json','material-build-report.json','material-buffer-check.json','conditional-interface-limits.json','render-report.json','source-render-review.json']
for prefix,nn in [('gray-',['quarter','front','profile','doublebend-detail']),('reflection-',['quarter','doublebend-detail','upper-bore-detail','lower-bore-detail']),('preview-',['quarter','reverse-quarter','doublebend-detail','lower-bore-detail'])]:
 for n in nn:
  for ext in ['png','json']:proof.append(prefix+n+'.'+ext)
for n in names:
 p=O/(n+'.png');cp=O/('checkpoint-'+n+'.json');q=json.loads(cp.read_text());assert q['source_sha256']==s and q['export_sha256']==g and q['PNG_sha256']==sha(p)and q['view']['camera_preflight']['technical_preflight_passed']
 with Image.open(p)as im:assert im.size==(1400,1000)
 proof+=[p.name,cp.name]
m={'component_id':'MOTO-ENGINE-PROTECTION-TERMINAL-A-001','revision':'engine-protection-terminal-a-v1','source_sha256':s,'export_sha256':g,'scope':'Original first visible terminal-A. Tube/weld/opposite terminal/hook/spacer/fasteners absent; exact dimensions, variant, side and contact unqualified. Tiny dark mark unresolved, no third bore.','proof_ownership':'Explicit A-only construction/source/render proof list plus attributed documentary input; no ROOT runtime proofs silently collected.','files':rows(inputs+[O/n for n in proof]),'visible_first_terminal_twohole_surface_built':True,'complete_guard_assembly':False,'all_metric_parameters_estimated':True,'current_RDC_identity_verified':False,'installed_mount_contact_or_strength_verified':False,'mobile_LOD_qualified':False,'physical_iphone_tested':False,'material_reflectance_measured':False,'art_accepted':False};(O/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('TERMINAL_A_SEALED',len(m['files']),sha(O/'manifest.json'))
