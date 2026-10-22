"""Independent evaluated native per-instance bounds for comparing assembled glTF placements."""
import bpy,json,sys,hashlib,numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];rev=sys.argv[sys.argv.index('--')+1];O=R/'creative/reviews'/rev;report=json.loads((O/'linked-parents-check.json').read_text());assert Path(bpy.data.filepath).resolve()==(R/report['source']).resolve();bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();rows=[]
def read(col,M,chain=()):
 assert col.as_pointer()not in chain
 for ob in col.all_objects:
  if ob.hide_render:continue
  W=M@ob.matrix_world
  if ob.type=='MESH':
   ev=ob.evaluated_get(dg);me=ev.to_mesh();vs=np.empty((len(me.vertices),3),dtype=np.float32);me.vertices.foreach_get('co',vs.ravel());N=np.array(W,dtype=np.float64);pts=vs@N[:3,:3].T+N[:3,3];tri=sum(len(p.vertices)-2 for p in me.polygons);ev.to_mesh_clear()
   if len(pts):yield pts.min(axis=0),pts.max(axis=0),len(pts),tri
  elif ob.instance_type=='COLLECTION'and ob.instance_collection:
   yield from read(ob.instance_collection,W@Matrix.Translation(-ob.instance_collection.instance_offset),chain+(col.as_pointer(),))
for row in report['parents']:
 ob=bpy.data.objects['COVERAGE_PARENT ['+row['key']+']'];parts=list(read(ob.instance_collection,ob.matrix_world@Matrix.Translation(-ob.instance_collection.instance_offset)));assert parts
 lo=np.min([p[0]for p in parts],axis=0);hi=np.max([p[1]for p in parts],axis=0);rows.append(dict(key=row['key'],bounds_native=[lo.tolist(),hi.tolist()],bounds_gltf=[[float(lo[0]),float(lo[2]),float(-hi[1])],[float(hi[0]),float(hi[2]),float(-lo[1])]],vertices=sum(p[2]for p in parts),triangles=sum(p[3]for p in parts),source=row['source'],sha256=row['sha256']))
(O/'native-evaluated-bounds.json').write_text(json.dumps(dict(source=report['source'],source_sha256=hashlib.sha256((R/report['source']).read_bytes()).hexdigest(),scope='Actual evaluated native mesh world bounds and triangle counts; not art/fit or silhouette acceptance',parents=rows),indent=2)+'\n');print('NATIVE_WORLD_BOUNDS',len(rows))
