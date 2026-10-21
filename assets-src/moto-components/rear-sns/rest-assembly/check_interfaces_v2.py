"""Read-only actual shared-frame surface intersections; no contact certification."""
import bpy,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/rear-sns-rest-assembly-v2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();j=json.loads((O/'build-report.json').read_text());source=H/'rear-sns-rest-assembly-v2.blend';assert sha(source)==j['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();parts={};evidence=[]
for q in j['input_geometry']:
 vertices=[];triangles=[]
 for row in q['objects']:
  ob=next(a for a in bpy.context.scene.objects if a.name==row['object']);ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();off=len(vertices);vertices.extend([ob.matrix_world@v.co for v in me.vertices]);triangles.extend([tuple(off+a for a in t.vertices)for t in me.loop_triangles]);ev.to_mesh_clear()
 assert all(len(t)==3 for t in triangles);parts[q['unit']]=BVHTree.FromPolygons(vertices,triangles,all_triangles=True,epsilon=0);evidence.append({'unit':q['unit'],'vertices':len(vertices),'triangles':len(triangles),'bbox_m':[[min(v[k]for v in vertices),max(v[k]for v in vertices)]for k in range(3)]})
rows=[];names=list(parts)
for i,a in enumerate(names):
 for b in names[i+1:]:
  pairs=parts[a].overlap(parts[b]);rows.append({'a':a,'b':b,'actual_intersecting_triangle_pairs':len(pairs),'first_pairs':pairs[:12]})
r={'schema':1,'source_sha256':sha(source),'exact_input_manifest_sha256':sha(O/'exact-inputs-v2.json'),'method':'Actual evaluated linked-source world-space triangle surfaces; zero epsilon BVHTree.overlap for all91 distinct component pairs. No source save.','components':evidence,'pairs':rows,'intersection_pair_total':sum(q['actual_intersecting_triangle_pairs']for q in rows),'limitation':'Surface-only test does not establish volume disjointness, containment, signed separation, seated contact, material load path, installed fit or OEM identity. Intentional covered/open interfaces are not converted to solid mechanics.','art_accepted':False};(O/'source-surface-interface-check.json').write_text(json.dumps(r,indent=2)+'\n');assert sha(source)==j['source_sha256'];print('ACTUAL_PAIRS',len(rows),'triangle_intersections',r['intersection_pair_total'])
