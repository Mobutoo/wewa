"""Original fine peripheral rendering hypothesis, not an OEM optical prescription."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from collections import Counter,defaultdict
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/indicator-front-lens-study-v6';O.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();P=json.loads((H/'parameters-study-v6.json').read_text());Q=P['fine_periphery'];B=R/'creative/reviews/indicator-front-lens-study-v5';base=json.loads((B/'build-report.json').read_text());freeze=json.loads((B/'study-freeze-manifest.json').read_text());assert all(sha(R/f['path'])==f['sha256']for f in freeze['files']);plan=R/'creative/research/indicator-front-lens/fine-zone-plan-v6.json';assert plan.exists();source0=H/'indicator-front-lens-study-v5.blend';assert sha(source0)==base['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source0));ob=bpy.data.objects[base['object']];old=ob.data;V=[tuple(v.co)for v in old.vertices];F=[tuple(f.vertices)for f in old.polygons];NS=[[tuple(old.corner_normals[k].vector)for k in f.loop_indices]for f in old.polygons];US=[[tuple(old.uv_layers.active.data[k].uv)for k in f.loop_indices]for f in old.polygons];oldV=list(V);oldF=list(F);oldNS=list(NS);oldUS=list(US);origin=list(range(len(F)))
def smooth(t):return t*t*t*(10+t*(-15+6*t))
def weight(x,z):
 r=math.hypot(x,z)
 lo=max(0.,min(1.,(r-Q['radial_zero_inner_m'])/(Q['radial_full_inner_m']-Q['radial_zero_inner_m'])));hi=max(0.,min(1.,(r-Q['radial_full_outer_m'])/(Q['radial_zero_outer_m']-Q['radial_full_outer_m'])));w=smooth(lo)*(1-smooth(hi));d=math.hypot(x,z-P['pocket']['center_xz_m'][1]);u=max(0.,min(1.,(d-Q['mouth_exclusion_inner_radius_m'])/(Q['mouth_exclusion_outer_radius_m']-Q['mouth_exclusion_inner_radius_m'])));theta=math.atan2(z,x);nd=abs(math.atan2(math.sin(theta+math.pi/2),math.cos(theta+math.pi/2)));n=max(0.,min(1.,(math.degrees(nd)-Q['notch_exclusion_inner_degrees'])/(Q['notch_exclusion_outer_degrees']-Q['notch_exclusion_inner_degrees'])));return w*smooth(u)*smooth(n)
def offset(x,z):
 w=weight(x,z)
 if w==0:return 0.
 return -Q['normal_displacement_peak_m']*w*((1+math.cos(Q['original_rib_count']*math.atan2(z,x)))/2)**2

patterns={0:[(0,1,2)],1:[(0,3,2),(3,1,2)],2:[(1,4,0),(4,2,0)],4:[(2,5,1),(5,0,1)],3:[(3,1,4),(0,3,4),(0,4,2)],6:[(4,2,5),(1,4,5),(1,5,0)],5:[(5,0,3),(2,5,3),(2,3,1)],7:[(0,3,5),(3,1,4),(5,4,2),(3,4,5)]};ref=[]
for iteration in range(Q['conforming_refinement_passes']):
 def needs(i):
  x,y,z=V[i];r=math.hypot(x,z);return y<=Q['refinement_front_y_limit_m']and Q['refinement_inner_radius_m']<r<Q['refinement_outer_radius_m']
 def long_angular_edge(a,b):
  va,vb=V[a],V[b];t=math.atan2(va[2],va[0])-math.atan2(vb[2],vb[0]);d=abs(math.atan2(math.sin(t),math.cos(t)));return max(math.hypot(va[0],va[2]),math.hypot(vb[0],vb[2]))*d>Q['maximum_selected_edge_angular_length_m']
 chosen={tuple(sorted((a,b)))for f in F for a,b in zip(f,f[1:]+f[:1])if(needs(a)or needs(b))and long_angular_edge(a,b)};mid={}
 for a,b in sorted(chosen):mid[(a,b)]=len(V);V.append(tuple((V[a][k]+V[b][k])/2 for k in range(3)))
 nf=[];nn=[];nu=[];no=[]
 for f,ns,uv,oi in zip(F,NS,US,origin):
  a,b,c=f;ids=[a,b,c,mid.get(tuple(sorted((a,b)))),mid.get(tuple(sorted((b,c)))),mid.get(tuple(sorted((c,a))))];bits=sum(1<<k for k in range(3)if ids[3+k]is not None);n=ns+[tuple((Vector(ns[0])+Vector(ns[1])).normalized()),tuple((Vector(ns[1])+Vector(ns[2])).normalized()),tuple((Vector(ns[2])+Vector(ns[0])).normalized())];u=uv+[tuple((uv[0][k]+uv[1][k])/2 for k in range(2)),tuple((uv[1][k]+uv[2][k])/2 for k in range(2)),tuple((uv[2][k]+uv[0][k])/2 for k in range(2))]
  for tri in patterns[bits]:nf.append(tuple(ids[k]for k in tri));nn.append([n[k]for k in tri]);nu.append([u[k]for k in tri]);no.append(oi)
 ref.append({'pass':iteration+1,'shared_split_edges':len(chosen),'triangles_before':len(F),'triangles_after':len(nf)});F,NS,US,origin=nf,nn,nu,no
D={};max_shift=0.;step=Q['Jacobian_finite_step_m']
for i,(x,y,z)in enumerate(V):
 if y>Q['refinement_front_y_limit_m']:continue
 dy=offset(x,z)
 if dy==0:continue
 dx=(offset(x+step,z)-offset(x-step,z))/(2*step);dz=(offset(x,z+step)-offset(x,z-step))/(2*step);D[i]=(dx,dz);V[i]=(x,y+dy,z);max_shift=max(max_shift,abs(dy))
for f,ns in zip(F,NS):
 for k,i in enumerate(f):
  if i in D:dx,dz=D[i];nx,ny,nz=ns[k];ns[k]=tuple(Vector((nx-dx*ny,ny,nz-dz*ny)).normalized())
mesh=bpy.data.meshes.new('Original fine peripheral rendering zones - assignment estimated');mesh.from_pydata(V,[],F);mesh.update();uv=mesh.uv_layers.new(name='Preserved source5 UV plus conforming interpolation');normals=[]
for f in mesh.polygons:
 f.use_smooth=True
 for k,li in enumerate(f.loop_indices):uv.data[li].uv=US[f.index][k];normals.append(NS[f.index][k])
mesh.normals_split_custom_set(normals)
for m in old.materials:mesh.materials.append(m)
# RNA collection pointer may be invalidated by material append; re-fetch live UV layer for audit.
uv=mesh.uv_layers.active
areas=[];min_dot=1.;edges=Counter();actual_changed=0
for f in mesh.polygons:
 a,b,c=[mesh.vertices[k].co for k in f.vertices];cross=(b-a).cross(c-a);area=cross.length/2;assert area>1e-16;areas.append(area);min_dot=min(min_dot,*(cross.normalized().dot(mesh.corner_normals[li].vector)for li in f.loop_indices))
 for a,b in zip(tuple(f.vertices),tuple(f.vertices)[1:]+tuple(f.vertices)[:1]):edges[tuple(sorted((a,b)))]+=1
assert min_dot>.9 and all(n in[1,2]for n in edges.values());adj=defaultdict(list)
for(a,b),n in edges.items():
 if n==1:adj[a].append(b);adj[b].append(a)
assert all(len(x)==2 for x in adj.values());todo=set(adj);loops=[]
while todo:
 stack=[next(iter(todo))];comp=set()
 while stack:
  i=stack.pop()
  if i in comp:continue
  comp.add(i);stack.extend(adj[i])
 todo-=comp;loops.append(len(comp))
assert len(loops)==2
counts=Counter(origin);protected=0;maxNdelta=0.
for i,(f,oi)in enumerate(zip(F,origin)):
 if counts[oi]!=1 or any(k>=len(oldV)or k in D for k in f):continue
 assert f==oldF[oi]
 for k,li in enumerate(mesh.polygons[i].loop_indices):
  assert tuple(mesh.vertices[f[k]].co)==oldV[f[k]];assert tuple(uv.data[li].uv)==oldUS[oi][k],(i,oi,k,tuple(uv.data[li].uv),oldUS[oi][k]);maxNdelta=max(maxNdelta,(mesh.corner_normals[li].vector-Vector(oldNS[oi][k])).length)
 protected+=1
ob.data=mesh;ob.name='Lens fine peripheral zones rendering hypothesis - estimated';ob['scope']='Shallow original rendering relief; outer/inner assignment and optical prescription NOT certified';ob['still_unmade']='Untranscribed markings and amber/transmission';ob['hidden']='No reflector/bulb/socket or approval text';source=H/'indicator-front-lens-study-v6.blend';glb=H/'indicator-front-lens-study-v6.glb';bpy.context.preferences.filepaths.save_version=0;bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);root=ob.parent;root.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True);bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_extras=True);assert sha(source0)==base['source_sha256']
r={'schema':1,'source_sha256':sha(source),'export_sha256':sha(glb),'builder_sha256':sha(Path(__file__)),'parameters_sha256':sha(H/'parameters-study-v6.json'),'plan_sha256':sha(plan),'baseline_source_sha256':base['source_sha256'],'object':ob.name,'objects':[ob.name],'root':root.name,'collection':base['collection'],'vertices':len(V),'triangles':len(F),'conforming_refinement':ref,'deformed_vertices':len(D),'maximum_surface_shift_m':max_shift,'actual_minimum_source_triangle_area_m2':min(areas),'actual_minimum_source_face_corner_normal_dot':min_dot,'boundary_loops_vertex_counts':loops,'unsubdivided_undeformed_source5_triangles_P_UV_exact':protected,'protected_cornernormal_reencoding_max_vector_delta':maxNdelta,'normal_method':'Original source5 per-corner normals interpolated at conforming splits, inverse transpose of y-height-field shear using Float64 central differences; no export repair','scope':'Fine peripheral rendering zones plus prior broad bands; count/profile/face assignment estimated, amber/transmission not made','external_libraries':[],'external_images':[],'complete_lens':False,'art_accepted':False};(O/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');print('FINE6_BUILT',r['source_sha256'],r['export_sha256'],r['triangles'],min_dot)
