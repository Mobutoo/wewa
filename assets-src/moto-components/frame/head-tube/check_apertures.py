"""Read-only full source bore ray, no edits to source/export."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/frame-head-tube-v1';p=H/'frame-head-tube-v1.blend';bpy.ops.wm.open_mainfile(filepath=str(p));o=list(bpy.data.collections['WEWA_FRAME_HEADTUBE_ISOLATED'].objects)[0];m=o.data;m.calc_loop_triangles();tree=BVHTree.FromPolygons([v.co for v in m.vertices],[list(t.vertices)for t in m.loop_triangles],all_triangles=True);rows=[]
for label,x in [('axis',0),('near_bore',.0202)]:
 hit=tree.ray_cast(Vector((x,0,-.01)),Vector((0,0,1)),.18)[0];assert hit is None;rows.append({'name':label,'origin_m':[x,0,-.01],'direction':[0,0,1],'distance_m':.18,'clear':True})
r={'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'actual_source_full_length_rays':rows,'bearing_seat_or_clearance_certified':False,'source_or_buffer_modified':False};(O/'source-apertures-check.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
