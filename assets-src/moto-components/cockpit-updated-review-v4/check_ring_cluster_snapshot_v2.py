from pathlib import Path
import bpy,json,hashlib,sys
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/cockpit-updated-review-v4';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=json.loads((O/'source-geometry-check.json').read_text());source=H/'cockpit-updated-review-v4.blend';assert sha(source)==B['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();from mathutils.bvhtree import BVHTree
def tree_world(o):
 graph=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(graph);mesh=ev.to_mesh();mesh.calc_loop_triangles()
 try:return BVHTree.FromPolygons([ev.matrix_world@v.co for v in mesh.vertices],[tuple(t.vertices)for t in mesh.loop_triangles],all_triangles=True)
 finally:ev.to_mesh_clear()
ring=next(o for c in s.collection.children if c.name=='WEWA_IGNITION_KEY_RING'for o in c.all_objects if o.type=='MESH');tree=tree_world(ring);rows=[]
for c in list(s.collection.children):
 if c.name not in ['WEWA_INSTRUMENTS_SEPARATE_PARTS','WEWA_IGNITION_LOCK','WEWA_IGNITION_CONNECTOR_HOUSING']:continue
 for o in list(c.all_objects):
  if o.type=='MESH':rows.append({'collection':c.name,'object':o.name,'surface_crossing_pairs':len(tree.overlap(tree_world(o)))})
r={'source_sha256':sha(source),'ring':ring.name,'frame':1,'tests':rows,'crossing_pairs_total':sum(q['surface_crossing_pairs']for q in rows),'scope':'Read-only evaluated native surface diagnostic of ring vs cluster/lock/connector. Surface crossing is separate from volumetric/coplanar contact or physical acceptance. No pose/mesh modified.','art_accepted':False};(O/'ring-cluster-surface-diagnostic.json').write_text(json.dumps(r,indent=2)+'\n');print('RING_CLUSTER_DIAGNOSTIC',r['crossing_pairs_total']);assert sha(source)==B['source_sha256']
