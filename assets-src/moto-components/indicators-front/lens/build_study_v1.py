"""First bounded exterior lens skin. No unseen back, optical prescription or mount inferred."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from collections import Counter
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/indicator-front-lens-study-v1';O.mkdir(parents=True,exist_ok=True);P=json.loads((H/'parameters-study-v1.json').read_text());assert(R/'creative/research/indicator-front-lens/G0-G2-exterior-plan-v1.json').exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=P['face_radius_m'];s=P['face_sag_m'];sphere=(r*r+s*s)/(2*s);alpha=math.asin(r/sphere);rho=P['rim_fillet_radius_m'];profile=[]
for i in range(1,P['cap_radial_rings']+1):
 a=alpha*i/P['cap_radial_rings'];profile.append((sphere*math.sin(a),(sphere-s)-sphere*math.cos(a),math.cos(a),math.sin(a)))
for i in range(1,P['fillet_rings']+1):
 a=alpha+(math.pi/2-alpha)*i/P['fillet_rings'];profile.append((r+rho*(math.sin(a)-math.sin(alpha)),rho*(math.cos(alpha)-math.cos(a)),math.cos(a),math.sin(a)))
rr,yy,_,_=profile[-1]
assert P['rear_interface_y_m']>yy
for i in range(1,P['wall_rings']+1):profile.append((rr,yy+(P['rear_interface_y_m']-yy)*i/P['wall_rings'],0,1))
N=P['angular_segments'];V=[(0,-s,0)];normals=[(0,-1,0)];distances=[];last=(0,-s);distance=0
for radial,y,dr,dy in profile:
 distance+=math.hypot(radial-last[0],y-last[1]);distances.append(distance);last=(radial,y)
 for k in range(N):
  a=2*math.pi*k/N;c=math.cos(a);z=math.sin(a);V.append((radial*c,y,radial*z));normals.append(tuple(Vector((dy*c,-dr,dy*z)).normalized()))
F=[]
for k in range(N):F.append((0,1+k,1+(k+1)%N))
for i in range(len(profile)-1):
 for k in range(N):
  a=1+i*N+k;b=1+(i+1)*N+k;c=1+(i+1)*N+(k+1)%N;d=1+i*N+(k+1)%N;F.extend([(a,b,c),(a,c,d)])
UV=[(.5,.5)]
for i in range(len(profile)):
 w=.49*distances[i]/distances[-1]
 for k in range(N):a=2*math.pi*k/N;UV.append((.5+w*math.cos(a),.5+w*math.sin(a)))
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.render.engine='CYCLES';sc.cycles.samples=12;sc.cycles.use_denoising=True;sc.cycles.denoiser='OPENIMAGEDENOISE';sc.cycles.denoising_use_gpu=False;sc.render.threads_mode='FIXED';sc.render.threads=1;bpy.context.view_layer.cycles.denoising_store_passes=True;C=bpy.data.collections.new('WEWA_FRONT_INDICATOR_LENS_STUDY');sc.collection.children.link(C);root=bpy.data.objects.new('FRONT_INDICATOR_LENS_UNPLACED_DATUM',None);C.objects.link(root);m=bpy.data.meshes.new('Estimated convex cap and tangent finite rim skin');m.from_pydata(V,[],F);m.update();o=bpy.data.objects.new('Related lens gross exterior skin - estimated incomplete',m);C.objects.link(o);o.parent=root;uv=m.uv_layers.new(name='Original arclength disk UV');custom=[]
for p in m.polygons:
 p.use_smooth=True
 for li in p.loop_indices:vid=m.loops[li].vertex_index;uv.data[li].uv=UV[vid];custom.append(normals[vid])
m.normals_split_custom_set(custom);mat=bpy.data.materials.new('Neutral lens gray study - no amber or optical claims');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.18,.18,.18,1);bs.inputs['Roughness'].default_value=.32;m.materials.append(mat);o['scope']=P['scope'];o['dimensions']='Authored estimates only';o['interface']='One intentional rear boundary, no hidden inner wall or seat';world=bpy.data.worlds.new('Isolated neutral lens studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.16,.16,1);world.node_tree.nodes['Background'].inputs[1].default_value=.3;sc.world=world;target=Vector((0,0,0))
for name,loc,power,size in [('Key',(-.06,-.14,.11),1.5,.12),('Fill',(.10,-.08,.03),.8,.10),('Rim',(.06,.05,.09),1.0,.08)]:
 l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='RECTANGLE';l.size=size;l.size_y=size*.55;a=bpy.data.objects.new(name,l);sc.collection.objects.link(a);a.location=loc;a.rotation_euler=(target-a.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new('Lens exterior study camera');a=bpy.data.objects.new(cam.name,cam);sc.collection.objects.link(a);a.location=(.075,-.145,.075);a.rotation_euler=(target-a.location).to_track_quat('-Z','Y').to_euler();cam.lens=65;cam.sensor_fit='HORIZONTAL';cam.sensor_width=36;cam.clip_start=.001;cam.clip_end=10;sc.camera=a;sc.render.resolution_x=1000;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';bpy.ops.object.select_all(action='DESELECT');o.select_set(True);root.select_set(True);bpy.context.view_layer.objects.active=o;src=H/'indicator-front-lens-study-v1.blend';glb=H/'indicator-front-lens-study-v1.glb';bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_extras=True)
edges=Counter(tuple(sorted((a,b)))for f in F for a,b in zip(f,f[1:]+f[:1]));boundary=[e for e,n in edges.items()if n==1];assert len(boundary)==N and all(n in[1,2]for n in edges.values());areas=[p.area for p in m.polygons];assert min(areas)>0;report={'schema':1,'source_sha256':sha(src),'export_sha256':sha(glb),'builder_sha256':sha(Path(__file__)),'parameters_sha256':sha(H/'parameters-study-v1.json'),'object':o.name,'objects':[o.name],'collection':C.name,'root':root.name,'profile_rings':len(profile),'angular_segments':N,'vertices':len(V),'triangles':len(F),'minimum_source_triangle_area_m2':min(areas),'intentional_boundary_edges':len(boundary),'expected_boundary_edges':N,'boundary_scope':'Open rear interface only; no inferred hidden inside/seat/back','construction_guard':'Monotone profile y and nondecreasing radius, convex cap, tangent fillet and finite peripheral wall','profile':profile,'external_images':[],'external_libraries':[],'installation_transform':None,'full_lens_or_exactRDC_completed':False,'art_accepted':False};(O/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('LENS_GROSS_STUDY_BUILT',report['source_sha256'],report['export_sha256'],len(F))
