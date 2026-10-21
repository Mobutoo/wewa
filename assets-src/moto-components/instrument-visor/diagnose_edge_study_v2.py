"""Read-only source diagnostic after visually rejected perimeter-bevel preview."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/instrument-visor-shell-study-v2';source=HERE/'instrument-visor-shell-study-v2.blend';digest=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(HERE/'instrument-visor-shell-study-v1.blend'));old=bpy.data.objects['Visor finite curved shell - conditional estimated study'];coords={tuple(v.co)for v in old.data.vertices};bpy.ops.wm.open_mainfile(filepath=str(source));ob=bpy.data.objects['Visor finite curved shell - conditional estimated study'];j=json.loads((OUT/'source-geometry-check.json').read_text());U=Vector(j['frame']['U']);V=Vector(j['frame']['up_V']);N=Vector(j['frame']['front_N']);origin=Vector(j['frame']['origin_m']);k=.040/.125**2;h=.0025/2;corners=ob.data.corner_normals;angles=[];signed=[]
def nearest(co):
 rel=co-origin;a=rel.dot(U);t=rel.dot(V);c=rel.dot(N);x=a
 for _ in range(8):x-=(x-a+2*k*x*(k*x*x+c))/(1+6*k*k*x*x+2*k*c)
 n=(N+U*(2*k*x)).normalized();p=origin+U*x+V*t-N*k*x*x;return n,(co-p).dot(n)
for vertex in ob.data.vertices:
 n,d=nearest(vertex.co);signed.append(d)
for f in ob.data.polygons:
 for li in f.loop_indices:
  co=ob.data.vertices[ob.data.loops[li].vertex_index].co
  if tuple(co)not in coords:continue
  n,d=nearest(co)
  if abs(abs(d)-h)>2e-6:continue
  actual=corners[li].vector;expected=n if d>0 else-n;angles.append(math.degrees(math.acos(max(-1,min(1,actual.dot(expected))))))
ob.data.calc_loop_triangles();triangles=[tuple(t.vertices)for t in ob.data.loop_triangles];tree=BVHTree.FromPolygons([v.co for v in ob.data.vertices],triangles,all_triangles=True);pairs=tree.overlap(tree);nonadj=[(a,b)for a,b in pairs if a<b and not set(triangles[a])&set(triangles[b])];report={'source_sha256':digest,'visible_rejection':'Triangular dark/bright spikes in macro near the curved lower relief; 123 actual UV triangles also degenerate. Technical closure/volume alone did not catch appearance.','retained_front_back_corner_samples':len(angles),'max_normal_angle_error_deg':max(angles),'normal_angle_over5deg':sum(a>5 for a in angles),'signed_distance_from_analytic_midsurface_m_range':[min(signed),max(signed)],'vertices_outside_original_half_thickness_by2um':sum(abs(d)>h+2e-6 for d in signed),'nonadjacent_triangle_BVH_candidates':len(nonadj),'first_candidate_triangle_pairs':nonadj[:20],'BVH_limit':'Candidate overlap is not a robust exact self-intersection classifier; coplanarity/contact may be included.','source_modified':False,'art_accepted':False};(OUT/'edge-rejection-diagnostic.json').write_text(json.dumps(report,indent=2)+'\n');assert hashlib.sha256(source.read_bytes()).hexdigest()==digest;print('EDGE_REJECT_DIAGNOSTIC',report)
