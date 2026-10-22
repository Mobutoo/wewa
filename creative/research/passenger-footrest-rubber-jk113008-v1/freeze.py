from pathlib import Path
import json,hashlib
R=Path('/workspace/wewa');K='passenger-footrest-rubber-jk113008-v1';D=R/'creative/research'/K;H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (O/'delivery.json').exists(),'Already frozen, no overwrite'
for mode,cnt in [('gray',3),('preview',2),('final',4)]:
 d=json.loads((O/(mode+'-render-report.json')).read_text());p=H/('child-gray.blend'if mode=='gray'else'child-candidate.blend');assert len(d['views'])==cnt and d['source_sha256']==sha(p) and d['protocol_sha256']==sha(H/'build.py')
 assert d['helper_sha256']==sha(D/'protocol-snapshots/powertrain_completion_common_open_v1.py')
 for v in d['views']:assert sha(O/v['png'])==v['PNG_sha256']and sha(O/v['exr'])==v['EXR_sha256']and v['samples']==(96 if mode=='final'else 16)
for name in ['gray-review.json','preview-review.json','final-review.json']:assert json.loads((O/name).read_text())['actually_read']
parity=json.loads((O/'native-glb-parity.json').read_text());assert parity['native_sha256']==sha(H/'child-candidate.blend')and parity['glb_sha256']==sha(H/'child-candidate.glb')and len(parity['objects'])==1
exp=json.loads((O/'independent-export-check.json').read_text());assert exp['gray_material_attributes_normals_indices_identical']
engine=json.loads((O/'inspection-v3/engine-check.json').read_text());assert all(sha(R/e['path'])==e['sha256']for e in engine['exports']);assert engine['capture_tool_sha256']==sha(D/'capture-engine.py')
coord=json.loads((O/'native-reopen-check.json').read_text());assert coord['parent_count']==1 and coord['parents'][0]['visible_geometry_objects']==1 and coord['source_sha256']==sha(H/'coord-exemplar.blend')
f=json.loads((O/'catalog-fragment.json').read_text());assert f['source_sha256']==sha(R/f['source'])and f['new_physical_ids']==1
(O/'coordination-contract-check.json').write_text(json.dumps({'source_files_review_and_identity_fields_present':True,'functions_build_stage_and_single_exemplar_present':True,'stock_checker_actual_reopen_passed':True,'source_visible_mesh_count':1,'new_physical_ids':1,'physical_repetition_created':False,'root_catalogue_or_registry_written':False,'complete_sleeve_or_fit_qualified':False},indent=2)+'\n')
paths=sorted(set(p for folder in [H,O,D]for p in folder.rglob('*')if p.is_file()and '__pycache__'not in p.parts and p.name not in ['delivery.json','delivery-frozen.json']))
entries=[dict(path=str(p.relative_to(R)),bytes=p.stat().st_size,sha256=sha(p))for p in paths]
d={'schema':1,'kind':'single_original_passenger_visible_envelope_exemplar','authorization':'Coordinator dispatch within user-authorized autonomous motorcycle completion','package':'P16','component_id':'MOTO-PASSENGER-FOOTREST-RUBBER-001','part_code':'JK113008','files':entries,'file_count':len(entries),'physical_exemplar_count':1,'new_physical_ids':1,'driver_DF161413_reused_or_rebuilt':False,'historical_sources_unchanged':True,'source_independent':True,'near_collar_complete_after_pre_freeze_rework':True,'diagnostic_lower_body_omission_not_physical_slot':True,'full_inner_seat_and_retention_not_invented':True,'three_gray_two_material_four_native96_actually_read':True,'independent_neutral_FLOAT32_raw':True,'actual_native_glb_parity_verified':True,'stock_coord_checker_passed':True,'proposed_metal_integration':'conditional only; no relative transform or geometry forced to fit','fit_qualified':False,'full_underside_and_complete_sleeve_qualified':False,'art_accepted':False,'package_complete':False,'g8':False,'mutable_external_ledgers_catalogs_excluded':True,'rejected_pre_freeze_study_preserved_not_admitted':True}
b=(json.dumps(d,indent=2)+'\n').encode()
for name in ['delivery.json','delivery-frozen.json']:(O/name).write_bytes(b)
for e in entries:assert sha(R/e['path'])==e['sha256']
print(json.dumps({'delivery':str((O/'delivery-frozen.json').relative_to(R)),'files':len(entries),'sha256':sha(O/'delivery-frozen.json'),'bytes':sum(e['bytes']for e in entries),'source_sha256':sha(H/'child-candidate.blend'),'glb_sha256':sha(H/'child-candidate.glb')}))
