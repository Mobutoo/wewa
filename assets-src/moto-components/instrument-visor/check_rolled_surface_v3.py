"""Actual source checks for defects observed in the rejected bevel study."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/instrument-visor-shell-study-v3';source=HERE/'instrument-visor-shell-study-v3.blend';j=json.loads((OUT/'source-geometry-check.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(source)==j['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));ob=bpy.data.objects[j['object']];U=Vector(j['frame']['U']);V=Vector(j['frame']['up_V']);N=Vector(j['frame']['front_N']);origin=Vector(j['frame']['origin_m']);k=.040/.125**2;h=.0025/2;triangles=len(json.loads((HERE/'rounded-planar-grid-v3.json').read_text())['triangles']);angles=[];dvals=[]
def nearest(co):
 rel=co-origin;a=rel.dot(U);t=rel.dot(V);c=rel.dot(N);x=a
 for _ in range(8):x-=(x-a+2*k*x*(k*x*x+c))/(1+6*k*k*x*x+2*k*c)
 n=(N+U*2*k*x).normalized();p=origin+U*x+V*t-N*k*x*x;return n,(co-p).dot(n)
for vertex in ob.data.vertices:dvals.append(nearest(vertex.co)[1])
for f in ob.data.polygons:
 if f.index>=2*triangles:continue
 for li in f.loop_indices:
  co=ob.data.vertices[ob.data.loops[li].vertex_index].co;n,d=nearest(co);expected=n if d>0 else-n;angles.append(math.degrees(math.acos(max(-1,min(1,ob.data.corner_normals[li].vector.dot(expected))))))
ob.data.calc_loop_triangles();tris=[tuple(t.vertices)for t in ob.data.loop_triangles];tree=BVHTree.FromPolygons([v.co for v in ob.data.vertices],tris,all_triangles=True);pairs=[(a,b)for a,b in tree.overlap(tree)if a<b and not set(tris[a])&set(tris[b])];report={'source_sha256':j['source_sha256'],'export_sha256':j['export_sha256'],'front_back_corner_samples':len(angles),'max_normal_angle_from_analytic_midsurface_deg':max(angles),'normal_angle_over_point1deg':sum(v>.1 for v in angles),'signed_distance_from_analytic_midsurface_m_range':[min(dvals),max(dvals)],'vertices_outside_halfthickness_by2um':sum(abs(d)>h+2e-6 for d in dvals),'nonadjacent_triangle_BVH_candidates':len(pairs),'first_candidate_triangle_pairs':pairs[:20],'scope':'Source defects directly investigated after the rejected bevel. BVH overlap alone is a candidate test, not a robust exact self-intersection classifier. No source saved.','art_accepted':False};(OUT/'rolled-surface-check.json').write_text(json.dumps(report,indent=2)+'\n');assert max(angles)<.1 and report['vertices_outside_halfthickness_by2um']==0 and not pairs,report;assert sha(source)==j['source_sha256'];print('ROLLED_SURFACE_SOURCE_CHECK',report)
