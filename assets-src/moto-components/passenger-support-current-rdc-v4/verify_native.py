import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[2]
bpy.ops.wm.open_mainfile(filepath=str(O/'context-material-linked.blend'));parts=list(bpy.data.collections['CURRENT_RDC_PASSENGER_SUPPORT_V4'].objects);rows=[];dg=bpy.context.evaluated_depsgraph_get()
for ob in parts:
 assert ob.type=='MESH';ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();rows.append({'key':ob.name,'vertices':len(me.vertices),'triangles':len(me.loop_triangles),'matrix_world':[list(r)for r in ob.matrix_world],'determinant':ob.matrix_world.to_3x3().determinant(),'mesh_library':bpy.path.abspath(ob.data.library.filepath)if ob.data.library else None,'materials_linked_unchanged':all(m.library is not None for m in ob.data.materials)});ev.to_mesh_clear()
assert len(rows)==8 and all(r['mesh_library']and abs(r['determinant']-1)<1e-5 and r['materials_linked_unchanged']for r in rows)
frag=json.loads((O/'integration-fragment.json').read_text());sources=[]
for r in frag['additions']:
 p=R/r['source'];actual=hashlib.sha256(p.read_bytes()).hexdigest();assert actual==r['sha256'];sources.append({'path':r['source'],'sha256':actual,'unchanged':True})
(O/'native-reopen-check.json').write_text(json.dumps({'parts':rows,'count':len(rows),'triangles':sum(r['triangles']for r in rows),'sources':sources,'scope':'Eight actual reopened linked meshes, proper rigid matrices and original material datablocks; photo-inferred visible cuts, no mechanical mount or G8 certification.'},indent=2));print('NATIVE_PASS',len(rows),sum(r['triangles']for r in rows))
