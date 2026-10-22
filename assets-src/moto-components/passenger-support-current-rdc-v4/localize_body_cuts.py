import bpy,json
from pathlib import Path
from mathutils.bvhtree import BVHTree
O=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(O/'context-material-linked.blend'));dg=bpy.context.evaluated_depsgraph_get()
def tree(ob,M):
 ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();v=[M@x.co for x in me.vertices];f=[tuple(t.vertices)for t in me.loop_triangles];ev.to_mesh_clear();return BVHTree.FromPolygons(v,f,all_triangles=True),v,f
parts=[o for o in bpy.context.scene.objects if o.type=='MESH'and 'CURRENT_RDC'in o.name];pts={o.name:tree(o,o.matrix_world)for o in parts};rows=[]
for ins in dg.object_instances:
 if not ins.is_instance or ins.object.type!='MESH'or ins.object.hide_render:continue
 b,v,f=tree(ins.object.original,ins.matrix_world)
 for ob in parts:
  pb,pv,pf=pts[ob.name];cross=pb.overlap(b)
  if cross:
   pp=[pv[k]for a,_ in cross for k in pf[a]];rows.append({'tube':ob.name,'collider':ins.object.name,'pairs':len(cross),'triangle_extent_m':[[min(p[i]for p in pp)for i in range(3)],[max(p[i]for p in pp)for i in range(3)]]})
(O/'body-cut-localization.json').write_text(json.dumps({'crossings':rows,'scope':'Actual intersection triangles localized; distinguishes source-observed cut near body from frame/SNS collisions. No geometry changed.'},indent=2));print(json.dumps(rows))
