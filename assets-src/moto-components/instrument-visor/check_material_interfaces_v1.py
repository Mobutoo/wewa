"""Actual-source shell/instrument interface, read only; no physical fit qualification."""
import bpy,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/instrument-visor-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=HERE/'instrument-visor-v1.blend';j=json.loads((OUT/'source-geometry-check.json').read_text());assert sha(source)==j['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));shell=bpy.data.objects[j['object']]
def tree(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles();v=[ob.matrix_world@p.co for p in m.vertices];t=BVHTree.FromPolygons(v,[tuple(t.vertices)for t in m.loop_triangles],all_triangles=True);ev.to_mesh_clear();return t,v
other=ROOT/'assets-src/moto-components/instruments/instruments-v3.blend';linkedsha=sha(other)
with bpy.data.libraries.load(str(other),link=False)as(a,b):b.collections=['WEWA_INSTRUMENTS_SEPARATE_PARTS']
collection=b.collections[0];bpy.context.scene.collection.children.link(collection);bpy.context.view_layer.update();s,verts=tree(shell);rows=[]
for ob in collection.all_objects:
 if ob.type not in ['MESH','FONT','CURVE']or ob.hide_render:continue
 t,v=tree(ob)
 if not v:continue
 hits=len(s.overlap(t));dist=[(s.find_nearest(p)[3])for p in v];rows.append({'object':ob.name,'actual_surface_triangle_crossings':hits,'minimum_vertex_sample_distance_m':min(x for x in dist if x is not None)})
clear=not any(r['actual_surface_triangle_crossings']for r in rows);assert sha(source)==j['source_sha256']and sha(other)==linkedsha;report={'source_sha256':j['source_sha256'],'linked_instruments_source_sha256':linkedsha,'actual_surface_checks':rows,'all_sampled_interfaces_clear':clear,'minimum_vertex_sample_distance_m':min(r['minimum_vertex_sample_distance_m']for r in rows),'scope':'Evaluated source BVH surface crossings and nearest distances only at actual instrument vertices. These distances are not exact minimum assembly clearance. Mount supports, headlamp, cables and installed physical fit unverified. No source saved.','art_accepted':False};(OUT/'instrument-interface-check.json').write_text(json.dumps(report,indent=2)+'\n');print('VISOR_INSTRUMENT_INTERFACE',clear,[r for r in rows if r['actual_surface_triangle_crossings']]);assert clear
