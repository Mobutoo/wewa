"""Read-only actual model rays; no real gas-flow or assembly certification."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-intake-manifold-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();b=json.loads((H/'build-report.json').read_text());P=json.loads((H/'parameters.json').read_text());source=H/'engine-intake-manifold-v1.blend';assert sha(source)==b['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));o=bpy.data.objects[b['geometry'][0]['name']];m=o.data;m.calc_loop_triangles();tree=BVHTree.FromPolygons([v.co for v in m.vertices],[tuple(t.vertices)for t in m.loop_triangles],all_triangles=True)
def cast(origin,direction):
 h=tree.ray_cast(Vector(origin),Vector(direction),.15);return None if h[0]is None else list(h[0])
through=[]
for x,y,label in [(0,0,'Central lumen'),(-.006,0,'Central lumen offset'),(.006,0,'Central lumen offset'),(-P['working_bolt_pitch_m']/2,0,'Bolt ear'),(P['working_bolt_pitch_m']/2,0,'Bolt ear')]:
 a=cast((x,y,.065),(0,0,-1));c=cast((x,y,-.010),(0,0,1));assert a is None and c is None,(label,a,c);through.append({'label':label,'local_xy_m':[x,y],'both_direction_rays_clear':True})
closed=[]
for origin,direction,label in [((.014,0,.065),(0,0,-1),'Annular top lip'),((-.04,0,.0252),(1,0,0),'Closed estimated lateral cast feature')]:
 a=cast(origin,direction);assert a,label;closed.append({'label':label,'origin_local_m':origin,'direction_local':direction,'hit_local_m':a})
q={'source_sha256':sha(source),'export_sha256':b['export_sha256'],'through_rays':through,'closed_surface_probes':closed,'scope':'Central and bolt lumens are actually clear in this candidate; lateral feature closed by explicit estimate, no function inferred. No physical flow, dimension or OEM fit proof.','all_dimensions_estimated':True,'art_accepted':False};(O/'opening-depth-check.json').write_text(json.dumps(q,indent=2)+'\n');assert sha(source)==b['source_sha256'];print(json.dumps(q))
