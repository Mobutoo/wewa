"""Actual finite clear bore, closed-mark depths and interior lip samples; no real fit/compliance claim."""
from pathlib import Path
import bpy,json,hashlib,sys,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-intake-sleeve-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=json.loads((H/('build-report.json'if'--final'in sys.argv else'geometry-report.json')).read_text());P=json.loads((H/'parameters.json').read_text());source=H/('engine-intake-sleeve-v1.blend'if'--final'in sys.argv else'engine-intake-sleeve-v1-geometry.blend');assert sha(source)==B['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));o=bpy.data.objects[B['geometry'][0]['name']];m=o.data;m.calc_loop_triangles();tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(t.vertices)for t in m.loop_triangles],all_triangles=True);clear=[]
for x,y in [(0,0),(.004,0),(-.004,0),(0,.004),(0,-.004),(.008,0),(-.008,0),(0,.008),(0,-.008)]:
 start=Vector((x,y,.035));axis=Vector((0,0,-1));hit=tree.ray_cast(start,axis,.070);assert hit[0]is None;clear.append({'origin_m':list(start),'direction':list(axis),'length_m':.070,'hit':False})
marks=[]
for angle in P['closed_front_mark_angles_degrees']:
 a=math.radians(angle);start=Vector((.0208*math.cos(a),.0208*math.sin(a),.030));hit=tree.ray_cast(start,Vector((0,0,-1)),.060);assert hit[0]is not None;assert .0172<hit[0].z<.0175;marks.append({'angle_degrees_working':angle,'actual_closed_bottom_Z_m':hit[0].z,'not_a_through_hole':True})
lips=[]
for z in [.015,.0072,-.006,-.016]:
 row=[]
 for j in range(4):
  a=math.tau*j/4;axis=Vector((math.cos(a),math.sin(a),0));hit=tree.ray_cast(Vector((0,0,z)),axis,.030);assert hit[0]is not None;r=math.hypot(hit[0].x,hit[0].y);assert .0105<r<.0185;row.append(r)
 lips.append({'local_Z_m':z,'actual_first_inner_surface_radii_m':row})
# The front fork opens axially between the two actual tongues at its estimated angular midpoint.
a=math.radians(sum(P['fork_working_angles_degrees'])/2);start=Vector((.0233*math.cos(a),.0233*math.sin(a),.035));hit=tree.ray_cast(start,Vector((0,0,-1)),.016);assert hit[0]is None
r={'component_id':P['component_id'],'source_sha256':sha(source),'export_sha256':B['export_sha256'],'clear_bore_rays':clear,'five_closed_face_marks':marks,'actual_inner_lip_radial_samples':lips,'fork_gap_finite_axial_ray_clear':True,'scope':'Nine finite70mm rays pass actual annular candidate; five front marks retain closed bottoms and are not holes;16true inner-wall ray hits reveal two lips/rear shoulder in this candidate only. Fork gap clear over finite interval. Not measured OEM bores, flow area, carb venturi, seal compression/rubber deformation or mounted interface. Rear profile conditional relatedGarage appearance, endcorrespondence unknown.','art_accepted':False};(O/'opening-envelope-check.json').write_text(json.dumps(r,indent=2)+'\n');assert sha(source)==B['source_sha256'];print(json.dumps(r))
