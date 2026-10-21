"""Bounded adjacent-edge contractions of the original closed raw author mesh.
No global merge, remesh, general simplification or buffer repair. Every removed
vertex maps to a kept original vertex within the fixed 1um cluster bound.
"""
import bpy,bmesh,math,json,hashlib,heapq,itertools
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/swingarm-body-v1';P=json.loads((H/'parameters.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();src=H/'swingarm-body-raw-v1.blend';parent=json.loads((O/'raw-source-geometry-check.json').read_text());assert sha(src)==parent['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(src));col=bpy.data.collections[P['collection']];objects=[o for o in col.objects if o.type=='MESH'];assert len(objects)==1;o=objects[0];original=o.data.copy();assert not original.has_custom_normals,'Raw author normals must be freshly recomputed, not inherited custom normals';bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table();before_volume=bm.calc_volume(signed=True);assert not any(not e.is_manifold for e in bm.edges);clusters={v:[v.co.copy()]for v in bm.verts};before_vertices=len(bm.verts);counter=itertools.count();queue=[];edge_limit=P['source_local_edge_collapse_max_edge_m'];shift_limit=P['source_local_edge_collapse_max_original_cluster_shift_m'];rejections={'link_condition':0,'cluster_shift':0,'face_fold':0};collapsed=0;largest_cluster_shift=0
for e in bm.edges:
 if e.calc_length()<=edge_limit:heapq.heappush(queue,(e.calc_length(),next(counter),e))
while queue:
 _,_,e=heapq.heappop(queue)
 if not e.is_valid or e.calc_length()>edge_limit:continue
 if len(e.link_faces)!=2 or any(len(f.verts)!=3 for f in e.link_faces):rejections['link_condition']+=1;continue
 a,b=e.verts;na={ed.other_vert(a)for ed in a.link_edges};nb={ed.other_vert(b)for ed in b.link_edges};opposite={v for f in e.link_faces for v in f.verts if v not in[a,b]}
 if len(opposite)!=2 or na&nb!=opposite:rejections['link_condition']+=1;continue
 choices=[]
 for keep,remove in[(a,b),(b,a)]:
  shift=max((q-keep.co).length for q in clusters[keep]+clusters[remove])
  if shift>shift_limit:rejections['cluster_shift']+=1;continue
  valid=True
  for face in remove.link_faces:
   if keep in face.verts:continue
   co=[keep.co if v==remove else v.co for v in face.verts];cross=(co[1]-co[0]).cross(co[2]-co[0]);old=[v.co for v in face.verts];oldcross=(old[1]-old[0]).cross(old[2]-old[0])
   if cross.length/2<=1e-18 or cross.dot(oldcross)<=0:valid=False;break
  if not valid:rejections['face_fold']+=1;continue
  choices.append((shift,-len(keep.link_edges),keep,remove))
 if not choices:continue
 _,_,keep,remove=min(choices,key=lambda c:(c[0],c[1]));merged=clusters[keep]+clusters.pop(remove);clusters[keep]=merged;largest_cluster_shift=max(largest_cluster_shift,max((q-keep.co).length for q in merged));bmesh.ops.weld_verts(bm,targetmap={remove:keep});collapsed+=1
 for ed in keep.link_edges:
  if ed.calc_length()<=edge_limit:heapq.heappush(queue,(ed.calc_length(),next(counter),ed))
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));nm=sum(not e.is_manifold for e in bm.edges);after_volume=bm.calc_volume(signed=True);r={'component_id':P['component_id'],'revision':P['revision'],'raw_source_sha256':sha(src),'method':'Adjacent edge contractions only, closed-triangle-mesh link condition, fold rejection, endpoints retain original coordinates. Original per-vertex clusters remain within 1um of their kept endpoint. No global proximity welding/general library simplification.','edge_limit_m':edge_limit,'maximum_original_cluster_shift_m':largest_cluster_shift,'cluster_shift_limit_m':shift_limit,'vertices_before':before_vertices,'vertices_after':len(bm.verts),'collapsed_edges':collapsed,'rejections':rejections,'nonmanifold_edges':nm,'signed_volume_before_m3':before_volume,'signed_volume_after_m3':after_volume,'relative_volume_change':abs(after_volume/before_volume-1),'buffer_repair':False,'art_accepted':False};(O/'topology-refinement-diagnostic.json').write_text(json.dumps(r,indent=2)+'\n');assert not nm and after_volume>0 and r['relative_volume_change']<1e-5 and largest_cluster_shift<=shift_limit,r
bm.to_mesh(o.data);bm.free();o.data.update();o.data.set_sharp_from_angle(angle=.55);slope=(.110-.103)/P['working_body_rear_end_y_m_estimated']
for f in o.data.polygons:
 n=f.normal;f.use_smooth=not(abs(n.z)>.999999 or abs(n.y)>.999999 or abs(n.x)>.999999 or(abs(abs(n.x)-1/math.sqrt(1+slope*slope))<1e-6 and abs(n.z)<1e-6))
uv=o.data.uv_layers.active
for f in o.data.polygons:
 axis=max(range(3),key=lambda a:abs(f.normal[a]));sign=1 if f.normal[axis]>=0 else-1
 for li in f.loop_indices:
  v=o.data.vertices[o.data.loops[li].vertex_index].co;pair=(sign*v.y,v.z)if axis==0 else(-sign*v.x,v.z)if axis==1 else(sign*v.x,v.y);uv.data[li].uv=(pair[0]/.010,pair[1]/.010)
o.data.calc_loop_triangles();areas=[(o.data.vertices[t.vertices[1]].co-o.data.vertices[t.vertices[0]].co).cross(o.data.vertices[t.vertices[2]].co-o.data.vertices[t.vertices[0]].co).length/2 for t in o.data.loop_triangles];o.data.calc_tangents(uvmap=uv.name);bad=[l.index for l in o.data.loops if l.tangent.length<.9];r.update(triangles=len(o.data.loop_triangles),minimum_triangle_area_m2=min(areas),zero_area_triangles=sum(a<=1e-18 for a in areas),source_zero_tangent_loops=len(bad),source_zero_tangent_loop_examples=bad[:20]);badset=set(bad);badfaces=[]
for f in o.data.polygons:
 if badset.intersection(f.loop_indices):badfaces.append({'polygon':f.index,'positions_m':[list(o.data.vertices[i].co)for i in f.vertices],'normal':list(f.normal),'area_m2':f.area,'smooth':f.use_smooth,'loops':[{'index':li,'normal':list(o.data.corner_normals[li].vector),'tangent':list(o.data.loops[li].tangent),'UV':list(uv.data[li].uv)}for li in f.loop_indices]})
r['bad_faces']=badfaces
bpy.ops.wm.save_as_mainfile(filepath=str(H/'swingarm-body-contracted-v1.blend'),compress=True)
r.update(intermediate_source_sha256=sha(H/'swingarm-body-contracted-v1.blend'),requires_authored_normal_and_needle_stage=True,not_final_export_or_freeze=True)
(O/'contraction-stage-check.json').write_text(json.dumps({k:v for k,v in r.items()if k!='bad_faces'},indent=2)+'\n')
print('WEWA_BODY_CONTRACTION_STAGE',collapsed,nm,largest_cluster_shift,r['intermediate_source_sha256'],flush=True)
