import bpy,json,hashlib
from pathlib import Path
R=Path('/workspace/wewa');P=R/'assets-src/moto-components/kickstarter/kickstarter-v2.blend';D=R/'creative/research/kickstarter-exterior-context-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(P);bpy.ops.wm.open_mainfile(filepath=str(P));bpy.context.view_layer.update();rows=[]
for ob in bpy.data.collections['WEWA_KICKSTARTER'].all_objects:
 rows.append({'name':ob.name,'type':ob.type,'parent':ob.parent.name if ob.parent else None,'matrix_world_rows':[list(r)for r in ob.matrix_world],'matrix_parent_inverse_rows':[list(r)for r in ob.matrix_parent_inverse],'mesh_vertices':len(ob.data.vertices)if ob.type=='MESH'else None,'mesh_polygons':len(ob.data.polygons)if ob.type=='MESH'else None})
assert sha(P)==before;(D/'parent-native-read.json').write_text(json.dumps({'source':str(P.relative_to(R)),'source_sha256':before,'actually_opened_and_evaluated':True,'source_not_saved':True,'objects':rows},indent=2));print('ACTUAL_PARENT_READ',len(rows))
