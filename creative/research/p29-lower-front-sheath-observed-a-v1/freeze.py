"""Hash-seal one bounded P29 study after staged visual reads and actual checks."""
from pathlib import Path
import json,hashlib
R=Path('/workspace/wewa');K='p29-lower-front-sheath-observed-a-v1'
D=R/'creative/research'/K;H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;A=R/'creative/research/p29-lower-front-sheath-evidence-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
assert not (O/'delivery-frozen.json').exists(),'Do not edit frozen delivery'
f=read(O/'catalog-fragment.json');assert f['source_sha256']==sha(R/f['source'])
for folder,rec,cnt,samples in [('gray-preview-v2','gray-read.json',3,16),('material-preview-v2','preview-read.json',2,16),('material-96','final-read.json',3,96)]:
 r=read(O/folder/'render-report.json');v=read(O/rec)['views'];assert len(r['views'])==len(v)==cnt
 assert r['protocol_sha256']==sha(D/'render.py') and r['source_sha256']==sha(R/r['source'])
 for x in r['views']:assert x['samples']==samples and sha(R/x['PNG'])==x['PNG_sha256'] and sha(R/x['EXR'])==x['EXR_sha256']
 for x in v:assert x['actually_viewed'] and sha(R/x['path'])==x['sha256']
raw=read(O/'raw-check.json');assert len(raw['files'])==3 and all(x['all_channels_FLOAT32']for x in raw['files'])
p=read(O/'native-glb-parity.json');assert len(p['objects'])==1 and p['native_sha256']==f['source_sha256'] and p['glb_sha256']==sha(H/(K+'-inspection.glb'))
assert all(x['oriented_triangle_connectivity_identical'] and x['maximum_native_imported_glb_vertex_distance_m']<1e-6 and x['maximum_corner_normal_vector_distance']<.001 for x in p['objects'])
v=read(H/(K+'-inspection.glb.validator.json'));assert v['issues']['numErrors']==v['issues']['numWarnings']==0
c=read(O/'native-reopen-check.json');assert c['source_sha256']==sha(H/'coord-exemplar.blend') and c['parents'][0]['visible_geometry_objects']==1 and c['parents'][0]['source_sha256']==f['source_sha256']
assert c['protocol_sha256']==sha(R/'tools/check_whole_exterior_coverage_v3.py')
e=read(O/'inspection-v3/engine-check.json');assert not e['page_errors'] and not e['http_failures'] and e['capture_tool_sha256']==sha(D/'capture-engine.py') and e['inspector_sha256']==sha(D/'engine-lab/review.js')
for x in e['exports']:assert sha(R/x['path'])==x['sha256']
for x in read(O/'engine-read.json')['views']:assert x['actually_viewed'] and sha(R/x['path'])==x['sha256']
parents=read(A/'native-audit.json')['sources']
for x in parents:assert sha(R/x['path'])==x['sha256']
for x in read(D/'G0-G2.json')['sources']:assert sha(Path(x['private_path']))==x['sha256']
paths=[p for folder in [D,H,O,A]for p in folder.rglob('*')if p.is_file()and '__pycache__'not in p.parts and p.name not in ['delivery.json','delivery-frozen.json']]
paths += [R/x['path']for x in parents]
paths += [R/'tools'/x for x in ['check_whole_exterior_coverage_v3.py','blender_component_camera_preflight.py','front_completion_check_raw_v1.py','front_completion_validate.mjs']]
paths += [R/'app/public/materials/kloppenheim_06_puresky_1k.hdr',R/'creative/library/motorcycle-reference-views.json']
paths=sorted(set(paths));rows=[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in paths]
delivery={'schema':1,'kind':'one_bounded_observed_front_lower_sheath_study','authorization':'Coordinator dispatch within user-authorized autonomous motorcycle completion','component_id':f['component_id'],'package':'P29','new_physical_ids':0,'physical_count_increment':0,'partial_study':True,'main_source':f['source'],'collection':f['collection'],'root':f['root'],'fragment':str((O/'catalog-fragment.json').relative_to(R)),'render_report':f['render_report'],'coord_plan':str((D/'coord-plan.json').relative_to(R)),'function_assigned':False,'historical_A_B_bijection_proven':False,'automatic_historical_replacement_allowed':False,'historical_sources_unchanged':True,'gray3_material2_native96x3_actually_read':True,'neutral_FLOAT32_raw_verified':True,'actual_native_glb_oriented_triangle_parity':True,'actual_babylon_read':True,'stock_whole_checker_passed':True,'no_hidden_upper_route_or_end_fittings':True,'depth_uncertainty_mm':[-15,15],'steering_flex_qualified':False,'fit_qualified':False,'G4_reception':False,'G8':False,'art_accepted':False,'files':rows,'file_count':len(rows),'total_bytes':sum(x['bytes']for x in rows)}
blob=(json.dumps(delivery,indent=2)+'\n').encode()
for n in ['delivery.json','delivery-frozen.json']:(O/n).write_bytes(blob)
for x in rows:assert sha(R/x['path'])==x['sha256'] and (R/x['path']).stat().st_size==x['bytes']
print(json.dumps({'freeze':str((O/'delivery-frozen.json').relative_to(R)),'sha256':sha(O/'delivery-frozen.json'),'files':len(rows),'bytes':delivery['total_bytes']}))
