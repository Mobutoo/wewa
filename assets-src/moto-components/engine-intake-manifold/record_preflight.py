"""Bind actual checked outputs; technical evidence is never art/OEM reception."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-intake-manifold-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=H/'engine-intake-manifold-v1.blend';glb=H/'engine-intake-manifold-inspection.glb'
assert not (H/'preflight-manifest.json').exists(), 'Do not replace a closed gel'
b=json.loads((H/'build-report.json').read_text());reports={k:json.loads((O/(k+'.json')).read_text())for k in ['export-check','interface-solid-check','opening-depth-check','reference-path-check','material-export-check','actual-embedded-map-pixel-check','preview-review','camera-layout-preflight']}
for q in reports.values():assert q['source_sha256']==sha(source)
assert sha(glb)==b['export_sha256']==reports['export-check']['sha256']
assert reports['export-check']['glTF_errors']==0 and len(reports['export-check']['meshes'])==1
assert len(b['geometry'])==1 and b['geometry'][0]['connected_shells']==1
assert len(reports['opening-depth-check']['through_rays'])==5
assert reports['reference-path-check']['direct_libraries_relative']and reports['reference-path-check']['all_loaded_targets_exist']
assert len(reports['material-export-check']['textures'])==2 and reports['actual-embedded-map-pixel-check']['pixel_payloads_decoded']
for q in reports['interface-solid-check']['pairs']:
 assert q['surface_pairs']==0
 for k in ['a_vertices_in_b','b_vertices_in_a']:assert not any(q[k][n]for n in ['inside','ambiguous','boundary_100nm'])
assert len(reports['camera-layout-preflight']['views'])==4
for q in reports['camera-layout-preflight']['views']:
 f=q['camera_preflight'];assert not f['actual_vertices_outside_depth_range'];assert not f['projected_extent_outside_margin']or f['allow_deliberate_crop']
p=reports['preview-review'];assert p['ready_for_isolated_final96']and len(p['actual_images_opened'])==7
for row in p['actual_images_opened']:
 assert row['actually_opened'];cp=Path(row['checkpoint']);q=json.loads(cp.read_text());assert q['source_sha256']==sha(source)
 assert q['configuration']['render_script_sha256']==sha(H/'render.py')and q['configuration']['protocol_sha256']==sha(H/'render_checkpoint.py')
 for v in q['outputs']:assert sha(cp.parent/v['file'])==v['sha256']
files=[H/n for n in ['engine-intake-manifold-v1.blend','engine-intake-manifold-inspection.glb','engine-intake-manifold-v1-geometry.blend','engine-intake-manifold-v1-geometry.glb','engine-intake-manifold-v1-topology.blend','engine-intake-manifold-v1-topology.glb','build.py','geometry-report.json','topology_stage.py','topology-report.json','diagnose_native_tangents.py','material.py','recipe.py','section_geometry.py','build-report.json','interfaces.json','parameters.json','README.md','provenance.json','check_geometry_export.mjs','check_export.mjs','check_interface.py','check_openings.py','check_reference_paths.py','check_material_export.mjs','check_exported_map_pixels.py','render.py','render_geometry.py','render_checkpoint.py','camera_preflight.py','record_preflight.py','record_review.py','textures/manifold-grain-normal-v1.png','textures/manifold-grain-roughness-v1.png']]
files+=[O/n for n in ['source-geometry-check.json','geometry-source-check.json','geometry-export-check.json','source-topology-refinement.json','material-padding-rejection.json','export-check.json','interface-solid-check.json','opening-depth-check.json','reference-path-check.json','material-build-report.json','material-export-check.json','actual-embedded-map-pixel-check.json','camera-layout-preflight.json','preview-review.json','README.md']]
files+=[R/'creative/research/engine-intake-manifold/fabrication-plan-v1.json',R/'creative/research/engine17-intake-exterior-v1/report.json',H.parent/'engine-intake-insulator/engine-intake-insulator-v1.blend',H.parent/'engine-head/engine-head-v3.blend',H.parent/'throttle-control/control_geometry.py',H.parent/'clutch-control/topology_cleanup_v2.py',H.parent/'front-brake-plate/csg.py']
m={'component_id':b['component_id'],'revision':b['revision'],'source_sha256':sha(source),'export_sha256':sha(glb),'files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(set(files))],'scope':'One original hollow cast-manifold exterior conditional on D04UG5. All dimensions, reverse, sidefeature function, orientation, original grain scale and OEM/RDC fit remain estimates/unreceived. Native maps/UV/buffers and bounded candidate interfaces checked; no art, iPhone or physical flow reception.','all_dimensions_estimated':True,'exact_RDC_identity_confirmed':False,'art_accepted':False,'physical_iphone_tested':False}
(H/'preflight-manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('FROZEN_MANIFOLD',len(m['files']),sha(source),sha(glb))
