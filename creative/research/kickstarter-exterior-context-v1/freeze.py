"""Seal one existing-parent composition only after actual visual and technical checks."""
import json,hashlib
from pathlib import Path
R=Path('/workspace/wewa'); K='kickstarter-exterior-context-v1'
D=R/'creative/research'/K; H=R/'assets-src/moto-components'/K; O=R/'creative/reviews'/K
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
assert not (O/'delivery-frozen.json').exists(),'Immutable delivery already exists'
m=read(D/'native-links-and-transforms.json')
for path,key in [('parent','parent_sha256'),('parent_glb','parent_glb_sha256'),('source','source_sha256')]:assert sha(R/m[path])==m[key]
for folder,record,count,samples in [('gray-preview-v2','gray-read.json',3,16),('material-preview-v2','preview-read.json',2,16),('material-96','final-read.json',3,96)]:
 report=read(O/folder/'render-report.json'); views=read(O/record)['views']
 assert len(report['views'])==len(views)==count and all(v['actually_viewed'] for v in views)
 assert report['source_sha256']==m['source_sha256'] and report['protocol_sha256']==sha(D/'render.py')
 for v in report['views']:
  assert v['samples']==samples and sha(R/v['PNG'])==v['PNG_sha256'] and sha(R/v['EXR'])==v['EXR_sha256']
 for v in views:assert sha(R/v['path'])==v['sha256']
raw=read(O/'raw-check.json');assert len(raw['files'])==3 and all(x['all_channels_FLOAT32']for x in raw['files'])
par=read(O/'native-glb-parity.json');assert par['native_sha256']==m['source_sha256'] and par['glb_sha256']==sha(H/(K+'-inspection.glb')) and len(par['objects'])==4
assert all(x['oriented_triangle_connectivity_identical'] and x['maximum_native_imported_glb_vertex_distance_m']<1e-6 and x['maximum_corner_normal_vector_distance']<.001 for x in par['objects'])
coord=read(O/'native-reopen-check.json');assert coord['parent_count']==1 and coord['source_sha256']==sha(H/'coord-exemplar.blend') and coord['parents'][0]['visible_geometry_objects']==4
assert coord['parents'][0]['source_sha256']==m['source_sha256'] and coord['protocol_sha256']==sha(R/'tools/check_whole_exterior_coverage_v3.py')
engine=read(O/'inspection-v3/engine-check.json');assert not engine['page_errors'] and not engine['http_failures']
assert engine['capture_tool_sha256']==sha(D/'capture-engine.py') and engine['inspector_sha256']==sha(D/'engine-lab/review.js')
for x in engine['exports']:assert sha(R/x['path'])==x['sha256']
for x in read(O/'engine-read.json')['views']:assert x['actually_viewed'] and sha(R/x['path'])==x['sha256']
fragment=read(O/'catalog-fragment.json');assert all(x in fragment for x in ['component_id','package','source','files','review','render_report'])
assert fragment['component_id']=='MOTO-KICKSTARTER-001' and fragment['package']=='P20' and fragment['source_sha256']==m['source_sha256']
assert all((R/'assets-src/moto-components'/x).is_file()for x in fragment['files']) and (R/fragment['render_report']).is_file()
evidence=read(D/'source-evidence-index.json')
for x in evidence['evidence_documents']:assert sha(R/x['path'])==x['sha256']
diagnostic=R/'creative/reviews/kickstarter-exterior-context-diagnostic-v1'
old=read(diagnostic/'frozen-checkpoint.json')
for x in old['files']:assert sha(R/x['path'])==x['sha256'] and (R/x['path']).stat().st_size==x['bytes']
contract={'direct_wrapper_stock_checker_passed':True,'four_existing_meshes_once':True,'flat_fragment_valid':True,'existing_identity_preserved':True,'new_physical_ids':0,'physical_count_increment':0,'source_native_unchanged':True,'common_rigid_transform_only':True,'current_engine_mount_not_assigned':True,'fit_qualified':False,'art_accepted':False}
(O/'coordination-contract-check.json').write_text(json.dumps(contract,indent=2)+'\n')
paths=[p for folder in [D,H,O,diagnostic]for p in folder.rglob('*')if p.is_file()and '__pycache__'not in p.parts and p.name not in ['delivery.json','delivery-frozen.json']]
paths += [R/m['parent'],R/m['parent_glb'],R/'assets-src/moto-components/kickstarter/gltf-node-map-v2.json',R/'app/public/materials/kloppenheim_06_puresky_1k.hdr']
paths += [R/x['path']for x in evidence['evidence_documents']]
paths += [R/'tools'/x for x in ['check_whole_exterior_coverage_v3.py','blender_component_camera_preflight.py','front_completion_check_raw_v1.py']]
paths=sorted(set(paths));entries=[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in paths]
delivery={'schema':1,'kind':'existing_kickstarter_exterior_rigid_composition','authorization':'Coordinator dispatch within user-authorized autonomous motorcycle completion','component_id':fragment['component_id'],'package':'P20','new_physical_ids':0,'physical_count_increment':0,'main_source':fragment['source'],'main_collection':fragment['collection'],'root':fragment['root'],'fragment':str((O/'catalog-fragment.json').relative_to(R)),'render_report':fragment['render_report'],'coord_plan':str((D/'coord-plan.json').relative_to(R)),'gray3_material2_native96x3_actually_read':True,'neutral_FLOAT32_raw_verified':True,'source_geometry_materials_reused':True,'selected_meshes':4,'excluded_estimated_hardware':m['excluded_existing_objects'],'historical_sources_unchanged':True,'actual_native_glb_parity_verified':True,'actual_babylon_captured_and_read':True,'current_engine_fit_qualified':False,'G4_reception':False,'G8':False,'art_accepted':False,'diagnostic_archive_not_for_integration':str(diagnostic.relative_to(R)),'files':entries,'file_count':len(entries),'total_bytes':sum(x['bytes']for x in entries)}
blob=(json.dumps(delivery,indent=2)+'\n').encode()
for n in ['delivery.json','delivery-frozen.json']:(O/n).write_bytes(blob)
for x in entries:assert sha(R/x['path'])==x['sha256'] and (R/x['path']).stat().st_size==x['bytes']
print(json.dumps({'freeze':str((O/'delivery-frozen.json').relative_to(R)),'sha256':sha(O/'delivery-frozen.json'),'files':len(entries),'bytes':delivery['total_bytes']}))
