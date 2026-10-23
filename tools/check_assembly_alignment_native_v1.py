"""Measure the new native mounts and actual contact surfaces in saved Blender source."""
import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'creative/reviews/assembly-alignment-v1'
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets-src/moto-components/assembly-alignment-v1/motorcycle-aligned.blend'))
dg=bpy.context.evaluated_depsgraph_get();rows=[]
for parent in bpy.context.scene.objects:
 if not parent.name.startswith('ALIGNMENT ['):continue
 for ob in parent.children_recursive:
  if ob.type!='MESH':continue
  evaluated=ob.evaluated_get(dg);mesh=evaluated.to_mesh();bm=bmesh.new();bm.from_mesh(mesh)
  bad=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=False)
  assert bad==0 and volume>0,(ob.name,bad,volume)
  rows.append({'name':ob.name,'non_manifold_edges':bad,'volume_m3':volume});bm.free();evaluated.to_mesh_clear()
# Compare upper cover boundary to seat surface, using actual transformed vertices.
seat=bpy.data.objects['Seat outer upholstered envelope - estimated']
tree=BVHTree.FromPolygons([seat.matrix_world@v.co for v in seat.data.vertices],[list(p.vertices) for p in seat.data.polygons])
seams=[]
for name in ['sidecover-LH','sidecover-RH-normalized']:
 ob=next(o for o in bpy.data.objects['PARENT ['+name+']'].children_recursive if o.type=='MESH' and 'OUTER_SKIN' in o.name)
 pts=[ob.matrix_world@v.co for v in ob.data.vertices]
 upper=[p for p in pts if p.z>-.315 and .4<p.y<.70]
 distances=[tree.find_nearest(p)[3] for p in upper]
 seams.append({'part':name,'upper_vertices_sampled':len(upper),'minimum_surface_distance_m':min(distances),'maximum_surface_distance_m':max(distances),'note':'Distances to seat are unsigned; bounded visual seam, not a collision/free-clearance certification.'})
(OUT/'native-surface-check.json').write_text(json.dumps({'new_meshes':rows,'seat_seams':seams,'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n')
print('ALIGNMENT_NATIVE_CHECK',len(rows),seams)
