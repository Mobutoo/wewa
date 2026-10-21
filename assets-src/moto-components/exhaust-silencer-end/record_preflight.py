"""Freeze actual source inputs only after explicit full-size preview review."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/exhaust-silencer-end-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=H/'exhaust-silencer-end-v1.blend';glb=H/'exhaust-silencer-end-inspection.glb';assert not(H/'preflight-manifest.json').exists()
b=json.loads((H/'build-report.json').read_text());assert sha(source)==b['source_sha256']and sha(glb)==b['export_sha256'];reports={n:json.loads((O/(n+'.json')).read_text())for n in ['export-check','self-surface-check','interface-solid-check','opening-wall-check','reference-path-check','material-export-check','actual-embedded-map-pixel-check','protected-export-invariants','camera-layout-preflight','preview-review']}
for q in reports.values():assert q['source_sha256']==sha(source)
assert reports['self-surface-check']['nonadjacent_surface_crossings']==0
assert reports['export-check']['glTF_errors']==0 and reports['actual-embedded-map-pixel-check']['native_embedded_payloads_actually_decoded'];assert len(reports['opening-wall-check']['lumen_rays'])==5 and len(reports['opening-wall-check']['actual_wall_rays'])==4
assert reports['reference-path-check']['direct_libraries_relative']and reports['reference-path-check']['all_loaded_targets_exist'];assert len(reports['interface-solid-check']['pairs'])==1
for pair in reports['interface-solid-check']['pairs']:
 assert pair['surface_pairs']==0
 for key in ['a_vertices_in_b','b_vertices_in_a']:assert not any(pair[key][k]for k in ['inside','ambiguous','boundary_100nm'])
assert len(reports['camera-layout-preflight']['views'])==4
for row in reports['camera-layout-preflight']['views']:
 q=row['camera_preflight'];assert not q['actual_vertices_outside_depth_range'];assert not q['projected_extent_outside_margin']or q['allow_deliberate_crop']
p=reports['preview-review'];assert p['ready_for_isolated_final96']and len(p['actual_images_opened'])==5
for row in p['actual_images_opened']:
 assert row['actually_opened'];cp=Path(row['checkpoint_private']);q=json.loads(cp.read_text());assert q['source_sha256']==sha(source)and q['configuration']['samples']==24
 assert q['configuration']['render_script_sha256']==sha(H/'render.py')and q['configuration']['protocol_sha256']==sha(H/'render_checkpoint.py')
 for v in q['outputs']:assert sha(cp.parent/v['file'])==v['sha256']
files=[p for p in H.rglob('*')if p.is_file()and '__pycache__'not in p.parts and p.suffix in ['.py','.mjs','.json','.blend','.glb','.png','.md']and p.name!='preflight-manifest.json']
files+=[p for p in O.iterdir()if p.is_file()and p.suffix in ['.json','.md','.log']and p.name!='review-manifest.json']
files+=[R/'creative/research/exhaust-silencer-end'/n for n in ['fabrication-plan-v1.json','material-plan-v1.json']];files+=[R/'creative/research/engine17-exhaust-exterior-v1/report.json'];P=json.loads((H/'parameters.json').read_text());files+=[R/P['body_source'],R/P['body_interfaces'],H.parent/'throttle-control/control_geometry.py']
m={'component_id':b['component_id'],'revision':b['revision'],'source_sha256':sha(source),'export_sha256':sha(glb),'files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(set(files))],'scope':'One visible rear annular closure with small outlet only. Body-derived section, local wall/lip/inset/gap, hidden front profile and optical finish estimated. Main shell unchanged, no heatshield, supports, fasteners, internal outlet pipe, CAT or baffles implicitly fabricated. No physical fit/art/OEM/iPhone reception.','all_dimensions_estimated':True,'exact_RDC_identity_confirmed':False,'art_accepted':False,'physical_iphone_tested':False};(H/'preflight-manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('FROZEN_SILENCER_END',len(m['files']),sha(source),sha(glb))
