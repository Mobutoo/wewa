"""Curated freeze of exterior connector2, its unchanged shape and bounded pose."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/ignition-connector-v2';read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not(H/'preflight-manifest-v2.json').exists()
B=read(H/'build-report-v2.json');P=read(H/'parameters-v2.json');I=read(H/'current-context-inputs-v2.json');source=H/'ignition-connector-v2.blend';glb=H/'ignition-connector-v2-inspection.glb'
assert sha(source)==B['source_sha256'] and sha(glb)==B['export_sha256']
assert sha(H/'ignition-connector-v2-geometry.blend')==B['geometry_source_sha256'] and sha(H/'ignition-connector-v2-geometry.glb')==B['geometry_export_sha256']
for key in ['original_geometry_source','original_geometry_report','pigtail_source','pigtail_report','pigtail_parameters','baseline_shape_parameters']:assert sha(R/P[key])==P[key+'_sha256']
for key in ['body','pigtail','instruments']:assert sha(R/I[key+'_source'])==I[key+'_source_sha256']
assert B['conditional_interfaces_passed'] and B['source_geometry_exact'] and B['source_libraries']==B['source_file_images']==0
S=read(O/'source-geometry-check-v2.json');assert S['source_sha256']==sha(source) and S['actual_reopened_source_geometry_normals_UV_indices_matrices_protected']
assert read(O/'export-check-v2.json')['glTF_errors']==0
N=read(O/'protected-material-export-v2.json');assert N['source_sha256']==sha(source)
assert all(q['actual_native_bytes_identical']for q in N['attributes']) and all(q['actual_world_matrix_identical']for q in N['matrices'])
assert not N['normalmap_used'] and N['texture_images']==0 and not N['native_tangents_repaired']
C=read(O/'conditional-point-containment.json');assert C['source_sha256']==B['geometry_source_sha256']
for row in C['guide_checks']:
    q=row['body_surface_sample_vs_guide'];assert row['surface_crossing_pairs']==q['inside']==q['boundary']==q['ambiguous']==0
F=read(O/'camera-preflight-v2.json');assert F['source_sha256']==sha(source) and len(F['views'])==4
assert all(q['camera_preflight']['technical_preflight_passed']for q in F['views'])
G=read(O/'geometry-preview-review-v2.json');Q=read(O/'preview-review-v2.json')
assert G['source_sha256']==B['geometry_source_sha256'] and G['ready_for_representative_material'] and len(G['actual_images_opened'])==8
assert Q['source_sha256']==sha(source) and Q['ready_for_isolated_final96'] and len(Q['actual_images_opened'])==4
for record in [G,Q]:
    for row in record['actual_images_opened']:
        cp=Path(row['checkpoint_private']);j=read(cp);assert row['actually_opened'] and j['source_sha256']==record['source_sha256']
        assert j['configuration_sha256']==hashlib.sha256(json.dumps(j['configuration'],sort_keys=True).encode()).hexdigest()
        for output in j['outputs']:assert sha(cp.parent/output['file'])==output['sha256']
        expected='render_geometry_v2.py'if record is G else'render_v2.py'
        assert j['configuration']['render_script_sha256']==sha(H/expected) and j['configuration']['protocol_sha256']==sha(H/'render_checkpoint.py')
J=read(O/'joint-geometry-review.json');assert len(J['actual_images_opened'])==4
for row in J['actual_images_opened']:
    assert row['actually_opened'] and row['own_pigtail_source_sha256']==I['pigtail_source_sha256']
    cp=Path(row['checkpoint_private']);j=read(cp);assert j['source_sha256']==B['geometry_source_sha256']
    for output in j['outputs']:assert sha(cp.parent/output['file'])==output['sha256']
core=['README_v2.md','parameters.json','parameters-v2.json','material-parameters-v2.json','provenance-v2.json','build_v2.py','material_v2.py','recipe_v2.py','geometry-report-v2.json','build-report-v2.json','ignition-connector-v2-geometry.blend','ignition-connector-v2-geometry.glb','ignition-connector-v2.blend','ignition-connector-v2-inspection.glb','check_geometry_export_v2.mjs','check_export_v2.mjs','check_material_export_v2.mjs','check_source_material_v2.py','check_pose_containment_v2.py','check_instruments5_geometry.mjs','render_geometry_v2.py','render_current_context_v2.py','render_current_reflection_v2.py','current-context-inputs-v2.json','render_v2.py','camera_preflight.py','render_checkpoint.py','record_preflight_v2.py','record_review_v2.py']
reports=['geometry-source-check','geometry-export-check','source-geometry-check','source-geometry-check-v2','source-material-check','export-check-v2','pose-only-protected-export','protected-material-export-v2','conditional-point-containment','current-instruments-v5-geometry-equivalence','camera-preflight-v2','geometry-gray-review-v2','geometry-preview-review-v2','joint-geometry-review','preview-review-v2']
files=[H/n for n in core]+[O/(n+'.json')for n in reports]+[H.parent/'throttle-control/control_geometry.py']
files += [R/P[key]for key in ['original_geometry_source','original_geometry_report','pigtail_source','pigtail_report','pigtail_parameters','baseline_shape_parameters']]
files += [R/I[key+'_source']for key in ['instruments','pigtail']]
files += [R/'creative/research/ignition-connector/observations-before-form.json',R/'creative/research/ignition-connector/material-observations-v2.json',R/'creative/research/ignition-connector/joint-route-study-v1/plan-before-route.json']
archive=H/'diagnostics/first-pigtail-placement-refused/diagnostic-manifest.json';files.append(archive)
for row in read(archive)['files']:
    p=R/row['path'];assert sha(p)==row['sha256'];files.append(p)
assert all(p.is_file()for p in files)
result={'component_id':B['component_id'],'revision':'ignition-connector-v2','source_sha256':sha(source),'export_sha256':sha(glb),'files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(set(files))],'scope':'Only the exterior hollow connector housing. Original local geometry protected from refused first pose; root aligned with revised pigtail3 as an artistic exterior mounting hypothesis. Real instruments5/context unchanged, no shrink or translation of other parts. Closed wall, empty mating cavity and wire-entry opening with estimated back/section; no contacts, pinout, counterpart or certified latch function. Provisional0.3mm axial discontinuity is not an electrical connection. Original constant dark polymer proposal, no measured grain/chemistry. Surface and sampled point checks are not exhaustive installed-fit or coplanar clearance proof.','all_dimensions_estimated':True,'automatic_attachment_allowed':False,'art_accepted':False,'physical_iphone_tested':False}
(H/'preflight-manifest-v2.json').write_text(json.dumps(result,indent=2)+'\n');print('FROZEN_CONNECTOR_V2',len(result['files']),sha(source),sha(glb))
