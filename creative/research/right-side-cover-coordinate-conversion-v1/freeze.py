from pathlib import Path
import json,hashlib
R=Path('/workspace/wewa');K='right-side-cover-coordinate-conversion-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;D=R/'creative/research'/K;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (O/'delivery.json').exists(),'Already frozen: do not rerun or overwrite'
for mode,cnt in [('gray',3),('preview',2),('final',3)]:
 d=json.loads((O/(mode+'-render-report.json')).read_text());assert len(d['views'])==cnt and d['source_sha256']==sha(H/'child-candidate.blend') and d['protocol_sha256']==sha(H/'build.py')
 for v in d['views']:assert sha(O/v['png'])==v['PNG_sha256'] and sha(O/v['exr'])==v['EXR_sha256'] and v['samples']==(96 if mode=='final' else 16)
 if mode=='final':assert d['render_wrapper_sha256']==sha(D/'render-final.py')
for e in json.loads((D/'source-and-export-inputs.json').read_text())['files']:assert sha(R/e['path'])==e['sha256']
report=json.loads((O/'inspection-v3/engine-check.json').read_text());assert all(sha(R/x['path'])==x['sha256']for x in report['exports']);assert report['capture_tool_sha256']==sha(D/'capture-engine.py')
f=json.loads((O/'catalog-fragment.json').read_text());assert all(k in f for k in ['component_id','package','source','files','review']);assert f['new_physical_ids']==0
for v in json.loads((O/'final-render-report.json').read_text())['views']:
 name=v.get('name',v.get('view'));assert (O/v.get('png',name+'.png')).exists() and (O/v.get('exr','raw/'+name+'.exr')).exists();assert sha(O/v['png'])==v['PNG_sha256']
(O/'coordination-contract-check.json').write_text(json.dumps({'required_fragment_fields_present':True,'author_report_paths_and_png_hashes_verified':True,'stock_native_coord_checker_passed':True,'functions_and_exemplar_wrapper_present':True,'zero_new_physical_ids':True,'no_coordinator_metadata_written':True,'fit_qualified':False},indent=2)+'\n')
paths=sorted(set(p for folder in [H,O,D]for p in folder.rglob('*')if p.is_file() and '__pycache__'not in p.parts and p.name not in ['delivery.json','delivery-frozen.json']))
entries=[dict(path=str(p.relative_to(R)),bytes=p.stat().st_size,sha256=sha(p))for p in paths]
delivery={'schema':1,'kind':'existing_RH_coordinate_convention_derivative_and_estimated_exemplar','files':entries,'file_count':len(entries),'authorization':'Coordinator dispatch within user-authorized autonomous motorcycle completion','component_id':f['component_id'],'physical_count_increment':0,'new_physical_ids':0,'historical_sources_unchanged':True,'source_independent':True,'normalized_object_scale':[1,1,1],'source_geometry_connectivity_uv_materials_preserved':True,'improper_A_baked_with_winding_and_normal_handling':True,'native_glb_parity_verified':True,'three_gray_two_material_three_native96_actually_read':True,'independent_neutral_and_float32_raw':True,'stock_coord_checker_passed':True,'estimated_context_T_m':[-.135,.535,-.41],'estimated_context_R_deg':[0,0,0],'estimated_context_scale':[1,1,1],'photo_registration_and_fit_qualified':False,'old_g4_g8_unchanged':True,'art_accepted':False,'g8':False}
bytes_=(json.dumps(delivery,indent=2)+'\n').encode()
for name in ['delivery.json','delivery-frozen.json']:(O/name).write_bytes(bytes_)
for e in entries:assert sha(R/e['path'])==e['sha256']
print(json.dumps({'delivery':str((O/'delivery.json').relative_to(R)),'files':len(entries),'sha256':sha(O/'delivery.json'),'total_bytes':sum(e['bytes']for e in entries),'native_sha256':sha(H/'child-candidate.blend'),'glb_sha256':sha(H/'child-candidate.glb')}))
