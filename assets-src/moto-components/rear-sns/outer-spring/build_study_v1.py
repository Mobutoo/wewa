"""One estimated SNS outer spring, original variable-pitch swept wire, no whole shock."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
from collections import Counter
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/rear-sns-outer-spring-study-v1';O.mkdir(parents=True,exist_ok=True);P=json.loads((H/'parameters-study-v1.json').read_text());assert(R/'creative/research/rear-sns-outer-spring/G0-G2-spring-plan-v1.json').exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();weights=[v*.001 for v in P['pitch_control_weights_mm']];turns=P['turns'];assert len(weights)==turns+1;tot=sum((a+b)/2 for a,b in zip(weights,weights[1:]));scale=P['centerline_height_m']/tot;prefix=[0]
for a,b in zip(weights,weights[1:]):prefix.append(prefix[-1]+(a+b)/2)
def law(t):
 i=min(turns-1,int(t));u=t-i;a=weights[i];b=weights[i+1];sm=u**3*(10+u*(-15+6*u));integ=u**6-3*u**5+2.5*u**4;z=scale*(prefix[i]+a*u+(b-a)*integ);slope=scale*(a+(b-a)*sm)/(2*math.pi);return z,slope
N=turns*P['samples_per_turn'];M=P['wire_segments'];rad=P['centerline_radius_m'];wire=P['wire_radius_m'];V=[];VN=[];centers=[];tangents=[]
for i in range(N+1):
 t=turns*i/N;theta=2*math.pi*t;z,slope=law(t);c=Vector((rad*math.cos(theta),rad*math.sin(theta),z));T=Vector((-rad*math.sin(theta),rad*math.cos(theta),slope)).normalized();A=Vector((math.cos(theta),math.sin(theta),0));B=T.cross(A).normalized();centers.append(c);tangents.append(T)
 for k in range(M):
  phi=2*math.pi*k/M;n=math.cos(phi)*A+math.sin(phi)*B;V.append(tuple(c+wire*n));VN.append(tuple(n))
# Conservative sampled inter-turn bound, independently of the surface shading.
kd=KDTree(len(centers))
for i,c in enumerate(centers):kd.insert(c,i)
kd.balance();minimum=float('inf');witness=None
for i,c in enumerate(centers):
 for co,j,dist in kd.find_range(c,.020):
  if abs(j-i)<P['samples_per_turn']//2:continue
  if dist<minimum:minimum=dist;witness=[i,j]
max_segment=max((a-b).length for a,b in zip(centers,centers[1:]));sample_bound=minimum-2*wire-max_segment;assert sample_bound>0,'Unresolved spring self contact';curvature_radius=[]
for i in range(1,N):
 a=(centers[i]-centers[i-1]);b=(centers[i+1]-centers[i]);bend=a.normalized().angle(b.normalized());curvature_radius.append((a.length+b.length)/2/bend if bend>1e-12 else 1e9)
assert min(curvature_radius)>wire
F=[];uvs=[];norm=[]
for i in range(N):
 for k in range(M):
  nk=(k+1)%M;a=i*M+k;b=i*M+nk;c=(i+1)*M+nk;d=(i+1)*M+k
  for f,uv in [((a,b,c),[(k/M,i/N),((k+1)/M,i/N),((k+1)/M,(i+1)/N)]),((a,c,d),[(k/M,i/N),((k+1)/M,(i+1)/N),(k/M,(i+1)/N)])]:
   ns=[VN[j]for j in f];cross=(Vector(V[f[1]])-Vector(V[f[0]])).cross(Vector(V[f[2]])-Vector(V[f[0]]))
   if cross.dot(sum((Vector(n)for n in ns),Vector()))<0:f=tuple(reversed(f));uv.reverse();ns.reverse()
   F.append(f);uvs.append(uv);norm.append(ns)
for end,ring,T in [(0,0,-tangents[0]),(1,N,tangents[-1])]:
 center=len(V);V.append(tuple(centers[ring]));
 for k in range(M):
  nk=(k+1)%M;f=(center,ring*M+k,ring*M+nk);uv=[(.5,.5),(.5+.49*math.cos(2*math.pi*k/M),.5+.49*math.sin(2*math.pi*k/M)),(.5+.49*math.cos(2*math.pi*(k+1)/M),.5+.49*math.sin(2*math.pi*(k+1)/M))];cross=(Vector(V[f[1]])-Vector(V[f[0]])).cross(Vector(V[f[2]])-Vector(V[f[0]]))
  if cross.dot(T)<0:f=tuple(reversed(f));uv.reverse()
  F.append(f);uvs.append(uv);norm.append([tuple(T)]*3)
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.render.engine='CYCLES';sc.cycles.samples=12;sc.cycles.use_denoising=True;sc.cycles.denoiser='OPENIMAGEDENOISE';sc.cycles.denoising_use_gpu=False;sc.render.threads_mode='FIXED';sc.render.threads=1;bpy.context.view_layer.cycles.denoising_store_passes=True;C=bpy.data.collections.new('WEWA_REAR_SNS_OUTER_SPRING');sc.collection.children.link(C);root=bpy.data.objects.new('REAR_SNS_OUTER_SPRING_UNPLACED_DATUM',None);C.objects.link(root);m=bpy.data.meshes.new('Original variable-pitch helix swept wire');m.from_pydata(V,[],F);m.update();o=bpy.data.objects.new('Related SNS black outer spring - estimated gray study',m);C.objects.link(o);o.parent=root;uv=m.uv_layers.new(name='Original axial wire UV');custom=[]
for p in m.polygons:
 p.use_smooth=True
 for k,li in enumerate(p.loop_indices):uv.data[li].uv=uvs[p.index][k];custom.append(norm[p.index][k])
m.normals_split_custom_set(custom);mat=bpy.data.materials.new('Neutral SNS outer spring gray - not final paint');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.18,.18,.18,1);bs.inputs['Roughness'].default_value=.32;m.materials.append(mat);o['scope']='One outer spring only, no inner spring, damper, cups, eyes or pair';o['dimensions']='All authored estimates; full turn count, handedness, endpoints and finish not certified';o['end_caps']='Flat computational closure, no measured grinding/contact';world=bpy.data.worlds.new('Isolated SNS spring studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.16,.16,1);world.node_tree.nodes['Background'].inputs[1].default_value=.3;sc.world=world;target=Vector((0,0,.095))
for name,loc,power,size in [('Key',(-.15,-.28,.25),7,.25),('Fill',(.21,-.12,.11),3,.21),('Rim',(.12,.15,.20),5,.18)]:
 l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='RECTANGLE';l.size=size;l.size_y=size*.55;a=bpy.data.objects.new(name,l);sc.collection.objects.link(a);a.location=loc;a.rotation_euler=(target-a.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new('SNS outer spring study camera');a=bpy.data.objects.new(cam.name,cam);sc.collection.objects.link(a);a.location=(.24,-.40,.25);a.rotation_euler=(target-a.location).to_track_quat('-Z','Y').to_euler();cam.lens=65;cam.sensor_fit='HORIZONTAL';cam.sensor_width=36;cam.clip_start=.001;cam.clip_end=10;sc.camera=a;sc.render.resolution_x=1000;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';bpy.ops.object.select_all(action='DESELECT');o.select_set(True);root.select_set(True);bpy.context.view_layer.objects.active=o;src=H/'rear-sns-outer-spring-study-v1.blend';glb=H/'rear-sns-outer-spring-study-v1.glb';bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_extras=True);edges=Counter(tuple(sorted((a,b)))for f in F for a,b in zip(f,f[1:]+f[:1]));assert all(n==2 for n in edges.values());report={'schema':1,'source_sha256':sha(src),'export_sha256':sha(glb),'builder_sha256':sha(Path(__file__)),'parameters_sha256':sha(H/'parameters-study-v1.json'),'object':o.name,'objects':[o.name],'root':root.name,'collection':C.name,'vertices':len(V),'triangles':len(F),'closed_edge_valence_all2':True,'minimum_source_triangle_area_m2':min(p.area for p in m.polygons),'centerline_samples':len(centers),'minimum_sampled_nonlocal_center_distance_m':minimum,'clearance_sample_witness':witness,'maximum_centerline_segment_m':max_segment,'conservative_sampled_interturn_clearance_bound_m':sample_bound,'minimum_sampled_centerline_curvature_radius_m':min(curvature_radius),'wire_radius_m':wire,'minimum_pitch_m_per_turn':min(weights)*scale,'end_caps':'Computational closure only, not actual hidden end grind or seat shape','spring_hand_turncount_dimensions':'Authored estimates, not certified PF/RDC','external_images':[],'external_libraries':[],'installation_transform':None,'full_SNS_completed':False,'art_accepted':False};(O/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('SNS_OUTER_SPRING_BUILT',report['source_sha256'],report['export_sha256'],len(F))
