"""One exterior connection hypothesis after exact-source whole SNS gap diagnostic."""
import bpy, math, json, hashlib
from pathlib import Path
from collections import Counter
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/rear-sns-body-end-closure-study-v1';O.mkdir(parents=True,exist_ok=True)
P=json.loads((H/'parameters-study-v1.json').read_text());assert(R/'creative/research/rear-sns-body-end-closure/G0-G2-plan-v1.json').exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
profile=[]
def point(r,z,dr,dz):
 length=math.hypot(dr,dz);dr/=length;dz/=length
 if profile and abs(profile[-1][0]-r)<1e-12 and abs(profile[-1][1]-z)<1e-12:
  assert math.hypot(profile[-1][2]-dr,profile[-1][3]-dz)<1e-6;return
 profile.append((r,z,dr,dz))
def arc(r,z,rad,a,b,n=12):
 for k in range(n+1):
  v=a+(b-a)*k/n;co=math.cos(v);si=math.sin(v);co=0 if abs(co)<1e-14 else co;si=0 if abs(si)<1e-14 else si;point(r+rad*co,z+rad*si,-si,co)
def cubic(A,B,C,D,n=24):
 for k in range(n+1):
  t=k/n;u=1-t;v=[u**3*A[i]+3*u*u*t*B[i]+3*u*t*t*C[i]+t**3*D[i]for i in range(2)];d=[3*u*u*(B[i]-A[i])+6*u*t*(C[i]-B[i])+3*t*t*(D[i]-C[i])for i in range(2)];point(*v,*d)
ri=P['inner_radius_m'];ro=P['outer_radius_m'];zt=P['top_z_m'];zb=P['bottom_z_m'];rc=P['round_m'];sr=P['lower_skirt_radius_m'];br=P['boss_outer_radius_m'];bt=P['boss_top_z_m'];outer_round=.0004
point(ro-outer_round,zt,-1,0);point(.0095,zt,-1,0)
cubic((.0095,zt),(.0081,zt),(br,.0015),(br,bt-rc),P['curve_samples'])
arc(br-rc,bt-rc,rc,0,math.pi/2)
point(ri+rc,bt,-1,0);arc(ri+rc,bt-rc,rc,math.pi/2,math.pi)
point(ri,zb+rc,0,-1);arc(ri+rc,zb+rc,rc,math.pi,3*math.pi/2)
point(sr-rc,zb,1,0);arc(sr-rc,zb+rc,rc,3*math.pi/2,2*math.pi)
point(sr,-.0068,0,1)
cubic((sr,-.0068),(sr,-.0054),(ro-.0019,-.0045),(ro-.0004,-.0043),P['curve_samples'])
cubic((ro-.0004,-.0043),(ro,-.004246666666666667),(ro,-.0041),(ro,-.0039),P['curve_samples'])
point(ro,zt-outer_round,0,1);arc(ro-outer_round,zt-outer_round,outer_round,0,math.pi/2)
assert math.hypot(profile[-1][0]-profile[0][0],profile[-1][1]-profile[0][1])<1e-12;profile.pop()
N=P['angular_segments'];K=len(profile);V=[];VN=[]
for k in range(N):
    a=2*math.pi*k/N;c=math.cos(a);s=math.sin(a)
    for rr,z,dr,dz in profile:V.append((rr*c,rr*s,z));VN.append((dz*c,dz*s,-dr))
F=[];UV=[]
for a in range(N):
    for j in range(K):
        n=(j+1)%K;ids=[a*K+j,((a+1)%N)*K+j,((a+1)%N)*K+n,a*K+n];uv=[(a/N,j/K),((a+1)/N,j/K),((a+1)/N,(j+1)/K),(a/N,(j+1)/K)]
        for t in [(0,1,2),(0,2,3)]:F.append(tuple(ids[i]for i in t));UV.append([uv[i]for i in t])
edges=Counter(tuple(sorted((a,b)))for f in F for a,b in zip(f,f[1:]+f[:1]));assert set(edges.values())=={2};volume=sum(Vector(V[a]).dot(Vector(V[b]).cross(Vector(V[c])))/6 for a,b,c in F);assert volume>0
areas=[];mindot=1
for f in F:
    a,b,c=[Vector(V[i])for i in f];cross=(b-a).cross(c-a);areas.append(cross.length/2);mindot=min(mindot,*(cross.normalized().dot(Vector(VN[i]))for i in f))
assert min(areas)>1e-16 and mindot>.9
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.render.engine='CYCLES';sc.cycles.samples=12;sc.cycles.use_denoising=True;sc.cycles.denoiser='OPENIMAGEDENOISE';sc.cycles.denoising_use_gpu=False;sc.render.threads_mode='FIXED';sc.render.threads=1;bpy.context.view_layer.cycles.denoising_store_passes=True
C=bpy.data.collections.new('WEWA_REAR_SNS_BODY_END_CLOSURE');sc.collection.children.link(C);root=bpy.data.objects.new('REAR_SNS_BODY_END_CLOSURE_UNPLACED_DATUM',None);C.objects.link(root);m=bpy.data.meshes.new('Original flattened rounded annular rim hypothesis');m.from_pydata(V,[],F);m.update();o=bpy.data.objects.new('SNS body-side support and rod-end cover - estimated continuation',m);C.objects.link(o);o.parent=root;uv=m.uv_layers.new(name='Original rim angular section UV');norms=[]
for p in m.polygons:
    p.use_smooth=True
    for k,li in enumerate(p.loop_indices):uv.data[li].uv=UV[p.index][k];norms.append(VN[m.loops[li].vertex_index])
m.normals_split_custom_set(norms);mat=bpy.data.materials.new('Neutral rim gray study - not paint');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.18,.18,.18,1);bs.inputs['Roughness'].default_value=.32;m.materials.append(mat)
o['scope']='Exterior support and rod-end cover hypothesis extending short rim fragments, not complete OEM section evidence';o['not_built']='Contact footprint/retention/hydraulic mechanism and actual servicepart count unknown';o['dimensions']='Authored radii/section/placement, not currentRDC cotes or installed fit'
world=bpy.data.worlds.new('Rim isolated neutral studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.16,.16,1);world.node_tree.nodes['Background'].inputs[1].default_value=.3;sc.world=world;target=Vector((0,0,-.003))
for name,loc,power,size in [('Key',(-.10,-.14,.10),1.6,.14),('Fill',(.12,-.05,.025),.6,.10),('Rim',(.05,.09,.06),1.1,.08)]:
    l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='RECTANGLE';l.size=size;l.size_y=size*.55;ob=bpy.data.objects.new(name,l);sc.collection.objects.link(ob);ob.location=Vector(loc)+Vector((0,0,.002));ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new('SNS rim study camera');ob=bpy.data.objects.new(cam.name,cam);sc.collection.objects.link(ob);ob.location=(.09,-.12,.072);ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler();cam.lens=70;cam.sensor_fit='HORIZONTAL';cam.sensor_width=36;cam.clip_start=.001;cam.clip_end=10;sc.camera=ob;sc.render.resolution_x=1000;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);root.select_set(True);bpy.context.view_layer.objects.active=o;src=H/'rear-sns-body-end-closure-study-v1.blend';glb=H/'rear-sns-body-end-closure-study-v1.glb';bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_extras=True)
report={'schema':1,'source_sha256':sha(src),'export_sha256':sha(glb),'builder_sha256':sha(Path(__file__)),'parameters_sha256':sha(H/'parameters-study-v1.json'),'object':o.name,'objects':[o.name],'root':root.name,'collection':C.name,'vertices':len(V),'triangles':len(F),'minimum_source_triangle_area_m2':min(areas),'minimum_source_normal_dot':mindot,'edge_valence_counts':dict(Counter(edges.values())),'positive_volume_m3':volume,'profile_RZ_dR_dZ':profile,'flat_face_normals':'Axial exactly at planar strips, no weighted smoothing over section corners','visible_scope':'Bounded external end closure and skirt, no hidden hydraulic or contact certification','continuation':'Full profile/circumference/back/inner passage explicitly authored to cover missing exterior; no OEM section or load path certification','installation_transform':None,'external_libraries':[],'external_images':[],'art_accepted':False};(O/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('SNS_RIM_STUDY_BUILT',report['source_sha256'],report['export_sha256'],len(F),mindot)
