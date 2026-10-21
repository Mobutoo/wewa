"""One observed broadblue annular appearance: original gray geometry first, depth/rear estimated."""
import bpy, math, json, hashlib
from pathlib import Path
from collections import Counter
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/rear-sns-opposite-blue-region-study-v1';O.mkdir(parents=True,exist_ok=True)
P=json.loads((H/'parameters-study-v1.json').read_text());assert(R/'creative/research/rear-sns-eyes/G0-G2-opposite-blue-region-plan-v1.json').exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ri=P['inner_radius_m'];ro=P['outer_radius_m'];zt=P['top_z_m'];zb=P['bottom_z_m'];rc=P['section_corner_radius_m'];assert ro-ri>2*rc and zt-zb>2*rc
profile=[]
for cr,cz,a0 in [(ro-rc,zt-rc,0),(ri+rc,zt-rc,math.pi/2),(ri+rc,zb+rc,math.pi),(ro-rc,zb+rc,3*math.pi/2)]:
    for k in range(P['quarter_round_samples']+1):
        a=a0+math.pi/2*k/P['quarter_round_samples'];c=math.cos(a);s=math.sin(a);c=0 if abs(c)<1e-14 else c;s=0 if abs(s)<1e-14 else s
        profile.append((cr+rc*c,cz+rc*s,-s,c))
N=P['angular_segments'];K=len(profile);V=[];VN=[]
for k in range(N):
    a=2*math.pi*k/N;c=math.cos(a);s=math.sin(a)
    for rr,z,dr,dz in profile:V.append((rr*c,rr*s,z));VN.append((dz*c,dz*s,-dr))
# Apply proper rotationX+90deg and authored eye-center translation to the actual mesh.
V=[(x,-z,P['eye_center_z_m']+y) for x,y,z in V]
VN=[(x,-z,y) for x,y,z in VN]
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
C=bpy.data.collections.new('WEWA_REAR_SNS_OPPOSITE_BLUE_REGION');sc.collection.children.link(C);root=bpy.data.objects.new('REAR_SNS_OPPOSITE_BLUE_REGION_UNPLACED_DATUM',None);C.objects.link(root);m=bpy.data.meshes.new('Original finite blue-appearance annulus hypothesis');m.from_pydata(V,[],F);m.update();o=bpy.data.objects.new('SNS opposite broadblue annular region - estimated continuation',m);C.objects.link(o);o.parent=root;uv=m.uv_layers.new(name='Original rim angular section UV');norms=[]
for p in m.polygons:
    p.use_smooth=True
    for k,li in enumerate(p.loop_indices):uv.data[li].uv=UV[p.index][k];norms.append(VN[m.loops[li].vertex_index])
m.normals_split_custom_set(norms);mat=bpy.data.materials.new('Neutral annular-region gray study - not composition');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.18,.18,.18,1);bs.inputs['Roughness'].default_value=.32;m.materials.append(mat)
o['scope']='Broadblue annular appearance only; full depth/back/section explicitly estimated';o['not_built']='No elastomer/cap function, separate OEM service boundary, hidden retention or embosseddetail inferred';o['dimensions']='Authored radii/section/placement, not currentRDC cotes or installed fit'
world=bpy.data.worlds.new('Rim isolated neutral studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.16,.16,1);world.node_tree.nodes['Background'].inputs[1].default_value=.3;sc.world=world;target=Vector((0,0,P['eye_center_z_m']))
for name,loc,power,size in [('Key',(-.06,-.09,-.05),.6,.08),('Fill',(.07,-.04,-.13),.25,.06),('Rim',(.03,.06,-.07),.5,.05)]:
    l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='RECTANGLE';l.size=size;l.size_y=size*.55;ob=bpy.data.objects.new(name,l);sc.collection.objects.link(ob);ob.location=Vector(loc)+Vector((0,0,P['eye_center_z_m']+.1115));ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new('SNS rim study camera');ob=bpy.data.objects.new(cam.name,cam);sc.collection.objects.link(ob);ob.location=(.060,-.110,.265);ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler();cam.lens=100;cam.sensor_fit='HORIZONTAL';cam.sensor_width=36;cam.clip_start=.001;cam.clip_end=10;sc.camera=ob;sc.render.resolution_x=1000;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);root.select_set(True);bpy.context.view_layer.objects.active=o;src=H/'rear-sns-opposite-blue-region-study-v1.blend';glb=H/'rear-sns-opposite-blue-region-study-v1.glb';bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_extras=True)
report={'schema':1,'source_sha256':sha(src),'export_sha256':sha(glb),'builder_sha256':sha(Path(__file__)),'parameters_sha256':sha(H/'parameters-study-v1.json'),'object':o.name,'objects':[o.name],'root':root.name,'collection':C.name,'vertices':len(V),'triangles':len(F),'minimum_source_triangle_area_m2':min(areas),'minimum_source_normal_dot':mindot,'edge_valence_counts':dict(Counter(edges.values())),'positive_volume_m3':volume,'profile_RZ_dR_dZ':profile,'flat_face_normals':'TransverseY exactly at planar lip faces after proper rotation, no weighted smoothing over rounds','visible_scope':'One broadblue appearance region, depth/back estimated; no physical function, composition or press-fit certification','continuation':'Full depth and rear lip are explicit authored smooth continuation estimates','installation_transform':None,'external_libraries':[],'external_images':[],'art_accepted':False};(O/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('SNS_BLUE_REGION_STUDY_BUILT',report['source_sha256'],report['export_sha256'],len(F),mindot)
