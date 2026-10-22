import bpy,json
from pathlib import Path
from collections import Counter,defaultdict
R=Path('/workspace/wewa');K='passenger-rubber-completion-v3';O=R/'creative/reviews'/K
bpy.ops.wm.open_mainfile(filepath=str(R/'assets-src/moto-components'/K/'child-candidate.blend'))
a=next(o for o in bpy.context.scene.objects if o.type=='MESH');coords={tuple(v.co) for v in a.data.vertices}
with bpy.data.libraries.load(str(R/'assets-src/moto-components/passenger-footrest-rubber-jk113008-v1/child-candidate.blend'),link=False) as (src,dst):dst.objects=['JK113008_PASSENGER_RUBBER_VISIBLE_ENVELOPE_ONLY']
b=dst.objects[0];assert all(tuple(v.co)in coords for v in b.data.vertices)
edges=Counter(tuple(sorted((x,y)))for p in a.data.polygons for x,y in zip(list(p.vertices),list(p.vertices[1:])+[p.vertices[0]]));adj=defaultdict(set)
for (x,y),n in edges.items():
 if n==1:adj[x].add(y);adj[y].add(x)
assert all(len(ns)==2 for ns in adj.values());unseen=set(adj);loops=[]
while unseen:
 stack=[unseen.pop()];found=[]
 while stack:
  v=stack.pop();found.append(v)
  for w in adj[v]:
   if w in unseen:unseen.remove(w);stack.append(w)
 loops.append(found)
assert sorted(map(len,loops))==[192,192]
proof=dict(all_old_native_vertex_coordinates_preserved=True,old_vertices=len(b.data.vertices),new_vertices=len(a.data.vertices),new_faces=len(a.data.polygons)-len(b.data.polygons),boundary_loops=[dict(vertex_count=len(vs),x_range=[min(a.data.vertices[v].co.x for v in vs),max(a.data.vertices[v].co.x for v in vs)])for vs in loops],no_longitudinal_diagnostic_boundary=True,deep_bore_modeled=False,distal_cap_modeled=False,retention_modeled=False)
(O/'native-delta-check.json').write_text(json.dumps(proof,indent=2)+'\n')
