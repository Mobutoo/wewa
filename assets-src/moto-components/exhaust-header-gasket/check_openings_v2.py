"""Actual finite annular opening and bead-depth rays; no seal performance claim."""
from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/exhaust-header-gasket-v2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();b=json.loads((H/'build-report-v2.json').read_text());source=H/'exhaust-header-gasket-v2.blend';assert sha(source)==b['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));o=bpy.data.objects[b['geometry'][0]['name']];m=o.data;m.calc_loop_triangles();tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(t.vertices)for t in m.loop_triangles],all_triangles=True);axis=Vector((0,0,1));rows=[];walls=[]
for x,y in [(0,0),(.005,0),(-.005,0),(0,.005),(0,-.005)]:
 start=Vector((x,y,-.006));hit=tree.ray_cast(start,axis,.012);q={'origin_world_m':list(start),'direction_world':list(axis),'length_m':.012,'wall_hit':hit[0]is not None};rows.append(q);assert hit[0]is None
for j in range(4):
 angle=math.tau*j/4;start=Vector((.0148*math.cos(angle),.0148*math.sin(angle),-.006));entry=tree.ray_cast(start,axis,.012);assert entry[0]is not None;exit=tree.ray_cast(entry[0]+axis*1e-6,axis,.012);assert exit[0]is not None;depth=(exit[0]-entry[0]).length;assert .001<depth<.003;walls.append({'angle_rad':angle,'sampled_external_envelope_depth_m':depth})
r={'component_id':b['component_id'],'source_sha256':sha(source),'export_sha256':b['export_sha256'],'lumen_rays':rows,'annular_envelope_depth_rays':walls,'scope':'Five actual finite-mesh clear central rays and four positive annular-envelope depths only. Not a material thickness/internal-core claim or measured free/crushed section, pressure seal, exhaust flow or mounted fit.','art_accepted':False};(O/'opening-envelope-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
