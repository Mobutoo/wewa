"""Read-only actual body rays: distinguish material obstruction from camera visibility."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];source=H/'engine-head-v3.blend';bpy.ops.wm.open_mainfile(filepath=str(source));body=bpy.data.objects['Engine UG5 head hollow exterior casting - editable candidate'];tree=BVHTree.FromPolygons([v.co for v in body.data.vertices],[tuple(p.vertices)for p in body.data.polygons]);rows=[]
for y in[-.040,-.020,0,.020,.040]:
 start=Vector((.055,y,-.002));direction=Vector((1,0,2.4)).normalized();point,normal,index,distance=tree.ray_cast(start,direction,.18);rows.append({'start_local_m':list(start),'direction_local':list(direction),'first_surface_local_m':list(point)if point else None,'normal':list(normal)if normal else None,'face':index,'distance':distance})
report={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'scope':'Unmeasured oblique visible-mouth rays, not real camera/gas-path/fit qualification','rays':rows,'source_modified':False};(R/'creative/reviews/engine-head-v3/oblique-mouth-rays.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
