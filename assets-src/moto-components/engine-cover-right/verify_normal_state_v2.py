from pathlib import Path
import bpy,json,hashlib,numpy as np
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-cover-right-v2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(path,clear=False):
 bpy.ops.wm.open_mainfile(filepath=str(path));o=bpy.data.objects['RH clutch cover hollow casting - editable candidate'];m=o.data
 if clear:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.mesh.customdata_custom_splitnormals_clear();m.update()
 normals=np.array([list(n.vector) for n in m.corner_normals],dtype=np.float32);co=np.empty(len(m.vertices)*3,dtype=np.float32);m.vertices.foreach_get('co',co);p=m.materials[0].node_tree.nodes.get('Principled BSDF');material=[list(p.inputs['Base Color'].default_value),p.inputs['Metallic'].default_value,p.inputs['Roughness'].default_value];lights=sorted([{'name':o.name,'matrix':[list(row) for row in o.matrix_world],'power':o.data.energy,'color':list(o.data.color),'size':o.data.size} for o in bpy.context.scene.objects if o.type=='LIGHT'],key=lambda r:r['name']);return normals,co,material,lights
old=H/'engine-cover-right-v1.blend';new=H/'engine-cover-right-v2.blend';expected=read(old,True);actual=read(new);assert np.array_equal(expected[0],actual[0]) and np.array_equal(expected[1],actual[1]) and expected[2:]==actual[2:]
j={'base_source_sha256':sha(old),'new_source_sha256':sha(new),'explicit_v2_state_equals_v1_after_diagnostic_normal_clear':True,'corner_normal_float32_sha256':hashlib.sha256(actual[0].tobytes()).hexdigest(),'positions_bit_identical':True,'visible_PBR_parameters_identical':True,'studio_lights_identical':True,'diagnostic8_views_scope':'Rendered from v1 with this exact in-memory normal correction, not renamed as v2 renders; actualv2 final96 remains separate','art_accepted':False};(O/'normal-state-equivalence.json').write_text(json.dumps(j,indent=2)+'\n');print('WEWA_EQUIVALENCE',json.dumps(j))
