"""Source-only bounded diagonal rotations, retaining every original vertex.
Triangle distance follows the independent cap2 plane/edge float64 method.
"""
import bpy,bmesh,json,math,hashlib,numpy as np,sys
from pathlib import Path
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H));from authored_normals import author_normals
R=H.parents[3];O=R/'creative/reviews/swingarm-body-v1';P=json.loads((H/'parameters.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();src=H/'swingarm-body-contracted-v1.blend';bpy.ops.wm.open_mainfile(filepath=str(src));o=next(o for o in bpy.data.collections[P['collection']].objects if o.type=='MESH');raw=json.loads((O/'raw-source-geometry-check.json').read_text());contraction=json.loads((O/'contraction-stage-check.json').read_text());assert sha(src)==contraction['intermediate_source_sha256'];all_positions=[tuple(v.co)for v in o.data.vertices];volume0=raw['signed_volume_m3'];slope=(.110-.103)/P['working_body_rear_end_y_m_estimated'];trials=[];batches=[]
def refresh():
 m=o.data;projection_normals,normal_report=author_normals(m,P)
 for uv in list(m.uv_layers):m.uv_layers.remove(uv)
 uv=m.uv_layers.new(name='Physical 10mm dominant projection after source retopology');values=[0.]*(len(m.loops)*2)
 for f in m.polygons:
  fn=projection_normals[f.index];axis=int(np.argmax(np.abs(fn)));sign=1 if fn[axis]>=0 else-1
  for li in f.loop_indices:
   v=m.vertices[m.loops[li].vertex_index].co;pair=(sign*v.y,v.z)if axis==0 else(-sign*v.x,v.z)if axis==1 else(sign*v.x,v.y);values[2*li:2*li+2]=[pair[0]/.010,pair[1]/.010]
 uv.data.foreach_set('uv',values);m.update();(O/'authored-normal-check.json').write_text(json.dumps(normal_report,indent=2)+'\n');m.calc_tangents(uvmap=uv.name);bad={l.index for l in m.loops if l.tangent.length<.9};return [f.index for f in m.polygons if bad.intersection(f.loop_indices)],len(bad)
def altitude(tris):
 a=tris[:,1]-tris[:,0];b=tris[:,2]-tris[:,0];area2=np.linalg.norm(np.cross(a,b),axis=1);longest=np.maximum.reduce([np.linalg.norm(a,axis=1),np.linalg.norm(b,axis=1),np.linalg.norm(tris[:,2]-tris[:,1],axis=1)]);return float(np.min(area2/longest))
weights=np.array([(i/16,j/16,1-(i+j)/16)for i in range(17)for j in range(17-i)],dtype=np.float64)
def samples(tri):return np.einsum('ij,kjl->kil',weights,tri).reshape((-1,3))
def distances(points,tri):
 best=np.full(len(points),np.inf)
 for a,b,c in tri:
  normal=np.cross(b-a,c-a);length=np.linalg.norm(normal)
  if length<=1e-30:continue
  normal/=length;signed=(points-a)@normal;q=points-signed[:,None]*normal;inside=np.ones(len(points),dtype=bool)
  for u,v in[(a,b),(b,c),(c,a)]:
   edge=v-u;inside&=np.cross(edge,q-u)@normal>=-1e-24;t=np.clip(((points-u)@edge)/np.dot(edge,edge),0,1);best=np.minimum(best,np.linalg.norm(points-u-t[:,None]*edge,axis=1))
  best[inside]=np.minimum(best[inside],np.abs(signed[inside]))
 return float(np.max(best))
# Identity must pass before this sampled local metric can authorize a rotation.
identity=np.array([[[0,0,0],[.02,0,0],[.01,1e-8,0]],[[0,0,0],[.01,1e-8,0],[0,.01,0]]],dtype=np.float64);assert distances(samples(identity),identity)<1e-12
for batch in range(8):
 badfaces,badcount=refresh();print('WEWA_NEEDLES_BATCH',batch,badcount,len(badfaces),flush=True)
 if not badcount:break
 bm=bmesh.new();bm.from_mesh(o.data);bm.faces.ensure_lookup_table();bm.verts.ensure_lookup_table();changed=0;used=set()
 targets=[bm.faces[fi]for fi in badfaces]
 for face in targets:
  if not face.is_valid or face in used:continue
  candidates=[]
  for edge in list(face.edges):
   if len(edge.link_faces)!=2:continue
   fa,fb=edge.link_faces
   if fa in used or fb in used or len(fa.verts)!=3 or len(fb.verts)!=3:continue
   vv=list(fa.verts);a,b=edge.verts
   if vv[(vv.index(a)+1)%3]!=b:a,b=b,a
   c=next(v for v in fa.verts if v not in[a,b]);d=next(v for v in fb.verts if v not in[a,b])
   if any(e.other_vert(c)==d for e in c.link_edges):continue
   old=np.array([[tuple(v.co)for v in f.verts]for f in[fa,fb]],dtype=np.float64);new=np.array([[tuple(v.co)for v in vs]for vs in[(c,d,b),(d,c,a)]],dtype=np.float64);quality0=altitude(old);quality1=altitude(new)
   if quality1<=quality0*1.20:continue
   nn=np.cross(new[:,1]-new[:,0],new[:,2]-new[:,0]);on=np.cross(old[:,1]-old[:,0],old[:,2]-old[:,0]);nref=on.sum(axis=0)
   if np.any(nn@nref<=0):continue
   forward=distances(samples(old),new);reverse=distances(samples(new),old)
   if max(forward,reverse)>1e-6:continue
   candidates.append((quality1,edge,fa,fb,old,new,forward,reverse,quality0))
  if not candidates:continue
  q,edge,fa,fb,old,new,fw,rv,q0=max(candidates,key=lambda x:x[0]);before_faces={tuple(sorted(v.index for v in f.verts))for f in[fa,fb]};used.update([fa,fb]);result=bmesh.ops.rotate_edges(bm,edges=[edge],use_ccw=False)
  if not result.get('edges'):continue
  for ed in result['edges']:used.update(ed.link_faces)
  changed+=1;trials.append({'batch':batch,'old_triangles_m':old.tolist(),'new_triangles_m':new.tolist(),'old_min_altitude_m':q0,'new_min_altitude_m':q,'sampled_old_to_new_surface_max_m':fw,'sampled_new_to_old_surface_max_m':rv,'sample_grid_subdivision':16,'source_operation':'one diagonal rotation; all vertex positions retained'})
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));nm=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);assert not nm and abs(vol/volume0-1)<1e-5;(O/'needle-refinement-progress.json').write_text(json.dumps({'batches':batches,'rotations':trials,'current_zero_tangent_loops':badcount,'all_vertex_positions_preserved':True,'art_accepted':False},indent=2)+'\n');bm.to_mesh(o.data);bm.free();assert all_positions==[tuple(v.co)for v in o.data.vertices];batches.append({'batch':batch,'bad_source_tangent_loops_before':badcount,'accepted_disjoint_diagonal_rotations':changed,'nonmanifold_edges':nm,'volume_relative_difference':abs(vol/volume0-1)})
 if not changed:break
badfaces,badcount=refresh();r={'component_id':P['component_id'],'revision':P['revision'],'raw_source_sha256':sha(src),'all_vertex_positions_bit_identical_to_contracted_input':all_positions==[tuple(v.co)for v in o.data.vertices],'original_author_raw_source_sha256':raw['source_sha256'],'prior_contraction_stage':'contraction-stage-check.json','method':'Source-only local diagonal rotations with geometric quality improvement and float64 two-triangle surface samples, 16subdivision. No vertex displacement, merge, remesh, general simplification or buffer repair.','batches':batches,'rotations':trials,'zero_tangent_loops':badcount,'art_accepted':False};(O/'needle-refinement-check.json').write_text(json.dumps(r,indent=2)+'\n');bpy.ops.wm.save_as_mainfile(filepath='/workspace/wewa-assets/work-in-progress/swingarm/body/needle-refinement-diagnostic.blend',compress=True);assert not badcount,{k:v for k,v in r.items()if k!='rotations'}
o.data.calc_loop_triangles();areas=[(o.data.vertices[t.vertices[1]].co-o.data.vertices[t.vertices[0]].co).cross(o.data.vertices[t.vertices[2]].co-o.data.vertices[t.vertices[0]].co).length/2 for t in o.data.loop_triangles];assert min(areas)>1e-18;bm=bmesh.new();bm.from_mesh(o.data);volume=bm.calc_volume(signed=True);nm=sum(not e.is_manifold for e in bm.edges);bm.free();assert not nm
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.gltf(filepath=str(H/'swingarm-body-v1-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True);bpy.ops.wm.save_as_mainfile(filepath=str(H/'swingarm-body-v1.blend'),compress=True);r.update(source_sha256=sha(H/'swingarm-body-v1.blend'),export_sha256=sha(H/'swingarm-body-v1-inspection.glb'));(O/'needle-refinement-check.json').write_text(json.dumps(r,indent=2)+'\n');g={**raw,'source_sha256':r['source_sha256'],'export_sha256':r['export_sha256'],'signed_volume_m3':volume,'triangles':len(o.data.loop_triangles),'vertices':len(o.data.vertices),'min_triangle_area_m2':min(areas),'needle_refinement_report':'needle-refinement-check.json','art_accepted':False};(O/'source-geometry-check.json').write_text(json.dumps(g,indent=2)+'\n');print('WEWA_BODY_NEEDLE_PASS',len(trials),r['source_sha256'],r['export_sha256'],flush=True)
