"""Read-only rays distinguish through holes, front groove and closed witnesses."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-intake-insulator-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();build=json.loads((H/'build-report.json').read_text());P=json.loads((H/'parameters.json').read_text())
source=H/'engine-intake-insulator-v1.blend';assert sha(source)==build['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source))
o=bpy.data.objects[build['geometry'][0]['name']];m=o.data;m.calc_loop_triangles()
tree=BVHTree.FromPolygons([v.co for v in m.vertices],[tuple(t.vertices)for t in m.loop_triangles],all_triangles=True)
def hit(xy,z,d):
    result=tree.ray_cast(Vector((*xy,z)),Vector((0,0,d)),.05)
    return None if result[0]is None else list(result[0])
half=P['working_bolt_pitch_m']/2;holes=[]
for xy in [(0,0),(-half,0),(half,0)]:
    a=hit(xy,.02,-1);b=hit(xy,-.01,1);assert a is None and b is None
    holes.append({'local_axis_xy_m':xy,'front_and_rear_rays_clear':True})
closed=[]
for xy in P['working_shallow_front_witness_marks_uv_m']:
    a=hit(xy,.02,-1);b=hit(xy,-.01,1);assert a and b
    assert abs(a[2]-(P['estimated_body_thickness_m']-P['working_front_witness_depth_m']))<1e-7 and abs(b[2])<1e-7
    closed.append({'local_xy_m':xy,'front_hit_m':a,'back_hit_m':b,'closed_not_through':True})
groove=[]
for xy in [(P['working_visible_front_groove_centre_radius_m'],0),(0,P['working_visible_front_groove_centre_radius_m'])]:
    a=hit(xy,.02,-1);b=hit(xy,-.01,1);assert a and b
    assert abs(a[2]-(P['estimated_body_thickness_m']-P['working_visible_front_groove_depth_m']))<1e-7 and abs(b[2])<1e-7
    groove.append({'local_xy_m':xy,'front_hit_m':a,'back_hit_m':b,'bottom_retained':True})
report={'source_sha256':sha(source),'export_sha256':build['export_sha256'],'through_openings':holes,'closed_surface_witnesses':closed,'groove_bottom_probes':groove,
        'scope':'Rays verify candidate model construction only. These dimensions/depths are estimates; unobserved back and exact installed fit are not received.',
        'all_dimensions_estimated':True,'art_accepted':False}
(O/'opening-depth-check.json').write_text(json.dumps(report,indent=2)+'\n');assert sha(source)==build['source_sha256'];print('INSULATOR_OPENINGS',json.dumps(report))
