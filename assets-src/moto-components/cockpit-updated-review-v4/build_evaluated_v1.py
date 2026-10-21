"""Static read-only composition: exact current candidate sources, no repair or new part."""
from pathlib import Path
import bpy,json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/cockpit-updated-review-v4';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not(H/'preflight-manifest.json').exists()
rows=json.loads((R/'creative/reviews/cockpit-current-review-v3/source-geometry-check.json').read_text())['linked_sources']
inputs=[]
for row in rows:
    row=dict(row)
    if row['asset']=='cockpit-cables-v2':
        B=json.loads((H.parent/'cockpit-cables/build-report-v3.json').read_text());row.update(asset='cockpit-cables-v3',source='assets-src/moto-components/cockpit-cables/cockpit-cables-v3.blend',sha256=B['source_sha256'])
    inputs.append({k:row[k]for k in['asset','source','sha256','source_collection']})
for folder,blend,collection,report in [('clutch-upper-sheath','clutch-upper-sheath-v1.blend','WEWA_CLUTCH_UPPER_SHEATH','build-report.json'),('front-brake-upper-sheath','front-brake-upper-sheath-v1.blend','WEWA_FRONT_BRAKE_UPPER_SHEATH','build-report.json'),('ignition-key-ring','ignition-key-ring-v1.blend','WEWA_IGNITION_KEY_RING','build-report.json'),('ignition-connector','ignition-connector-v2.blend','WEWA_IGNITION_CONNECTOR_HOUSING','build-report-v2.json')]:
    B=json.loads((H.parent/folder/report).read_text());inputs.append({'asset':folder,'source':f'assets-src/moto-components/{folder}/{blend}','sha256':B['source_sha256'],'source_collection':collection})
assert (H.parent/'ignition-connector/preflight-manifest-v2.json').is_file(), 'Finish and freeze connector2 first'
assert len(inputs)==18
for row in inputs:assert sha(R/row['source'])==row['sha256']
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
seen=[]
loaded=[]
for row in inputs:
    with bpy.data.libraries.load(str(R/row['source']),link=True,relative=True)as(a,l):l.collections=[row['source_collection']]
    c=l.collections[0];assert c is not None;s.collection.children.link(c);local=list(c.all_objects);assert all(o is not None for o in local)
    basis_before={o.name:([list(q)for q in o.matrix_basis],[list(q)for q in o.matrix_parent_inverse])for o in local}
    s.frame_set(1);bpy.context.view_layer.update()
    assert all(basis_before[o.name]==([list(q)for q in o.matrix_basis],[list(q)for q in o.matrix_parent_inverse])for o in local), 'Evaluation changed local transform data'
    row['local_basis_and_parent_inverse_unchanged_by_evaluation']=True
    loaded.append((row,c))
    row['mesh_objects']=sum(o.type=='MESH'for o in local)
    row['actual_rest_world_matrices']=[{'object':o.name,'matrix':[list(q)for q in o.matrix_world]}for o in local if o.type=='MESH']
    seen+=local
s.frame_set(1);bpy.context.view_layer.update()
for row,c in loaded:
    for o in c.all_objects:
        if o.type=='MESH':assert [list(q)for q in o.matrix_world]==next(q['matrix']for q in row['actual_rest_world_matrices']if q['object']==o.name)
libraries=[]
for lib in bpy.data.libraries:
    path=Path(bpy.path.abspath(lib.filepath));assert path.is_file();libraries.append({'path':str(path.relative_to(R))if path.is_relative_to(R)else str(path),'sha256':sha(path)})
    lib.filepath=bpy.path.relpath(str(path),start=str(H))
images=[]
for image in bpy.data.images:
    if image.source!='FILE':continue
    row={'name':image.name,'packed':bool(image.packed_file)}
    if not image.packed_file:
        path=Path(bpy.path.abspath(image.filepath,library=image.library));assert path.is_file();row.update(path=str(path.relative_to(R))if path.is_relative_to(R)else str(path),sha256=sha(path))
    images.append(row)
source=H/'cockpit-updated-review-v4.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
result={'kind':'Read-only static cockpit composition, no new physical type','source_sha256':sha(source),'linked_sources':inputs,'actual_libraries':libraries,'material_file_images':images,'builder':'assets-src/moto-components/cockpit-updated-review-v4/build_evaluated_v1.py','matrix_capture_protocol':'Evaluate each linked collection at source rest frame1 before reading world matrices; local basis/parent inverse unchanged. Prepared initial pre-evaluation identity caches were rejected and preserved.','pose_changes':[],'excluded':['incompatible M6','DS008/009/010 without datum'],'camera_is_estimated':True,'full_harness_created':False,'driver_added':False,'art_accepted':False,'physical_iphone_tested':False}
(O/'source-geometry-check.json').write_text(json.dumps(result,indent=2)+'\n')
for row in inputs:assert sha(R/row['source'])==row['sha256']
print('COMPOSITION_CURRENT18_EXACT',sha(source))
