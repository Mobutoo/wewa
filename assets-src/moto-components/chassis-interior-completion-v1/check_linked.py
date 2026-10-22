import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(O/'kit-linked-v2.blend'));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();rows=[]
for inst in dg.object_instances:
 if inst.is_instance and inst.object.type=='MESH'and not inst.object.hide_render:
  ob=inst.object;m=ob.to_mesh();m.calc_loop_triangles();rows.append({'name':ob.name,'triangles':len(m.loop_triangles),'matrix_world':[list(v)for v in inst.matrix_world]});ob.to_mesh_clear()
lib=[]
for l in bpy.data.libraries:
 p=Path(bpy.path.abspath(l.filepath));lib.append({'path':str(p),'exists':p.exists(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()if p.exists()else None})
r={'linked_mesh_instances':len(rows),'triangles':sum(x['triangles']for x in rows),'all_libraries_present':all(x['exists']for x in lib),'instances':rows,'libraries':lib,'scope':'Native linked kit reopened, depsgraph evaluated; artistic/installed fit not accepted'};assert r['all_libraries_present'];assert r['triangles']==2356464,(r['triangles'],len(rows));(O/'linked-reopen-check.json').write_text(json.dumps(r,indent=2));print('LINKED_PASS',len(rows),r['triangles'])
