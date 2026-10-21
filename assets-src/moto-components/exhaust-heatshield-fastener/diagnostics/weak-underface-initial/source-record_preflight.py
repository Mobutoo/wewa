"""Candidate partial screw, never implicit reception of unobserved crown/drive."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/exhaust-heatshield-fastener-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert not(H/'preflight-manifest.json').exists();source=H/'exhaust-heatshield-fastener-v1.blend';glb=H/'exhaust-heatshield-fastener-inspection.glb';b=json.loads((H/'build-report.json').read_text());assert sha(source)==b['source_sha256']and sha(glb)==b['export_sha256'];reports={n:json.loads((O/(n+'.json')).read_text())for n in ['export-check','uv-material-export-check','self-surface-check','interface-solid-check','reference-path-check','camera-layout-preflight','preview-review']}
for q in reports.values():assert q['source_sha256']==sha(source)
assert reports['export-check']['glTF_errors']==0 and reports['self-surface-check']['nonadjacent_surface_crossings']==0
assert reports['uv-material-export-check']['physical_type_count']==1 and reports['uv-material-export-check']['conditional_instances']==2
for q in reports['uv-material-export-check']['rows']:assert q['zero_area_UV']==0
assert reports['reference-path-check']['direct_libraries_relative']and reports['reference-path-check']['all_loaded_targets_exist'];assert len(reports['interface-solid-check']['pairs'])==5
for q in reports['interface-solid-check']['pairs']:
 assert q['surface_pairs']==0
 for k in ['a_vertices_in_b','b_vertices_in_a']:assert not any(q[k][t]for t in ['inside','ambiguous','boundary_100nm'])
assert len(reports['camera-layout-preflight']['views'])==4
for q in reports['camera-layout-preflight']['views']:
 f=q['camera_preflight'];assert not f['actual_vertices_outside_depth_range'];assert not f['projected_extent_outside_margin']or f['allow_deliberate_crop']
p=reports['preview-review'];assert p['ready_for_isolated_final96']and len(p['actual_images_opened'])==4
for row in p['actual_images_opened']:
 assert row['actually_opened'];cp=Path(row['checkpoint_private']);q=json.loads(cp.read_text());assert q['source_sha256']==sha(source)and q['configuration']['samples']==24;assert q['configuration']['render_script_sha256']==sha(H/'render.py')and q['configuration']['protocol_sha256']==sha(H/'render_checkpoint.py')
 for item in q['outputs']:assert sha(cp.parent/item['file'])==item['sha256']
P=json.loads((H/'parameters.json').read_text());files=[p for p in H.rglob('*')if p.is_file()and'__pycache__'not in p.parts and p.suffix in['.py','.mjs','.json','.blend','.glb','.md','.png','.log']and p.name!='preflight-manifest.json'];files +=[p for p in O.iterdir()if p.is_file()and p.suffix in ['.json','.md','.log']and p.name!='review-manifest.json'];files +=[R/'creative/research/exhaust-heatshield-fastener/reference-plan-v1.json',R/'creative/research/engine17-exhaust-exterior-v1/report.json',R/'creative/research/engine17-exhaust-exterior-v1/heatshield-targeted-v1/report.json',H.parent/'throttle-control/control_geometry.py']+[R/P[k]for k in ['shield_source','shield_interfaces','body_source']];x={'component_id':b['component_id'],'revision':b['revision'],'source_sha256':sha(source),'export_sha256':sha(glb),'files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(set(files))],'physical_type_count':1,'conditional_instances':2,'scope':'Partial screw candidate with observed bearing underface and short stem, two conditional instances. Crown/drive unobserved: plain provisional envelope explicitly INCOMPLETE. Catalogue M5x0.8 related only; local head/length/trace/seatgap and coating unmeasured. No hidden standoff/nut/engagement or independent washer fabricated. No OEM art fit physicaliPhone reception.','unresolved_visible_crown_or_drive':True,'art_accepted':False,'physical_iphone_tested':False};(H/'preflight-manifest.json').write_text(json.dumps(x,indent=2)+'\n');print('FROZEN_PARTIAL_SHIELD_FASTENER',len(x['files']),sha(source),sha(glb))
