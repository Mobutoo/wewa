"""One opposed notch, locally refined/deformed; no optical bands or hidden lug."""
import bpy,json,math,hashlib
from pathlib import Path
from collections import Counter,defaultdict
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/indicator-front-lens-study-v3';O.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();P=json.loads((H/'parameters-study-v3.json').read_text());Q=P['notch'];B=R/'creative/reviews/indicator-front-lens-study-v2';base=json.loads((B/'build-report.json').read_text());freeze=json.loads((B/'study-freeze-manifest.json').read_text());assert all(sha(R/q['path'])==q['sha256']for q in freeze['files']);assert(R/'creative/research/indicator-front-lens/opposed-notch-plan-v3.json').exists();src0=H/'indicator-front-lens-study-v2.blend';assert sha(src0)==base['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(src0));ob=bpy.data.objects[base['object']];old=ob.data;V=[Vector(v.co)for v in old.vertices];F=[tuple(f.vertices)for f in old.polygons];NS=[[Vector(old.corner_normals[k].vector)for k in f.loop_indices]for f in old.polygons];US=[[tuple(old.uv_layers.active.data[k].uv)for k in f.loop_indices]for f in old.polygons];origin=list(range(len(F)));oldV=[tuple(v)for v in V];oldF=list(F);oldNS=[[tuple(n)for n in a]for a in NS];oldUS=[list(a)for a in US];S=(P['face_radius_m']**2+P['face_sag_m']**2)/(2*P['face_sag_m']);center=math.radians(Q['theta_center_degrees']);half=math.radians(Q['theta_half_span_degrees']);margin=math.radians(Q['local_refinement_margin_degrees'])
def da(x,z):return math.atan2(math.sin(math.atan2(z,x)-center),math.cos(math.atan2(z,x)-center))
def near(v):return math.hypot(v.x,v.z)>=Q['radial_transition_start_m']and abs(da(v.x,v.z))<half+margin
patterns={0:[(0,1,2)],1:[(0,3,2),(3,1,2)],2:[(1,4,0),(4,2,0)],4:[(2,5,1),(5,0,1)],3:[(3,1,4),(0,3,4),(0,4,2)],6:[(4,2,5),(1,4,5),(1,5,0)],5:[(5,0,3),(2,5,3),(2,3,1)],7:[(0,3,5),(3,1,4),(5,4,2),(3,4,5)]};refinements=[]
for iteration in range(Q['local_edge_refinement_passes']):
 chosen={tuple(sorted((a,b)))for f in F for a,b in zip(f,f[1:]+f[:1])if near(V[a])or near(V[b])};mid={}
 for a,b in sorted(chosen):
  p=(V[a]+V[b])/2
  if V[a].y<=1e-9 and V[b].y<=1e-9:p.y=(S-P['face_sag_m'])-math.sqrt(S*S-p.x*p.x-p.z*p.z)
  mid[(a,b)]=len(V);V.append(p)
 nf=[];nn=[];nu=[];no=[]
 for f,ns,uv,oi in zip(F,NS,US,origin):
  a,b,c=f;ids=[a,b,c,mid.get(tuple(sorted((a,b)))),mid.get(tuple(sorted((b,c)))),mid.get(tuple(sorted((c,a))))];bits=sum((1<<k)for k in range(3)if ids[3+k]is not None);n=ns+[(ns[0]+ns[1]).normalized(),(ns[1]+ns[2]).normalized(),(ns[2]+ns[0]).normalized()];u=uv+[tuple((uv[0][k]+uv[1][k])/2 for k in range(2)),tuple((uv[1][k]+uv[2][k])/2 for k in range(2)),tuple((uv[2][k]+uv[0][k])/2 for k in range(2))]
  for tri in patterns[bits]:nf.append(tuple(ids[k]for k in tri));nn.append([n[k]for k in tri]);nu.append([u[k]for k in tri]);no.append(oi)
 refinements.append({'pass':iteration+1,'shared_split_edges':len(chosen),'triangles_before':len(F),'triangles_after':len(nf)});F,NS,US,origin=nf,nn,nu,no
# Smooth bounded U trim. Cap remains on its analytic sphere; rim reaches the unchanged rear plane.
def smooth(t):return t*t*t*(10+t*(-15+6*t))
def deform(v):
 x,y,z=v;r=math.hypot(x,z)
 if r<=Q['radial_transition_start_m']:return Vector(v)
 d=da(x,z)
 if abs(d)>=half:return Vector(v)
 w=math.cos(math.pi*d/(2*half))**2;t=max(0,min(1,(r-Q['radial_transition_start_m'])/(Q['radial_transition_end_m']-Q['radial_transition_start_m'])));rn=r-Q['depth_m']*w*smooth(t);a=rn/r;dy=math.sqrt(S*S-r*r)-math.sqrt(S*S-rn*rn);rear=max(0,min(1,y/P['rear_interface_y_m']));return Vector((x*a,y+dy*(1-smooth(rear)),z*a))
step=Q['Jacobian_finite_step_m'];J={};changed=[];min_det=1;max_move=0
for i,v in enumerate([Vector(v)for v in V]):
 p=deform(v);movement=(p-v).length
 if movement>1e-15:
  cols=[]
  for k in range(3):
   lo=Vector(v);hi=Vector(v);lo[k]-=step;hi[k]+=step;cols.append((deform(hi)-deform(lo))/(2*step))
  jac=Matrix([tuple(c)for c in cols]).transposed();min_det=min(min_det,jac.determinant());assert jac.determinant()>.05;J[i]=jac.inverted().transposed();changed.append(i);max_move=max(max_move,movement)
 V[i]=p
for f,ns in zip(F,NS):
 for k,i in enumerate(f):
  if i in J:ns[k]=(J[i]@ns[k]).normalized()
edges=Counter(tuple(sorted((a,b)))for f in F for a,b in zip(f,f[1:]+f[:1]));assert all(n in[1,2]for n in edges.values());adj=defaultdict(list)
for(a,b),n in edges.items():
 if n==1:adj[a].append(b);adj[b].append(a)
assert all(len(a)==2 for a in adj.values());todo=set(adj);loops=[]
while todo:
 seed=next(iter(todo));stack=[seed];component=set()
 while stack:
  i=stack.pop()
  if i in component:continue
  component.add(i);stack.extend(adj[i])
 todo-=component;loops.append(len(component))
assert len(loops)==2;areas=[];min_dot=1
for f,ns in zip(F,NS):
 a,b,c=[V[k]for k in f];cross=(b-a).cross(c-a);areas.append(cross.length/2);assert cross.length>0;min_dot=min(min_dot,*(cross.normalized().dot(n)for n in ns))
assert min(areas)>1e-16 and min_dot>.9
mesh=bpy.data.meshes.new('Original finite exterior with locally refined opposed notch');mesh.from_pydata(V,[],F);mesh.update();uv=mesh.uv_layers.new(name='Preserved source2 UV plus conforming local interpolation');normals=[]
for face in mesh.polygons:
 face.use_smooth=True
 for k,li in enumerate(face.loop_indices):uv.data[li].uv=US[face.index][k];normals.append(tuple(NS[face.index][k]))
mesh.normals_split_custom_set(normals)
for mat in old.materials:mesh.materials.append(mat)
counts=Counter(origin);untouched=0;max_reencode=0;changed_normal_corners=0
for i,(f,oi)in enumerate(zip(F,origin)):
 if counts[oi]!=1 or any(v>=len(oldV)or v in J for v in f):continue
 assert tuple(f)==oldF[oi]
 for k,li in enumerate(mesh.polygons[i].loop_indices):
  assert tuple(mesh.vertices[f[k]].co)==oldV[f[k]];assert tuple(mesh.uv_layers.active.data[li].uv)==oldUS[oi][k];delta=(mesh.corner_normals[li].vector-Vector(oldNS[oi][k])).length;max_reencode=max(max_reencode,delta);changed_normal_corners+=int(delta!=0)
 untouched+=1
ob.data=mesh;ob.name='Lens exterior with top mouth and opposed notch - estimated';ob['scope']='Only opposed boundary feature, full profile/back/scale/currentRDC unknown';ob['still_unmade']='Broad optical zones, fine peripheral zones and untranscribed molded marks';ob['hidden']='No prescription, reflector, socket, rear lug or approval marks';source=H/'indicator-front-lens-study-v3.blend';glb=H/'indicator-front-lens-study-v3.glb';bpy.context.preferences.filepaths.save_version=0;bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);root=ob.parent;root.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True);bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_extras=True);assert sha(src0)==base['source_sha256']
r={'schema':1,'source_sha256':sha(source),'export_sha256':sha(glb),'builder_sha256':sha(Path(__file__)),'parameters_sha256':sha(H/'parameters-study-v3.json'),'baseline_source_sha256':base['source_sha256'],'baseline_export_sha256':base['export_sha256'],'object':ob.name,'objects':[ob.name],'root':root.name,'collection':base['collection'],'vertices':len(V),'triangles':len(F),'local_refinement':refinements,'deformed_vertices':len(changed),'maximum_actual_vertex_displacement_m':max_move,'minimum_sampled_deformation_Jacobian_determinant':min_det,'minimum_source_triangle_area_m2':min(areas),'minimum_pre_encoding_face_corner_normal_dot':min_dot,'boundary_loops_vertex_counts':loops,'edge_valence_counts':dict(Counter(edges.values())),'unsubdivided_undeformed_triangles_with_source_P_UV_exact':untouched,'unaffected_normal_reencoding_max_vector_delta':max_reencode,'unaffected_normal_reencoding_changed_corners':changed_normal_corners,'normal_method':'Local numerical Jacobian inverse transpose, old per-corner normals where identity; source re-encoding quantified, not bit-equivalence asserted','scope':'Only opposed notch, full cut/back/scale estimated; optical zones and marks remain unmade','external_libraries':[],'external_images':[],'installation_transform':None,'complete_lens':False,'art_accepted':False};(O/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');print('NOTCH3_BUILT',r['source_sha256'],r['export_sha256'],r['triangles'],min_dot,max_reencode)
