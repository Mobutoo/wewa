"""Read-only candidate Y placement sweep after the first actual interface refusal."""
import bpy,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/research/instrument-visor';source=HERE/'instrument-visor-shell-study-v1.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();digest=sha(source);bpy.ops.wm.open_mainfile(filepath=str(source));shell=bpy.data.objects['Visor finite curved shell - conditional estimated study'];root=bpy.data.objects['VISOR_PANEL_MOUNT_ESTIMATED'];other=ROOT/'assets-src/moto-components/instruments/instruments-v3.blend';linkedsha=sha(other)
def tree(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles();v=[ob.matrix_world@p.co for p in m.vertices];t=BVHTree.FromPolygons(v,[tuple(t.vertices)for t in m.loop_triangles],all_triangles=True);ev.to_mesh_clear();return t,v
with bpy.data.libraries.load(str(other),link=False)as(a,b):b.collections=['WEWA_INSTRUMENTS_SEPARATE_PARTS']
collection=b.collections[0];bpy.context.scene.collection.children.link(collection);bpy.context.view_layer.update();others=[]
for ob in collection.all_objects:
 if ob.type not in ['MESH','FONT','CURVE']or ob.hide_render:continue
 t,v=tree(ob)
 if v:others.append((ob.name,t,v))
rows=[]
for delta in [0,-.005,-.010,-.015,-.020,-.025,-.030]:
 root.location.y=delta;bpy.context.view_layer.update();s,v=tree(shell);cross=[];near=[]
 for name,t,verts in others:
  count=len(s.overlap(t))
  if count:cross.append({'object':name,'crossings':count})
  near.append(min(s.find_nearest(p)[3]for p in verts))
 rows.append({'Y_delta_m':delta,'new_origin_Y_m':-.275+delta,'actual_source_crossings':cross,'surface_crossing_free':not cross,'min_distance_at_instrument_vertices_m':min(near)})
assert sha(source)==digest and sha(other)==linkedsha;report={'baseline_source_sha256':digest,'linked_instruments_source_sha256':linkedsha,'pose_candidates':rows,'source_files_modified':False,'scope':'Only source root location changed temporarily in memory; bounded frontward Y translations. Actual evaluated BVH crossings, vertex-sample distances are not exact minimum clearance. No change to rake, wrap, thickness, width or height.','art_accepted':False};(OUT/'placement-sweep-v1.json').write_text(json.dumps(report,indent=2)+'\n');print('VISOR_POSE_SWEEP',rows)
