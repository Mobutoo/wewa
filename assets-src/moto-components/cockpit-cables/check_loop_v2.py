"""Read-only surface/containment checks in current immutable cases, no source saving."""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(H.parent/'throttle-control'))
from control_geometry import tree_world
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();src=H/'cockpit-cables-v2.blend';before=sha(src);bpy.ops.wm.open_mainfile(filepath=str(src));bpy.data.collections['CABLES_IMMUTABLE_INTERFACE_GUIDES'].hide_viewport=False;bpy.context.view_layer.update();loop=next(o for o in bpy.data.collections['WEWA_COCKPIT_CABLES_PARTIAL'].objects if'ignition'in o.name.lower());mesh=loop.data;mesh.calc_loop_triangles();verts=[loop.matrix_world@v.co for v in mesh.vertices];faces=[list(t.vertices)for t in mesh.loop_triangles];tree=BVHTree.FromPolygons(verts,faces,all_triangles=True)
# Adjacent triangles touch by construction; only disjoint index sets count.
selfpairs=[(a,b)for a,b in tree.overlap(tree)if a<b and not set(faces[a]).intersection(faces[b])];assert not selfpairs,selfpairs[:10]
cover=bpy.data.objects['Shaped central cluster cover'];ctree=tree_world(cover)
def is_inside(point):
 direction=Vector((.8123,.3937,.4301)).normalized();origin=point.copy();hits=0
 for _ in range(100):
  location,normal,index,distance=ctree.ray_cast(origin,direction,1.0)
  if location is None:return hits%2==1
  hits+=1;origin=location+direction*1e-7
 raise RuntimeError('Ray did not terminate')
inside=[i for i,p in enumerate(verts)if is_inside(p)];assert not inside,inside[:10]
nearest=min(ctree.find_nearest(p)[3]for p in verts)
report={'source_sha256':before,'loop_nonadjacent_triangle_self_crossings':len(selfpairs),'loop_to_current_central_cover_triangle_crossings':len(tree.overlap(ctree)),'loop_vertices_inside_current_central_cover':len(inside),'sampled_vertex_to_cover_minimum_distance_m':nearest,'distance_scope':'Minimum sampled loopvertex→cover distance, NOT exact surface clearance, manufacturer tolerance or full steering test.','source_modified':False,'art_accepted':False};assert report['loop_to_current_central_cover_triangle_crossings']==0;assert sha(src)==before
(R/'creative/reviews/cockpit-cables-v2/loop-spatial-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
