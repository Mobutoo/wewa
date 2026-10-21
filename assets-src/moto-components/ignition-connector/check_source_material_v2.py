"""Reopen the actual saved material source and prove its protected mesh/matrices."""
from pathlib import Path
import bpy,json,hashlib,sys,array
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/ignition-connector-v2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
B=json.loads((H/'build-report-v2.json').read_text());source=H/'ignition-connector-v2.blend';assert sha(source)==B['source_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source));o=bpy.data.objects[B['geometry'][0]['name']];m=o.data;m.calc_loop_triangles();d={}
for name,seq,key,n in [('positions',m.vertices,'co',3),('corner_normals',m.corner_normals,'vector',3)]:
    a=array.array('f',[0.]*(len(seq)*n));seq.foreach_get(key,a);d[name]=hashlib.sha256(a.tobytes()).hexdigest()
d['UV']=[]
for layer in m.uv_layers:
    a=array.array('f',[0.]*(len(layer.data)*2));layer.data.foreach_get('uv',a);d['UV'].append(hashlib.sha256(a.tobytes()).hexdigest())
d['indices']=hashlib.sha256(array.array('I',[i for t in m.loop_triangles for i in t.vertices]).tobytes()).hexdigest();d['object_matrix']=[list(q)for q in o.matrix_world];d['root_matrix']=[list(q)for q in o.parent.matrix_world]
assert d==B['source_protected_geometry_signatures'], 'Saved source changed protected geometry or matrices'
assert not bpy.data.libraries and not [i for i in bpy.data.images if i.source=='FILE']
sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import check_mesh
geometry=[check_mesh(o)];p=o.data.materials[0].node_tree.nodes['Principled BSDF']
assert not p.inputs['Normal'].is_linked and not p.inputs['Base Color'].is_linked
r={**B,'geometry':geometry,'source_libraries':0,'source_file_images':0,'actual_reopened_source_geometry_normals_UV_indices_matrices_protected':True,'conditional_interfaces_inherited_without_geometry_or_matrix_change':True}
(O/'source-geometry-check-v2.json').write_text(json.dumps(r,indent=2)+'\n');(O/'source-geometry-check.json').write_text(json.dumps(r,indent=2)+'\n');assert sha(source)==B['source_sha256'];print('SAVED_CONNECTOR_MATERIAL_SOURCE_PROTECTED')
