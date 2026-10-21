"""Bind one bounded exterior after actual component diagnostics, never reception."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-intake-insulator-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=H/'engine-intake-insulator-v1.blend';glb=H/'engine-intake-insulator-inspection.glb'
build=json.loads((H/'build-report.json').read_text());ex=json.loads((O/'export-check.json').read_text())
interface=json.loads((O/'interface-solid-check.json').read_text());opening=json.loads((O/'opening-depth-check.json').read_text())
preview=json.loads((O/'preview-review.json').read_text());camera=json.loads((O/'camera-layout-preflight.json').read_text());paths=json.loads((O/'reference-path-check.json').read_text())
for q in [build,ex,interface,opening,preview,camera,paths]:assert q['source_sha256']==sha(source)
assert sha(glb)==build['export_sha256']==ex['sha256']==preview['export_sha256']
assert ex['glTF_errors']==0 and len(ex['meshes'])==1 and ex['meshes'][0]['zeroAreaTriangles']==0
assert len(build['geometry'])==1 and len(opening['through_openings'])==3 and len(opening['closed_surface_witnesses'])==4
assert paths['direct_libraries_relative'] and paths['all_loaded_targets_exist']
for row in interface['pairs']:
    assert row['surface_pairs']==0
    for k in ['a_vertices_in_b','b_vertices_in_a']:assert not any(row[k][n]for n in ['inside','ambiguous','boundary_100nm'])
assert len(camera['views'])==5
for v in camera['views']:
    f=v['camera_preflight'];assert not f['actual_vertices_outside_depth_range']
    assert not f['projected_extent_outside_margin']or f['allow_deliberate_crop']
assert preview['ready_for_isolated_final96'] and len(preview['actual_images_opened'])==6
for row in preview['actual_images_opened']:
    assert row['actually_opened'];p=Path(row['checkpoint']);q=json.loads(p.read_text())
    assert q['source_sha256']==sha(source)and q['configuration']['samples']in[8,24]
    assert q['configuration']['render_script_sha256']==sha(H/'render.py')and q['configuration']['protocol_sha256']==sha(H/'render_checkpoint.py')
    for v in q['outputs']:assert sha(p.parent/v['file'])==v['sha256']
files=[H/n for n in ['engine-intake-insulator-v1.blend','engine-intake-insulator-inspection.glb','build.py','build-report.json','parameters.json','README.md','provenance.json','check_export.mjs','check_interface.py','check_openings.py','check_reference_paths.py','render.py','render_checkpoint.py','camera_preflight.py','record_preflight.py','record_review.py']]
files +=[O/n for n in ['source-geometry-check.json','export-check.json','interface-solid-check.json','opening-depth-check.json','reference-path-check.json','camera-layout-preflight.json','camera-rejection-history.json','preview-review.json','README.md']]
files +=[R/'creative/research/engine-intake-insulator/fabrication-plan-v1.json',R/'creative/research/engine-intake-insulator/witness-projection-check.json',R/'creative/research/engine17-intake-exterior-v1/report.json',H.parent/'engine-head/engine-head-v3.blend',H.parent/'throttle-control/control_geometry.py',H.parent/'clutch-control/topology_cleanup_v2.py',H.parent/'front-brake-plate/csg.py']
manifest={'component_id':build['component_id'],'revision':build['revision'],'source_sha256':sha(source),'export_sha256':sha(glb),
          'files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(set(files))],
          'scope':'One original conditional UG5 insulator exterior, three true through openings, four closed witness estimates, visible front groove and explicitly simplified unobserved reverse. Constant material baseline; cotes, chemistry and OEM/RDC fit unreceived.',
          'all_dimensions_estimated':True,'exact_RDC_identity_confirmed':False,'art_accepted':False,'physical_iphone_tested':False}
(H/'preflight-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('FROZEN_INTAKE_INSULATOR',len(manifest['files']),sha(source),sha(glb))
