"""Bounded local source retessellation before UV/baking, no tangent buffer edits."""
from pathlib import Path
import bpy,bmesh,json,hashlib,math,sys
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-intake-manifold-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (H/'preflight-manifest.json').exists(), 'Frozen revision must stay immutable; author a separate revision'
g=json.loads((H/'geometry-report.json').read_text());source=H/'engine-intake-manifold-v1-geometry.blend';assert sha(source)==g['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));o=bpy.data.objects[g['geometry'][0]['name']];datum=o.parent
sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import check_mesh,export
original=o.data.copy();positions=[tuple(v.co)for v in original.vertices];matrix=[list(r)for r in o.matrix_world]
def faces(m):return {tuple(sorted(p.vertices)):tuple(p.vertices)for p in m.polygons}
def quality(m,ids):
 a,b,c=[np.asarray(m.vertices[i].co,dtype=np.float64)for i in ids];length=max(np.linalg.norm(b-a),np.linalg.norm(c-b),np.linalg.norm(a-c));return np.linalg.norm(np.cross(b-a,c-a))/length**2

def samples(m,ids):
 out=[]
 for f in ids:
  a,b,c=[np.asarray(m.vertices[i].co,dtype=np.float64)for i in f]
  for j in range(17):
   for k in range(17-j):out.append(a+(b-a)*j/16+(c-a)*k/16)
 return out

def distance(p,m,subset):
 best=float('inf')
 for ids in subset:
  a,b,c=[np.asarray(m.vertices[i].co,dtype=np.float64)for i in ids];normal=np.cross(b-a,c-a);L=np.linalg.norm(normal)
  if L==0:continue
  normal/=L;signed=np.dot(p-a,normal);q=p-normal*signed
  if min(np.dot(np.cross(v-u,q-u),normal)for u,v in [(a,b),(b,c),(c,a)])>=-1e-24:best=min(best,abs(signed))
  for u,v in [(a,b),(b,c),(c,a)]:
   t=np.clip(np.dot(p-u,v-u)/np.dot(v-u,v-u),0,1);best=min(best,float(np.linalg.norm(p-u-t*(v-u))))
 return best

def author_UV_and_find_bad():
 bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.012,area_weight=0,correct_aspect=True,scale_to_bounds=False);bpy.ops.object.mode_set(mode='OBJECT')
 m=o.data;m.calc_tangents(uvmap=m.uv_layers.active.name);bad=[]
 for f in m.polygons:
  errors=[(abs(m.loops[i].tangent.length-1),abs(m.loops[i].tangent.dot(m.corner_normals[i].vector)))for i in f.loop_indices]
  uv=[m.uv_layers.active.data[i].uv for i in f.loop_indices];area=abs((uv[1]-uv[0]).cross(uv[2]-uv[0]))/2
  if area==0 or any(a>.001 or b>.001 for a,b in errors):bad.append({'face':f.index,'vertices':list(f.vertices),'errors':errors,'UVarea':area})
 return bad
steps=[];initial=None
for iteration in range(30):
 bad=author_UV_and_find_bad()
 if initial is None:initial=bad
 print('TOPOLOGY_BAD',iteration,len(bad),flush=True)
 if not bad:break
 chosen=None
 for badface in bad:
  old=o.data;oldfaces=faces(old);ids=badface['vertices'];trials=[]
  for i in range(3):
   edgeids={ids[i],ids[(i+1)%3]};m=old.copy();bm=bmesh.new();bm.from_mesh(m);bm.verts.ensure_lookup_table();edge=next(e for e in bm.edges if {v.index for v in e.verts}==edgeids)
   before=[tuple(v.index for v in f.verts)for f in edge.link_faces]
   if len(before)!=2:bm.free();continue
   result=bmesh.ops.rotate_edges(bm,edges=[edge],use_ccw=False);bm.normal_update();bm.to_mesh(m);bm.free();m.update();newfaces=faces(m);removed=[v for k,v in oldfaces.items()if k not in newfaces];added=[v for k,v in newfaces.items()if k not in oldfaces]
   if len(removed)!=2 or len(added)!=2:continue
   assert positions==[tuple(v.co)for v in m.vertices]
   oldq=min(quality(old,x)for x in removed);newq=min(quality(m,x)for x in added)
   if newq<=oldq*1.05:continue
   d1=max(distance(p,m,added)for p in samples(old,removed));d2=max(distance(p,old,removed)for p in samples(m,added))
   row={'edge_vertex_indices':sorted(edgeids),'removed':removed,'added':added,'old_min_triangle_quality':oldq,'new_min_triangle_quality':newq,'old_to_new_sampled_max_m':d1,'new_to_old_sampled_max_m':d2,'samples_each_direction':306,'vertices_bit_identical':True}
   if max(d1,d2)<1e-7:trials.append((row,m))
  if trials:
   row,m=max(trials,key=lambda t:t[0]['new_min_triangle_quality']);o.data=m;chosen=row;break
 if chosen is None:raise RuntimeError('No bounded local source retessellation found '+json.dumps(bad))
 steps.append(chosen)
else:raise RuntimeError('Native tangent diagnostic failed to converge')
assert positions==[tuple(v.co)for v in o.data.vertices]and matrix==[list(r)for r in o.matrix_world]
# UV is reauthored deterministically in the following material recipe; topology source keeps this actual diagnostic atlas.
geometry=[check_mesh(o)];glb=H/'engine-intake-manifold-v1-topology.glb';export(glb,[datum,o]);dest=H/'engine-intake-manifold-v1-topology.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True,relative_remap=False)
report={**g,'source_sha256':sha(dest),'export_sha256':sha(glb),'parent_geometry_source_sha256':g['source_sha256'],'geometry':geometry,'source_topology_refinements':steps,'initial_native_bad_faces':initial,'final_native_bad_faces':bad,'all_vertex_positions_bit_identical':True,'matrix_unchanged':True,'distance_method':'Direct float64 point-to-two-triangle distance, two directions153samples per changed triangle. Sampled bound, not a global Hausdorff proof.','native_tangent_buffer_repaired':False}
(H/'topology-report.json').write_text(json.dumps(report,indent=2)+'\n');(O/'source-topology-refinement.json').write_text(json.dumps(report,indent=2)+'\n');assert sha(source)==g['source_sha256'];print('MANIFOLD_TOPOLOGY',len(steps),sha(dest),sha(glb),flush=True)
