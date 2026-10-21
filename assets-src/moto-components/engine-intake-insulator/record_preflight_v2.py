"""Freeze an examined material-only revision while preserving all v1 pins."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-intake-insulator-v2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=H/'engine-intake-insulator-v2.blend';glb=H/'engine-intake-insulator-v2-inspection.glb';assert not (H/'preflight-manifest-v2.json').exists()
v1=json.loads((H/'preflight-manifest.json').read_text())
for row in v1['files']:assert sha(R/row['path'])==row['sha256'],row['path']
b=json.loads((H/'build-report-v2.json').read_text());reports={k:json.loads((O/(k+'.json')).read_text())for k in ['export-check','protected-export-invariants','material-export-check','actual-embedded-map-pixel-check','interface-solid-check','reference-path-check','camera-layout-preflight','preview-review']}
for q in reports.values():assert q['source_sha256']==sha(source)
assert b['source_sha256']==sha(source)and b['export_sha256']==sha(glb)==reports['export-check']['sha256'];assert b['positions_indices_corner_normals_matrices_bit_identical']and b['protected_v1_geometry_digest']==b['new_geometry_digest'];assert b['normalmap_applied']is False and b['bump_or_displacement_applied']is False
assert reports['export-check']['glTF_errors']==0 and reports['protected-export-invariants']['actual_triangle_positions_normals_order_bit_identical']and reports['protected-export-invariants']['world_matrix_bit_identical']
assert reports['material-export-check']['normalmap_present']is False and reports['material-export-check']['tangent_attribute_present']is False and reports['material-export-check']['actual_UV_zero_area_triangles']==0
assert reports['actual-embedded-map-pixel-check']['native_embedded_payloads_actually_decoded']
for row in reports['interface-solid-check']['pairs']:
 assert row['surface_pairs']==0
 for k in ['a_vertices_in_b','b_vertices_in_a']:assert not any(row[k][n]for n in ['inside','ambiguous','boundary_100nm'])
assert reports['reference-path-check']['direct_libraries_relative']and len(reports['reference-path-check']['maps'])==2
assert len(reports['camera-layout-preflight']['views'])==3
for row in reports['camera-layout-preflight']['views']:
 f=row['camera_preflight'];assert not f['actual_vertices_outside_depth_range'];assert not f['projected_extent_outside_margin']or f['allow_deliberate_crop']
p=reports['preview-review'];assert p['ready_for_material_final96']and len(p['actual_images_opened'])==5
for row in p['actual_images_opened']:
 assert row['actually_opened'];cp=Path(row['checkpoint']);q=json.loads(cp.read_text());assert q['source_sha256']==sha(source)and q['configuration']['render_script_sha256']==sha(H/'render_v2.py')and q['configuration']['protocol_sha256']==sha(H/'render_checkpoint.py')
 for v in q['outputs']:assert sha(cp.parent/v['file'])==v['sha256']
files=[H/n for n in ['engine-intake-insulator-v2.blend','engine-intake-insulator-v2-inspection.glb','build_v2.py','build-report-v2.json','parameters-v2.json','README_v2.md','provenance-v2.json','check_initial_UV_v2.py','check_export_v2.mjs','check_invariants_v2.mjs','check_material_export_v2.mjs','check_exported_map_pixels_v2.py','check_interface_v2.py','check_reference_paths_v2.py','render_v2.py','render_checkpoint.py','camera_preflight.py','record_preflight_v2.py','record_review_v2.py','textures-v2/insulator-striation-basecolor-v2.png','textures-v2/insulator-striation-roughness-v2.png','engine-intake-insulator-v1.blend','engine-intake-insulator-inspection.glb','build-report.json','preflight-manifest.json']]
files+=[O/n for n in ['source-material-check.json','native-UV-initial-check.json','export-check.json','protected-export-invariants.json','material-export-check.json','actual-embedded-map-pixel-check.json','interface-solid-check.json','reference-path-check.json','camera-layout-preflight.json','preview-review.json','README.md']]
files+=[R/'creative/research/engine-intake-insulator/fabrication-plan-v2.json',R/'creative/research/engine17-intake-exterior-v1/report.json',H.parent/'engine-head/engine-head-v3.blend',H.parent/'engine-intake-manifold/engine-intake-manifold-v1.blend']
m={'component_id':b['component_id'],'revision':b['revision'],'source_sha256':sha(source),'export_sha256':sha(glb),'files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(set(files))],'scope':'Original color/roughness striations only, no normalmap/tangent or relief claim. V1 source geometry/indices/normals/matrices and actual exported triangle corners protected. Striation direction/scale, chemistry, reverse finish, physical dimensions and OEM/RDC fit remain unreceived.','all_dimensions_estimated':True,'exact_RDC_identity_confirmed':False,'art_accepted':False,'physical_iphone_tested':False}
(H/'preflight-manifest-v2.json').write_text(json.dumps(m,indent=2)+'\n');print('FROZEN_INSULATOR2',len(m['files']),sha(source),sha(glb))
