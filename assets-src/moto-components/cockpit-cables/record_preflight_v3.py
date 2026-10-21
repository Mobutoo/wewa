"""Freeze only the bounded route revision and its explicitly attributed proofs."""
from pathlib import Path
import json, hashlib
H=Path(__file__).resolve().parent; R=H.parents[2]; O=R/'creative/reviews/cockpit-cables-v3'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
assert not (H/'preflight-manifest-v3.json').exists()
B=read(H/'build-report-v3.json'); P=read(H/'parameters-v3.json'); I=read(H/'render-inputs-v3.json')
source=R/I['source']; export=R/I['export']
assert sha(source)==B['source_sha256'] and sha(export)==B['export_sha256']
for key in ['source','export','connector_guide','instruments_guide']:
    assert sha(R/I[key])==I[key+'_sha256']
for key in ['baseline_source','baseline_export','baseline_parameters','baseline_report','ignition_parameters','connector_snapshot_source','visor_source']:
    assert sha(R/P[key])==P[key+'_sha256']
assert B['lower_two_source_geometry_normals_UV_indices_matrices_identical'] and B['actual_initial_axial_stations_unchanged']==36
assert B['conditional_interfaces_passed'] and B['self_nonadjacent_crossings']==0
assert B['source_libraries']==B['source_file_images']==0
assert all(q['surface_crossing_pairs']==0 for q in B['conditional_interface_checks'])
E=read(O/'export-check.json'); assert E['glTF_errors']==0
assert sum(q['triangles'] for q in E['meshes'])==59328
for row in read(O/'protected-export-invariants.json')['protected_lower_objects']:
    assert row['world_matrix_identical'] and row['material_constants_identical']
    assert all(q['actual_native_bytes_identical'] for q in row['attributes'])
assert read(O/'source-material-lineage.json')['actual_native_pigtail_material_constants_identical']
assert read(O/'evaluated-source-check.json')['source_libraries']==0
F=read(O/'camera-preflight.json'); assert len(F['views'])==2
assert all(q['camera_preflight']['technical_preflight_passed'] for q in F['views'])
Q=read(O/'preview-review-v3.json'); assert Q['ready_for_isolated_final96'] and len(Q['actual_images_opened'])==2
G=read(O/'geometry-preview-review-v3.json'); assert G['ready_for_unchanged_material_preview'] and len(G['actual_images_opened'])==4
for row in Q['actual_images_opened']+G['actual_images_opened']:
    cp=Path(row['checkpoint_private']); data=read(cp); assert row['actually_opened']
    assert data['configuration_sha256']==hashlib.sha256(json.dumps(data['configuration'],sort_keys=True).encode()).hexdigest()
    for output in data['outputs']: assert sha(cp.parent/output['file'])==output['sha256']
    if row in Q['actual_images_opened']:
        assert data['source_sha256']==sha(source) and data['configuration']['samples']==24
        assert data['configuration']['render_script_sha256']==sha(H/'render_v3.py')
    else:
        assert row['own_pigtail_source_sha256']==sha(source)
        assert data['source_sha256']==I['connector_guide_sha256']
entry=read(O/'entry-interface-diagnostic-review.json'); assert entry['actually_opened'] and entry['source_sha256']==sha(source)
core=['README_v3.md','parameters-v3.json','provenance-v3.json','build_v3.py','build-report-v3.json','cockpit-cables-v3.blend','cockpit-cables-v3-inspection.glb','check_export_v3.mjs','check_protected_export_v3.mjs','check_material_lineage_v3.mjs','check_current_geometry_v3.py','recipe_v3.py','render-inputs-v3.json','render_v3.py','render_entry_diagnostic_v3.py','camera_preflight_v3.py','render_checkpoint_v3.py','record_preflight_v3.py','record_review_v3.py']
reports=['source-geometry-check','export-check','protected-export-invariants','source-material-lineage','evaluated-source-check','camera-preflight','geometry-preview-review-v3','preview-review-v3','entry-interface-diagnostic-review']
files=[H/n for n in core]+[O/(n+'.json') for n in reports]
files += [R/P[k] for k in ['baseline_source','baseline_export','baseline_parameters','baseline_report','ignition_parameters','connector_snapshot_source','visor_source']]
files += [R/I[k] for k in ['connector_guide','instruments_guide']]
files += [R/'creative/research/cockpit-cables/reference-observations.json',R/'creative/research/ignition-connector/joint-route-study-v1/plan-before-route.json',R/'creative/research/ignition-connector/observations-before-form.json',H.parent/'ignition-connector/current-context-inputs-v2.json',H.parent/'ignition-connector/render_current_context_v2.py',H.parent/'ignition-connector/render_current_reflection_v2.py',R/'creative/reviews/ignition-connector-v2/current-instruments-v5-geometry-equivalence.json',R/'creative/reviews/ignition-connector-v2/conditional-point-containment.json']
assert all(p.is_file() for p in files)
result={'component_id':B['component_id'],'revision':'cockpit-cables-v3','source_sha256':sha(source),'export_sha256':sha(export),'files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(set(files))],'scope':'Route-only artistic exterior placement of the ignition pigtail; last two controls revised. First36 axial stations and two lower source/native meshes protected. Old v2, refused first connector placement and technical diagnostics preserved separately. Unchanged constant black estimated polymer. Actual instruments5 and connector2 neutral contexts, no reception transferred. Two lower free sheaths retain historical proofs. No full upper harness, contacts/pinout, real installed fit, steering-flex qualification or game LOD.','all_dimensions_estimated':True,'automatic_attachment_allowed':False,'art_accepted':False,'physical_iphone_tested':False}
(H/'preflight-manifest-v3.json').write_text(json.dumps(result,indent=2)+'\n')
print('FROZEN_COCKPIT_CABLES_V3',len(result['files']),sha(source),sha(export))
