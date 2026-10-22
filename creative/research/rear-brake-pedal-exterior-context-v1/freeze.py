from pathlib import Path
import json,hashlib
R=Path('/workspace/wewa');K='rear-brake-pedal-exterior-context-v1';D=R/'creative/research'/K;H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (O/'delivery.json').exists(),'Already frozen; do not overwrite'
parents=json.loads((D/'parent-native-read.json').read_text())['parents']
for p in parents:assert sha(R/p['source'])==p['sha256'] and sha(R/p['glb'])==p['glb_sha256']
for mode,cnt in [('gray',3),('preview',2),('final',3)]:
 d=json.loads((O/(mode+'-render-report.json')).read_text());assert len(d['views'])==cnt and d['source_sha256']==sha(H/(K+'.blend')) and d['protocol_sha256']==sha(H/'compose.py')
 for v in d['views']:assert sha(O/v['png'])==v['PNG_sha256'] and sha(O/v['exr'])==v['EXR_sha256'] and v['samples']==(96 if mode=='final' else 16)
engine=json.loads((O/'inspection-v3/engine-check.json').read_text());assert all(sha(R/x['path'])==x['sha256']for x in engine['exports']);assert engine['capture_tool_sha256']==sha(D/'capture-engine.py')
parity=json.loads((O/'native-glb-parity.json').read_text());assert len(parity['objects'])==4 and parity['native_sha256']==sha(H/(K+'.blend')) and parity['glb_sha256']==sha(H/(K+'-inspection.glb'))
wrapper=json.loads((D/'integration-wrapper-equivalence.json').read_text());assert wrapper['sha256']==sha(H/'integration-wrapper.blend') and len(wrapper['objects'])==4
coord=json.loads((O/'native-reopen-check.json').read_text());assert coord['parent_count']==1 and coord['parents'][0]['visible_geometry_objects']==4 and coord['source_sha256']==sha(H/'coord-exemplar.blend')
f=json.loads((O/'catalog-fragment.json').read_text());assert all(k in f for k in ['component_id','package','source','files','review']);assert f['source_sha256']==sha(R/f['source'])
(O/'coordination-contract-check.json').write_text(json.dumps({'required_fragment_fields_and_author_report_paths_valid':True,'author_native_vs_main_native_equivalence_report':str((D/'integration-wrapper-equivalence.json').relative_to(R)),'stock_checker_actual_reopen_passed':True,'main_collection_direct_visible_meshes':4,'zero_new_physical_ids':True,'parked_pad_not_mounted':True,'world_translation_not_assigned':True,'fit_qualified':False},indent=2)+'\n')
paths=[p for folder in [H,D,O]for p in folder.rglob('*')if p.is_file()and '__pycache__'not in p.parts and p.name not in ['delivery.json','delivery-frozen.json']]
for p in parents:
 base=(R/p['source']).parent;paths.extend(base/n for n in ['child-candidate.blend','child-candidate.glb','parameters.json'])
paths=sorted(set(paths));entries=[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in paths]
d={'schema':1,'kind':'existing_four_parent_local_exterior_context','authorization':'Coordinator dispatch within user-authorized autonomous motorcycle completion','files':entries,'file_count':len(entries),'new_physical_ids':0,'physical_count_increment':0,'historical_sources_unchanged':True,'four_existing_parents_once':True,'geometry_and_original_materials_unchanged':True,'main_source':f['source'],'main_collection':f['collection'],'root':f['root'],'source_rigid_matrices':'creative/research/'+K+'/native-links-and-transforms.json','gray3_material2_native96x3_actually_read':True,'independent_neutral_FLOAT32_raw':True,'actual_native_glb_oriented_triangle_parity_verified':True,'stock_coord_checker_passed':True,'parked_pad_original_face_study_not_mounted':True,'rod_and_clevis_excluded':True,'world_translation_unknown':True,'Q_convention_only_EulerXYZ_deg':[90,0,-90],'fit_qualified':False,'variant':'PF161002 related product; current RDC125 mounting unconfirmed','old_g4_g8_unchanged':True,'art_accepted':False,'g8':False,'mutable_ledgers_catalogs_and_caches_excluded':True}
b=(json.dumps(d,indent=2)+'\n').encode()
for n in ['delivery.json','delivery-frozen.json']:(O/n).write_bytes(b)
for e in entries:assert sha(R/e['path'])==e['sha256']
print(json.dumps({'delivery':str((O/'delivery-frozen.json').relative_to(R)),'files':len(entries),'sha256':sha(O/'delivery-frozen.json'),'bytes':sum(e['bytes']for e in entries),'main_source_sha256':sha(R/f['source']),'glb_sha256':sha(H/(K+'-inspection.glb'))}))
