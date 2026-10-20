"""Read-only intended planar-pocket source normals, separate from visual acceptance."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/switchgear-left-v1';path=HERE/'switchgear-left-v1.blend';digest=hashlib.sha256(path.read_bytes()).hexdigest();assert digest==json.loads((OUT/'source-geometry-check.json').read_text())['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(path))
E=Vector((.34,.085,.105));I=Vector((-.195,-.085,0)).normalized();T=I.cross(Vector((0,0,1)));angles=[];faces=0
for o in bpy.data.collections['WEWA_SWITCHGEAR_LEFT'].objects:
 if o.type!='MESH' or 'shell - editable' not in o.name:continue
 m=o.data;m.update()
 for f in m.polygons:
  c=f.center-E;q=c.dot(I);v=c.dot(T);z=c.z
  if .123<q<.149 and -.016<z<-.0015 and abs(v-.0247)<.000001 and f.normal.dot(T)>.9999:
   faces+=1
   for li in f.loop_indices:angles.append(math.degrees(math.acos(max(-1,min(1,m.corner_normals[li].vector.dot(f.normal))))))
report={'source_sha256':digest,'scope':'Normals on intentionally planar rectangular selector pocket floor only. Excludes curved lips by plane and face-normal filtering. No dimensional/photo fidelity certification.','plane_v_m':.0247,'triangles':faces,'corner_normal_deviation_max_degrees':max(angles),'mean_degrees':sum(angles)/len(angles),'working_flat_face_quality_threshold_degrees':1,'passed':faces>0 and max(angles)<1,'art_accepted':False}
(OUT/'planar-surface-normal-check.json').write_text(json.dumps(report,indent=2)+'\n');assert report['passed'],report
