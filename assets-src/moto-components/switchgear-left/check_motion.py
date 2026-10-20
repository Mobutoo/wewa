"""Read-only geometric control travel inspection, not electrical qualification."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Matrix,Quaternion,Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/switchgear-left-v1';path=HERE/'switchgear-left-v1.blend'
bpy.ops.wm.open_mainfile(filepath=str(path));report=json.loads((OUT/'source-geometry-check.json').read_text());assert report['source_sha256']==hashlib.sha256(path.read_bytes()).hexdigest()
I=Vector(report['datum']['inward_axis']);T=Vector(report['datum']['thumb_side_radial'])
body=[o for o in bpy.data.collections['WEWA_SWITCHGEAR_LEFT'].objects if o.type=='MESH' and 'shell - editable' in o.name]
def tree(o):
 deps=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(deps);m=e.to_mesh();result=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);e.to_mesh_clear();return result
trees=[tree(o) for o in body];checks=[]
for c in report['controls']:
 obj=bpy.data.objects[c['object']];pivot=obj.parent;position=Vector(c['pivot_world_m']);poses=[('rest',Matrix.Translation(position))]
 if 'rotation_degrees' in c['travel_estimated']:
  for angle in c['travel_estimated']['rotation_degrees']:poses.append((str(angle)+'degrees',Matrix.Translation(position)@Quaternion(I,math.radians(angle)).to_matrix().to_4x4()))
 if 'slide_metres' in c['travel_estimated']:
  for delta in c['travel_estimated']['slide_metres']:poses.append((str(delta)+'m slide',Matrix.Translation(position+I*delta)))
 if 'push_metres' in c['travel_estimated']:poses.append(('push',Matrix.Translation(position-T*c['travel_estimated']['push_metres'])))
 for name,transform in poses:
  pivot.matrix_world=transform;bpy.context.view_layer.update();control=tree(obj);crossings=[len(control.overlap(t)) for t in trees];checks.append({'object':obj.name,'pose':name,'shell_triangle_crossings':crossings})
 pivot.matrix_world=Matrix.Translation(position);bpy.context.view_layer.update()
result={'source_sha256':report['source_sha256'],'scope':'Actual rigid source surfaces at explicit working review travels; no contact-pressure, detent, electrical or ergonomic certification','poses':checks,'all_clear':not any(any(c['shell_triangle_crossings']) for c in checks),'travel_measured':False,'art_accepted':False};(OUT/'motion-check.json').write_text(json.dumps(result,indent=2)+'\n');print('WEWA_LH_MOTION',json.dumps(result));assert result['all_clear'],result
