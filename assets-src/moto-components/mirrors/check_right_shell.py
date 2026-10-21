"""Read-only RH shell actual passage, closure and positive evaluated triangle test."""
import bpy,bmesh,json,hashlib,sys,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/mirror-right-v1';source=HERE/'mirror-right-shell-study-v1.blend';j=json.loads((OUT/'shell-study-v1-check.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(source)==j['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));o=bpy.data.objects['RH mirror compound shell and socket - candidate'];m=o.data;m.calc_loop_triangles();areas=[(m.vertices[t.vertices[1]].co-m.vertices[t.vertices[0]].co).cross(m.vertices[t.vertices[2]].co-m.vertices[t.vertices[0]].co).length/2 for t in m.loop_triangles];assert min(areas)>0
C=Vector(j['head_frame_world']['centre_m']);U=Vector(j['head_frame_world']['outward_U']);V=Vector(j['head_frame_world']['up_V']);N=Vector(j['head_frame_world']['normal_toward_rider_N']);point=lambda u,v,d:C+U*u+V*v+N*d;t=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(t.vertices)for t in m.loop_triangles],all_triangles=True)
p=json.loads((HERE/'parameters-right.json').read_text());u,v=p['observed_small_hole']['position_local_uv_working_m'];r=p['observed_small_hole']['radius_working_m'];centre=t.ray_cast(point(u,v,-.055),N,.055)[0];around=[]
for k in range(8):
 a=k*math.tau/8;hit=t.ray_cast(point(u+math.cos(a)*r*1.7,v+math.sin(a)*r*1.7,-.055),N,.055)[0];around.append({'angle_deg':k*45,'wall_present':hit is not None,'first_hit_local_depth_m':(hit-C).dot(N)if hit is not None else None})
centre_depth=(centre-C).dot(N)if centre is not None else None
# The opening leads into the head cavity, whose farther neck surface may still be hit.
# Do not incorrectly require an unobstructed ray through the complete hollow head.
rear_depth=max(x['first_hit_local_depth_m']for x in around if x['wall_present']);clear_depth=(centre_depth-rear_depth)if centre_depth is not None else None
assert all(x['wall_present']for x in around)and(centre_depth is None or clear_depth>.005),'Rear wall opening absent or insufficiently clear in actual model'
report={'source_sha256':j['source_sha256'],'export_sha256':j['export_sha256'],'triangles':len(areas),'min_triangle_area_m2':min(areas),'exact_zero_area_triangles':sum(a==0 for a in areas),'actual_rear_hole_centre_ray_first_hit_local_depth_m':centre_depth,'ray_clear_depth_beyond_adjacent_rear_wall_m':clear_depth,'opening_model_clear_into_cavity':centre_depth is None or clear_depth>.005,'farther_interior_surface_may_be_hit':True,'adjacent_rear_wall_rays':around,'hole_function_dimensions_and_RDC_applicability':'unknown; local placement and radius estimated','art_accepted':False};(OUT/'shell-shape-check.json').write_text(json.dumps(report,indent=2)+'\n');assert sha(source)==j['source_sha256'];print('RH_SHELL_CHECK',json.dumps(report))
