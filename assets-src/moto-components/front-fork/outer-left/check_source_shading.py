"""Read freshly generated source normals; no source or buffer modification."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/fork-outer-left-v1';P=json.loads((HERE/'parameters.json').read_text());source=HERE/'fork-outer-left-v1.blend';bpy.ops.wm.open_mainfile(filepath=str(source));o=list(bpy.data.collections['WEWA_FORK_OUTER_LEFT_ISOLATED'].objects)[0];m=o.data;m.update();bore=[];planes=[]
def error(n,expected):return math.degrees(math.atan2(n.cross(expected).length,n.dot(expected)))
for f in m.polygons:
 if all(abs(math.hypot(m.vertices[k].co.y,m.vertices[k].co.z)-P['axle_bore_diameter_working_m']/2)<1e-7 for k in f.vertices):
  for li in f.loop_indices:
   v=m.vertices[m.loops[li].vertex_index].co;n=m.corner_normals[li].vector;bore.append(error(n,Vector((0,-v.y,-v.z)).normalized()))
 if not f.use_smooth:
  for li in f.loop_indices:planes.append(error(m.corner_normals[li].vector,f.normal))
r={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'custom_normals_present':m.has_custom_normals,'method':'atan2 of cross and dot against analytical radial bore normal; flat loops against polygon normal','bore_corner_samples':len(bore),'maximum_bore_radial_normal_error_degrees':max(bore),'flat_corner_samples':len(planes),'maximum_flat_face_normal_error_degrees':max(planes),'source_or_GLb_modified':False,'bore_polygon_segments':160,'bore_half_sector_angle_degrees':180/160,'comparison_limit_degrees':180/160+.03,'limit_reason':'Boolean intersections can add vertices inside original cylindrical polygon facets; radial-circle difference is bounded by half a polygon sector, not an OEM tolerance','manufacturing_accuracy_claimed':False,'art_accepted':False};assert not m.has_custom_normals and len(bore)>=500 and max(bore)<180/160+.03 and max(planes)<.02,r;(OUT/'source-shading-check.json').write_text(json.dumps(r,indent=2)+'\n');print('WEWA_SOURCE_SHADING',json.dumps(r))
