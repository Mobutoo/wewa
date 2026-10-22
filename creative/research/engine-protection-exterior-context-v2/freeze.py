# Source template SHA256 198d6c728f878692e84890ed8074e68e9d7b5cefab4c3add42610041c6471f66; revised for recovered guide context and strict checks.
"""Seal four unchanged parents and completed review, with unresolved mounting explicit."""
from pathlib import Path
import json,hashlib
R=Path('/workspace/wewa');K='engine-protection-exterior-context-v2'
D=R/'creative/research'/K;H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
assert not (O/'delivery-frozen.json').exists(),'Immutable freeze already exists'
parents=read(D/'parent-native-read.json')['parents'];assert len(parents)==4
for p in parents:assert sha(R/p['source'])==p['sha256'] and sha(R/p['glb'])==p['glb_sha256']
meta=read(D/'native-links-and-transforms.json');assert meta['source_sha256']==sha(R/meta['source'])
f=read(O/'catalog-fragment.json');assert all(k in f for k in ['component_id','package','source','files','review','render_report'])
assert f['component_id']=='MOTO-ENGINE-PROTECTION-HOOP-001' and f['package']=='P26' and f['source_sha256']==meta['source_sha256']
assert f['context_pose_ready'] and f['new_physical_ids']==0
for folder,record,count,samples in [('gray-preview-v2','gray-read.json',3,16),('material-preview-v2','preview-read.json',2,16),('material-96','final-read.json',3,96)]:
 r=read(O/folder/'render-report.json');v=read(O/record)['views'];assert len(v)==len(r['views'])==count and r['source_sha256']==meta['source_sha256'] and r['protocol_sha256']==sha(D/'render.py')
 for x in r['views']:assert x['samples']==samples and sha(R/x['PNG'])==x['PNG_sha256'] and sha(R/x['EXR'])==x['EXR_sha256']
 for x in v:assert x['actually_viewed'] and sha(R/x['path'])==x['sha256']
raw=read(O/'raw-check.json');assert len(raw['files'])==3 and all(x['all_channels_FLOAT32']for x in raw['files'])
p=read(O/'native-glb-parity.json');glb=H/(K+'-inspection.glb');assert p['native_sha256']==meta['source_sha256'] and p['glb_sha256']==sha(glb) and len(p['objects'])==4
assert all(x['oriented_triangle_connectivity_identical'] and x['maximum_native_imported_glb_vertex_distance_m']<1e-6 and x['maximum_corner_normal_vector_distance']<.001 for x in p['objects'])
ex=read(D/'export-integrity.json');assert ex['output_sha256']==sha(glb) and ex['roundtrip_geometry_material_textures_identical'] and len(ex['objects'])==4 and ex['validation']['numErrors']==ex['validation']['numWarnings']==0
for o in ex['objects']:assert o['exact_geometry_material_texture_reuse'] and sha(R/o['source'])==o['source_sha256'] and o['source_mesh_proof']['primitives'][0]['material']['extensions']
strict=read(O/'export-buffer-check.json');assert strict['inspection_protocol_sha256']==sha(D/'check-all-tangents.mjs')
for e in strict['exports']:
 assert e['sha256']==sha(glb) and e['glTF_errors']==0 and e['glTF_warnings']==0
 t=e['tangent_frame'];assert t['vectors']>0 and t['max_unit_error']<=.001 and t['max_normal_dot']<=.001 and t['handedness_sign_is_unit']
 assert e['triangle_area_local_m2']['exactly_zero']==0
c=read(O/'native-reopen-check.json');assert c['parent_count']==1 and c['source_sha256']==sha(H/'coord-exemplar.blend') and c['parents'][0]['visible_geometry_objects']==4 and len(c['parents'][0]['nested_source_checks'])==4
assert c['protocol_sha256']==sha(R/'tools/check_whole_exterior_coverage_v3.py')
linked=read(O/'linked-reuse-check.json');assert linked['actual_wrapper_reopened'] and linked['source_sha256']==meta['source_sha256'] and linked['hoop_exact'] and len(linked['objects'])==4
assert linked['protocol_sha256']==sha(D/'check-linked-reuse.py') and all(x['same_linked_mesh_datablock'] and x['same_linked_material_slots']for x in linked['objects'])
engine=read(O/'inspection-v3/engine-check.json');assert not engine['page_errors'] and not engine['http_failures'] and engine['meshes']==4 and engine['textures_ready']
assert engine['capture_tool_sha256']==sha(D/'capture-engine.py') and engine['inspector_sha256']==sha(D/'engine-lab/review.js')
for e in engine['exports']:assert sha(R/e['path'])==e['sha256']
for x in read(O/'engine-read.json')['views']:assert x['actually_viewed'] and sha(R/x['path'])==x['sha256']
for x in read(D/'photo-read.json')['photos']:assert x['actually_viewed'] and sha(Path(x['private_path']))==x['sha256']
guide=read(D/'actual-guide-read.json');assert guide['actual_guide_opened'] and guide['guide_not_physical_parent'] and len(guide['objects'])==4
for x in read(D/'source-recovery.json')['files']:assert sha(R/x['local_snapshot'])==x['sha256']
g=read(D/'guide-native-recovery.json');assert sha(R/g['public_owned_native_snapshot'])==g['sha256']
witness=read(O/'open-joint-witness.json');assert witness['native_sha256']==meta['source_sha256'] and len(witness['actual_triangle_sample_checks'])==3
for x in witness['actual_triangle_sample_checks']:assert .0029<x['minimum_sampled_distance_m']<=x['maximum_sampled_distance_m']<.0031
assert witness['protocol_sha256']==sha(D/'check-open-joints.py')
paths=[p for folder in [D,H,O]for p in folder.rglob('*')if p.is_file()and '__pycache__'not in p.parts and p.name not in ['delivery.json','delivery-frozen.json']]
paths += [R/p[k]for p in parents for k in ['source','glb']]
paths += [R/'tools'/x for x in ['check_whole_exterior_coverage_v3.py','check_motorcycle18_exports_v2.mjs','blender_component_camera_preflight.py','front_completion_check_raw_v1.py']]
paths += [R/'app/public/materials/kloppenheim_06_puresky_1k.hdr']
paths=sorted(set(paths));entries=[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in paths]
delivery={'schema':1,'kind':'four_existing_guard_parents_guide_based_rigid_context','authorization':'Coordinator dispatch within user-authorized autonomous motorcycle completion','component_id':f['component_id'],'package':'P26','main_source':f['source'],'main_collection':f['collection'],'root':f['root'],'fragment':str((O/'catalog-fragment.json').relative_to(R)),'render_report':f['render_report'],'coord_plan':f['coord_plan'],'new_physical_ids':0,'physical_count_increment':0,'historical_sources_unchanged':True,'hoop_geometry_and_pose_exact':True,'all_original_PBR_textures_clearcoat_preserved':True,'all_tangents_strictly_checked':True,'gray3_material2_native96x3_actually_read':True,'independent_neutral_FLOAT32_raw_verified':True,'actual_native_glb_parity_verified':True,'actual_babylon_captured_read':True,'direct_wrapper_stock_whole_checker_passed':True,'guide_source_recovered_and_actually_opened':True,'context_pose_ready':True,'coordinator_can_replace_single_hoop_keeping_world_pose':True,'nominal_review_gap_m':.003,'gap_is_not_measured_OEM_clearance':True,'fit_qualified':False,'G4_reception':False,'G8':False,'art_accepted':False,'files':entries,'file_count':len(entries),'total_bytes':sum(x['bytes']for x in entries)}
blob=(json.dumps(delivery,indent=2)+'\n').encode()
for n in ['delivery.json','delivery-frozen.json']:(O/n).write_bytes(blob)
for e in entries:assert sha(R/e['path'])==e['sha256'] and (R/e['path']).stat().st_size==e['bytes']
print(json.dumps({'freeze':str((O/'delivery-frozen.json').relative_to(R)),'sha256':sha(O/'delivery-frozen.json'),'files':len(entries),'bytes':delivery['total_bytes']}))
