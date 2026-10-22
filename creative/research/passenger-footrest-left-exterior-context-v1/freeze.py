from pathlib import Path
import json,hashlib
R=Path('/workspace/wewa');K='passenger-footrest-left-exterior-context-v1';D=R/'creative/research'/K;H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (O/'delivery.json').exists(),'Already frozen; no overwrite'
parents=json.loads((D/'native-parent-audit.json').read_text())['parents']
for p in parents:assert sha(R/p['source'])==p['sha256']and sha(R/p['glb'])==p['glb_sha256']
for mode,cnt in [('gray',3),('preview',2),('final',4)]:
 d=json.loads((O/(mode+'-render-report.json')).read_text());assert len(d['views'])==cnt and d['source_sha256']==sha(H/(K+'.blend'))and d['protocol_sha256']==sha(H/'compose.py')
 for v in d['views']:assert sha(O/v['png'])==v['PNG_sha256']and sha(O/v['exr'])==v['EXR_sha256']and v['samples']==(96 if mode=='final'else 16)
for name in ['gray-read.json','preview-read.json','final-read.json']:assert json.loads((O/name).read_text())['actually_read']
parity=json.loads((O/'native-glb-parity.json').read_text());assert len(parity['objects'])==3 and parity['native_sha256']==sha(H/(K+'.blend'))and parity['glb_sha256']==sha(H/(K+'-inspection.glb'))
gaps=json.loads((D/'native-context-and-gap-read.json').read_text());assert all(x['actual_triangle_surface_intersection_pairs']==0 for x in gaps['pairs'])
rays=json.loads((D/'feature-axis-ray-check.json').read_text());assert all(x['actual_axis_ray_clear_in_own_mesh']for x in rays['sources'])
coord=json.loads((O/'native-reopen-check.json').read_text());assert coord['parent_count']==1 and coord['parents'][0]['visible_geometry_objects']==3 and coord['source_sha256']==sha(H/'coord-exemplar.blend')
engine=json.loads((O/'inspection-v3/engine-check.json').read_text());assert all(sha(R/e['path'])==e['sha256']for e in engine['exports']);assert engine['capture_tool_sha256']==sha(D/'capture-engine.py')
f=json.loads((O/'catalog-fragment.json').read_text());assert all(k in f for k in ['component_id','package','source','files','review']);assert sha(R/f['source'])==f['source_sha256']and f['new_physical_ids']==0
(O/'coordination-contract-check.json').write_text(json.dumps({'fragment_fields_and_render_paths_valid':True,'stock_native_checker_passed':True,'source_direct_visible_meshes':3,'one_unit_context':True,'zero_new_physical_ids':True,'original_parents_once':True,'mounted_frame_and_fit_qualified':False},indent=2)+'\n')
paths=[p for folder in [H,D,O]for p in folder.rglob('*')if p.is_file()and '__pycache__'not in p.parts and p.name not in ['delivery.json','delivery-frozen.json']]
for p in parents:
 base=(R/p['source']).parent;paths.extend(base/n for n in ['child-candidate.blend','child-candidate.glb','parameters.json'])
paths=sorted(set(paths));entries=[dict(path=str(p.relative_to(R)),bytes=p.stat().st_size,sha256=sha(p))for p in paths]
d={'schema':1,'kind':'reused_single_LH_passenger_exterior_unit','authorization':'Coordinator dispatch within user-authorized autonomous motorcycle completion','files':entries,'file_count':len(entries),'unit_context_count':1,'existing_parent_count':3,'new_physical_ids':0,'physical_count_increment':0,'historical_sources_unchanged':True,'JK_standalone_freeze_unchanged':'c3aac54ee0f170925f366a1636da37e90c382bd8da8fec21a62088798b52de36','main_source':f['source'],'main_collection':f['collection'],'root':f['root'],'all_poses_rigid_positive_determinant':True,'original_materials_preserved':True,'gray3_material2_native96x4_actually_read':True,'independent_neutral_FLOAT32_raw_and_hinge_macro':True,'source_glb_accessors_and_actual_native_import_parity_verified':True,'stock_coord_checker_passed':True,'display_hole_axis_offset_m':.005,'rubber_nominal_overhang_m':.022,'diagnostic_rubber_cut_not_actual_slot':True,'world_mounting_not_assigned':True,'frame_or_shock_attachment_not_qualified':True,'fit_qualified':False,'art_accepted':False,'package_complete':False,'g8':False,'mutable_ledgers_catalogues_excluded':True}
b=(json.dumps(d,indent=2)+'\n').encode()
for name in ['delivery.json','delivery-frozen.json']:(O/name).write_bytes(b)
for e in entries:assert sha(R/e['path'])==e['sha256']
# Verify standalone JK freeze still byte-exact, not merely its three referenced source inputs.
jko=R/'creative/reviews/passenger-footrest-rubber-jk113008-v1/delivery-frozen.json';assert sha(jko)==d['JK_standalone_freeze_unchanged']
for e in json.loads(jko.read_text())['files']:assert sha(R/e['path'])==e['sha256']
print(json.dumps({'delivery':str((O/'delivery-frozen.json').relative_to(R)),'files':len(entries),'sha256':sha(O/'delivery-frozen.json'),'bytes':sum(e['bytes']for e in entries),'source_sha256':sha(H/(K+'.blend')),'glb_sha256':sha(H/(K+'-inspection.glb')),'JK119frozen_files_still_exact':True}))
