"""One original related RH signal stalk exterior; covered interfaces intentionally open."""
import bpy,json,math,hashlib
from pathlib import Path
from collections import Counter
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/indicator-front-right-stalk-study-v1';O.mkdir(parents=True,exist_ok=True);P=json.loads((H/'parameters-study-v1.json').read_text());assert(R/'creative/research/indicator-front-right-stalk/G0-G2-profile-plan-v1.json').exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def smooth(t):return 6*t**5-15*t**4+10*t**3
def dsmooth(t):return 30*t*t*(t-1)*(t-1)
def blend(s,a,b,ra,rb):
 t=min(1.,max(0.,(s-a)/(b-a)));return ra+(rb-ra)*smooth(t),(rb-ra)*dsmooth(t)/(b-a)
def radius(s):
 b=P['main_body'];sh=P['shoulder'];n=P['neck'];st=P['head_stub']
 if s<=b['end_m']:return blend(s,b['start_m'],b['end_m'],b['radius_start_m'],b['radius_end_m'])
 if s<=sh['end_m']:return blend(s,sh['start_m'],sh['end_m'],b['radius_end_m'],sh['end_radius_m'])
 if s>=st['start_m']:return blend(s,st['start_m'],st['end_m'],n['radius_m'],st['end_radius_m'])
 r=n['radius_m'];der=0.
 for g in P['grooves']:
  d=s-g['center_m'];a=abs(d);lo=g['flat_half_width_m'];hi=g['half_width_m']
  if a<=lo:r-=g['depth_m']
  elif a<hi:
   t=(a-lo)/(hi-lo);r-=g['depth_m']*(1-smooth(t));der+=g['depth_m']*dsmooth(t)/(hi-lo)*(1 if d>0 else-1)
 return r,der
profile=[]
def add(s,r,tx,tr):
 if profile and abs(profile[-1][0]-s)<1e-12:return
 assert not profile or s>profile[-1][0];assert r>0;profile.append((s,r,tx,tr))
f=P['root_flare']
for k in range(f['quarter_segments']+1):
 a=math.pi*k/(2*f['quarter_segments']);add(f['length_m']*(1-math.cos(a)),f['start_radius_m']+(f['end_radius_m']-f['start_radius_m'])*math.sin(a),f['length_m']*math.sin(a),(f['end_radius_m']-f['start_radius_m'])*math.cos(a))
for tag in ['main_body','shoulder','neck','head_stub']:
 d=P[tag];start=d.get('start_m',f['length_m']);end=d['end_m'];count=d.get('samples',math.ceil((end-start)/d.get('axial_sample_m',.0001)))
 samples={start+(end-start)*k/count for k in range(count+1)}
 if tag=='neck':
  for g in P['grooves']:
   for delta in [-g['half_width_m'],-g['flat_half_width_m'],0,g['flat_half_width_m'],g['half_width_m']]:samples.add(g['center_m']+delta)
 for s in sorted(samples):r,der=radius(s);add(s,r,1.,der)
N=P['radial_segments'];verts=[];normal=[]
for s,r,tx,tr in profile:
 for k in range(N):
  a=2*math.pi*k/N;c=math.cos(a);z=math.sin(a);verts.append((-s,r*c,r*z));normal.append(tuple(Vector((tr,tx*c,tx*z)).normalized()))
faces=[];uvs=[];L=profile[-1][0]
for i in range(len(profile)-1):
 for k in range(N):
  nxt=(k+1)%N;a=i*N+k;b=i*N+nxt;c=(i+1)*N+k;d=(i+1)*N+nxt;u0=k/N;u1=(k+1)/N;v0=profile[i][0]/L;v1=profile[i+1][0]/L;faces.extend([(a,d,b),(a,c,d)]);uvs.extend([[(u0,v0),(u1,v1),(u1,v0)],[(u0,v0),(u0,v1),(u1,v1)]])
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.render.engine='CYCLES';sc.cycles.samples=12;sc.cycles.use_denoising=True;sc.cycles.denoiser='OPENIMAGEDENOISE';sc.cycles.denoising_use_gpu=False;sc.render.threads_mode='FIXED';sc.render.threads=1;bpy.context.view_layer.cycles.denoising_store_passes=True;C=bpy.data.collections.new('WEWA_FRONT_INDICATOR_RIGHT_STALK');sc.collection.children.link(C);root=bpy.data.objects.new('FRONT_INDICATOR_RH_STALK_DATUM',None);C.objects.link(root);m=bpy.data.meshes.new('Original loft with rounded root and three C2 valleys');m.from_pydata(verts,[],faces);m.update();o=bpy.data.objects.new('Related RH external grooved stalk skin - estimated',m);C.objects.link(o);o.parent=root;uv=m.uv_layers.new(name='Original circumferential UV');custom=[]
for p in m.polygons:
 p.use_smooth=True
 for k,li in enumerate(p.loop_indices):uv.data[li].uv=uvs[p.index][k];custom.append(normal[m.loops[li].vertex_index])
m.normals_split_custom_set(custom);mat=bpy.data.materials.new('Neutral stalk gray - not final polymer');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.18,.18,.18,1);bs.inputs['Roughness'].default_value=.32;m.materials.append(mat);o['scope']='External visible stalk skin only, two intentional interface cuts, no bore/back/retention peg inferred';o['identity']='RelatedPF401002RH appearance, exactcurrentRDC notcertified';o['dimensions']='Authored estimates, no partcotes';world=bpy.data.worlds.new('Neutral isolated stalk studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.16,.16,1);world.node_tree.nodes['Background'].inputs[1].default_value=.3;sc.world=world;target=Vector((-.032,0,0))
for name,loc,power,size in [('Key',(-.02,-.12,.11),1.5,.12),('Fill',(.10,.09,.06),.8,.10),('Rim',(.08,-.06,-.06),1.0,.08)]:
 l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='RECTANGLE';l.size=size;l.size_y=size*.55;a=bpy.data.objects.new(name,l);sc.collection.objects.link(a);a.location=loc;a.rotation_euler=(target-a.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new('Stalk study camera');a=bpy.data.objects.new(cam.name,cam);sc.collection.objects.link(a);a.location=(-.105,-.125,.075);a.rotation_euler=(target-a.location).to_track_quat('-Z','Y').to_euler();cam.lens=70;cam.sensor_fit='HORIZONTAL';cam.sensor_width=36;cam.clip_start=.001;cam.clip_end=10;sc.camera=a;sc.render.resolution_x=1000;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';bpy.ops.object.select_all(action='DESELECT');o.select_set(True);root.select_set(True);bpy.context.view_layer.objects.active=o;src=H/'indicator-front-right-stalk-study-v1.blend';glb=H/'indicator-front-right-stalk-study-v1.glb';bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_extras=True)
edges=Counter(tuple(sorted((a,b)))for f in faces for a,b in zip(f,f[1:]+f[:1]));boundary=[e for e,n in edges.items()if n==1];expected=2*N;assert len(boundary)==expected and all(n in[1,2]for n in edges.values());areas=[p.area for p in m.polygons];assert min(areas)>0;report={'schema':1,'source_sha256':sha(src),'export_sha256':sha(glb),'builder_sha256':sha(Path(__file__)),'parameters_sha256':sha(H/'parameters-study-v1.json'),'object':o.name,'objects':[o.name],'collection':C.name,'root':root.name,'profile_rings':len(profile),'radial_segments':N,'vertices':len(verts),'triangles':len(faces),'minimum_source_triangle_area_m2':min(areas),'exact_zero_source_area_triangles':0,'intentional_boundary_edges':len(boundary),'expected_boundary_edges':expected,'boundary_scope':'Two covered interface rings, no complete hidden solid/bore/retentionpeg inferred','self_intersection_construction_guard':'Strictly increasing axialS and positive radialR, one revolution shell only','profile_samples':profile,'external_images':[],'external_libraries':[],'source_axis':'-X from mount to hypotheticalRHhead, rootidentity no negativeobjectscale','working_family_equality_not_OEMsymmetry':True,'installation_transform':None,'full_indicator_or_exactRDC_completed':False,'art_accepted':False};(O/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('STALK_STUDY_BUILT',report['source_sha256'],report['export_sha256'],len(faces))
