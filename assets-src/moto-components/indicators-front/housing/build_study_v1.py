"""Bounded outer hood and finite frontedge, not a measured OEM housing or hidden optical interior."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from collections import Counter
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/indicator-front-housing-study-v1';O.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();P=json.loads((H/'parameters-study-v1.json').read_text());plan=R/'creative/research/indicator-front-housing/G0-G2-housing-plan-v1.json';assert plan.exists();N=P['angular_segments'];NR=P['dome_rings'];r=P['rim_outer_radius_m'];ri=P['front_inner_radius_m'];y0=P['dome_start_y_m'];d=P['dome_depth_m'];di=d-P['wall_thickness_m'];b=P['rim_round_radius_m'];yc=P['front_interface_y_m']+b;assert yc<y0;profile=[]
# Backpole -> outer dome -> short collar -> rolled finite edge -> inner rendering continuation.
for j in range(1,NR+1):
 t=math.pi/2*(1-j/NR);normal=Vector((d*math.cos(t),r*math.sin(t))).normalized();profile.append((r*math.cos(t),y0+d*math.sin(t),normal.x,normal.y,'outer_dome'))
profile.append((r,yc,1,0,'outer_collar'))
for j in range(1,P['rim_round_rings']+1):
 t=math.pi*j/P['rim_round_rings'];a=(r-ri)/2;normal=Vector((b*math.cos(t),-a*math.sin(t))).normalized();profile.append(((r+ri)/2+a*math.cos(t),yc-b*math.sin(t),normal.x,normal.y,'rolled_edge'))
profile.append((ri,y0,-1,0,'inner_collar'))
for j in range(1,NR):
 t=math.pi/2*j/NR;normal=Vector((-di*math.cos(t),-ri*math.sin(t))).normalized();profile.append((ri*math.cos(t),y0+di*math.sin(t),normal.x,normal.y,'inner_rendering_continuation'))
V=[(0,y0+d,0)];NN=[(0,1,0)];S=[0];dist=0.;last=(0,y0+d)
for rr,yy,nr,ny,kind in profile:
 dist+=math.hypot(rr-last[0],yy-last[1]);S.append(dist);last=(rr,yy)
 for k in range(N):a=2*math.pi*k/N;V.append((rr*math.cos(a),yy,rr*math.sin(a)));NN.append((nr*math.cos(a),ny,nr*math.sin(a)))
dist+=math.hypot(last[0],y0+di-last[1]);pole=len(V);V.append((0,y0+di,0));NN.append((0,-1,0));F=[];UV=[]
for k in range(N):F.append((0,1+(k+1)%N,1+k));UV.append([((k+.5)/N,0),((k+1)/N,S[1]/dist),(k/N,S[1]/dist)])
for j in range(len(profile)-1):
 for k in range(N):
  a=1+j*N+k;b0=1+j*N+(k+1)%N;c=1+(j+1)*N+(k+1)%N;e=1+(j+1)*N+k;u0=k/N;u1=(k+1)/N;v0=S[j+1]/dist;v1=S[j+2]/dist;F.extend([(a,b0,c),(a,c,e)]);UV.extend([[(u0,v0),(u1,v0),(u1,v1)],[(u0,v0),(u1,v1),(u0,v1)]])
lastbase=1+(len(profile)-1)*N
for k in range(N):F.append((lastbase+k,lastbase+(k+1)%N,pole));UV.append([(k/N,S[-1]/dist),((k+1)/N,S[-1]/dist),((k+.5)/N,1)])
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=1;bpy.context.view_layer.cycles.denoising_store_passes=True;C=bpy.data.collections.new('WEWA_FRONT_INDICATOR_HOUSING_STUDY');s.collection.children.link(C);root=bpy.data.objects.new('FRONT_INDICATOR_HOUSING_UNPLACED_DATUM',None);C.objects.link(root);mesh=bpy.data.meshes.new('Original smooth hood with finite rolled mouth and bounded inner continuation');mesh.from_pydata(V,[],F);mesh.update();uv=mesh.uv_layers.new(name='Original continuous profile arclengthUV');normals=[]
for f in mesh.polygons:
 f.use_smooth=True
 for k,li in enumerate(f.loop_indices):uv.data[li].uv=UV[f.index][k];normals.append(NN[f.vertices[k]])
mesh.normals_split_custom_set(normals);ob=bpy.data.objects.new('Rounded indicator hood exterior - estimated continuation',mesh);C.objects.link(ob);ob.parent=root;mat=bpy.data.materials.new('Neutral housing study gray');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.18,.18,.18,1);bs.inputs['Roughness'].default_value=.3;mesh.materials.append(mat);ob['scope']=P['scope'];ob['back_and_inside']='Original bounded rendering continuation, not documented mold/backside';ob['still_unmade']='Visible stalk-root transition/fastener/interfaces, rightstalk and whole indicator review';edges=Counter(tuple(sorted((a,b)))for f in F for a,b in zip(f,f[1:]+f[:1]));assert set(edges.values())=={2};min_dot=1.;min_area=1.;volume=0.
for f in mesh.polygons:
 a,b0,c=[mesh.vertices[k].co for k in f.vertices];cross=(b0-a).cross(c-a);assert cross.length>0;min_area=min(min_area,cross.length/2);volume+=a.dot(b0.cross(c))/6;min_dot=min(min_dot,*(cross.normalized().dot(mesh.corner_normals[li].vector)for li in f.loop_indices))
assert min_area>1e-16 and min_dot>.98 and volume>0
world=bpy.data.worlds.new('Isolated neutral housing studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.16,.16,1);world.node_tree.nodes['Background'].inputs[1].default_value=.3;s.world=world;target=Vector((0,.017,0))
for name,loc,power,size in [('Key',(-.07,-.12,.12),1.5,.12),('Fill',(.10,-.07,.02),.8,.10),('Rim',(.05,.10,.09),1.,.08)]:
 light=bpy.data.lights.new(name,'AREA');light.energy=power;light.shape='RECTANGLE';light.size=size;light.size_y=size*.55;lamp=bpy.data.objects.new(name,light);s.collection.objects.link(lamp);lamp.location=loc;lamp.rotation_euler=(target-lamp.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new('Housing isolation camera');co=bpy.data.objects.new(cam.name,cam);s.collection.objects.link(co);co.location=(.08,.12,.07);co.rotation_euler=(target-co.location).to_track_quat('-Z','Y').to_euler();cam.lens=65;cam.sensor_fit='HORIZONTAL';cam.sensor_width=36;cam.clip_start=.001;cam.clip_end=10;s.camera=co;s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';source=H/'indicator-front-housing-study-v1.blend';glb=H/'indicator-front-housing-study-v1.glb';bpy.context.preferences.filepaths.save_version=0;bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);root.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True);bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_extras=True);report={'schema':1,'source_sha256':sha(source),'export_sha256':sha(glb),'builder_sha256':sha(Path(__file__)),'parameters_sha256':sha(H/'parameters-study-v1.json'),'plan_sha256':sha(plan),'object':ob.name,'objects':[ob.name],'root':root.name,'collection':C.name,'vertices':len(V),'triangles':len(F),'minimum_actual_source_triangle_area_m2':min_area,'minimum_actual_source_face_corner_normal_dot':min_dot,'all_actual_edges_valence2':True,'actual_signed_volume_m3':volume,'profile':profile,'external_libraries':[],'external_images':[],'scope':'Original estimated dome/finite mouth plus inner/back rendering continuation; no measured OEM housing/hidden optical assembly','remaining_observable':['Stalk-root exterior transition','Visible fastening and lens/stalk context interfaces'],'installation_transform':None,'complete_indicator':False,'art_accepted':False};(O/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('HOUSING_GRAY1_BUILT',report['source_sha256'],report['export_sha256'],len(F))
