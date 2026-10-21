"""One black eye/neck exterior, rounded finite-depth continuation; no sleeve or weld."""
import bpy,json,math,hashlib,sys
from pathlib import Path
from mathutils import Vector
from collections import Counter
H=Path(__file__).resolve().parent;R=H.parents[3];sys.path.insert(0,str(H));from outline_v1 import frame
O=R/'creative/reviews/rear-sns-opposite-eye-exterior-study-v2';O.mkdir(parents=True,exist_ok=True);P=json.loads((H/'parameters-study-v2.json').read_text());assert(R/'creative/research/rear-sns-eyes/G0-G2-opposite-eye-exterior-plan-v2.json').exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
N=P['angular_segments'];nr=P['quarter_round_samples'];rc=P['outer_edge_round_m'];br=P['inner_edge_round_m'];half=P['half_depth_y_m'];ri=P['inner_passage_radius_m'];cz=P['eye_center_z_m'];assert half>rc and half>br
audit=[frame(2*math.pi*k/(N*4),P) for k in range(N*4)];minradius=min(1/abs(f[-1])for f in audit if abs(f[-1])>1e-9);assert minradius>rc*1.1,('Inward offset could fold',minradius,rc)
profile=[(kind,k/nr)for kind in ['OF','OB','IB','IF']for k in range(nr+1)];K=len(profile);V=[];VN=[]
def snap(v):return 0 if abs(v)<1e-14 else v
for a in range(N):
    theta=2*math.pi*a/N;x,z,dx,dz,nx,nz,dnx,dnz,curv=frame(theta,P);s=math.sin(theta);c=math.cos(theta)
    for kind,u in profile:
        if kind in ['OF','OB']:
            beta=u*math.pi/2+(0 if kind=='OF'else math.pi/2);sb=snap(math.sin(beta));cb=snap(math.cos(beta));delta=-rc+rc*sb;y=(-half+rc if kind=='OF'else half-rc)-rc*cb
            v=(x+delta*nx,y,cz+z+delta*nz);pt=Vector((dx+delta*dnx,0,dz+delta*dnz));pu=Vector((rc*cb*nx,rc*sb,rc*cb*nz))
        else:
            beta=u*math.pi/2 if kind=='IB'else(1-u)*math.pi/2;sb=snap(math.sin(beta));cb=snap(math.cos(beta));rr=ri+br-br*sb
            if kind=='IB':y=half-br+br*cb;dr=-br*cb;dy=-br*sb
            else:y=-half+br-br*cb;dr=br*cb;dy=-br*sb
            v=(rr*s,y,cz+rr*c);pt=Vector((rr*c,0,-rr*s));pu=Vector((dr*s,dy,dr*c))
        V.append(v);VN.append(tuple(pt.cross(pu).normalized()))
# Proper rotationY180deg about authored eye center: determinant+1, winding retained.
# Only generator orientation is reused; independent parameters define this opposite end.
V=[(-x,y,2*cz-z) for x,y,z in V]
VN=[(-x,y,-z) for x,y,z in VN]
F=[];UV=[]
for a in range(N):
    for j in range(K):
        nj=(j+1)%K;ids=[a*K+j,((a+1)%N)*K+j,((a+1)%N)*K+nj,a*K+nj];uv=[(a/N,j/K),((a+1)/N,j/K),((a+1)/N,(j+1)/K),(a/N,(j+1)/K)]
        for t in [(0,1,2),(0,2,3)]:F.append(tuple(ids[i]for i in t));UV.append([uv[i]for i in t])
edges=Counter(tuple(sorted((a,b)))for f in F for a,b in zip(f,f[1:]+f[:1]));assert set(edges.values())=={2};volume=sum(Vector(V[a]).dot(Vector(V[b]).cross(Vector(V[c])))/6 for a,b,c in F);assert volume>0
areas=[];mindot=1
for f in F:
    a,b,c=[Vector(V[i])for i in f];cross=(b-a).cross(c-a);areas.append(cross.length/2);mindot=min(mindot,*(cross.normalized().dot(Vector(VN[i]))for i in f))
assert min(areas)>1e-16 and mindot>.9,(min(areas),mindot)
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.render.engine='CYCLES';sc.cycles.samples=12;sc.cycles.use_denoising=True;sc.cycles.denoiser='OPENIMAGEDENOISE';sc.cycles.denoising_use_gpu=False;sc.render.threads_mode='FIXED';sc.render.threads=1;bpy.context.view_layer.cycles.denoising_store_passes=True
C=bpy.data.collections.new('WEWA_REAR_SNS_OPPOSITE_EYE_EXTERIOR');sc.collection.children.link(C);root=bpy.data.objects.new('REAR_SNS_OPPOSITE_EYE_EXTERIOR_UNPLACED_DATUM',None);C.objects.link(root);m=bpy.data.meshes.new('Original eye neck and rounded passage exterior');m.from_pydata(V,[],F);m.update();o=bpy.data.objects.new('SNS opposite black eye and neck exterior - estimated',m);C.objects.link(o);o.parent=root;uv=m.uv_layers.new(name='Original eye angular section UV');norms=[]
for p in m.polygons:
    p.use_smooth=True
    for k,li in enumerate(p.loop_indices):uv.data[li].uv=UV[p.index][k];norms.append(VN[m.loops[li].vertex_index])
m.normals_split_custom_set(norms);mat=bpy.data.materials.new('Neutral eye gray study - not black composition');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.18,.18,.18,1);bs.inputs['Roughness'].default_value=.32;m.materials.append(mat);o['scope']='Continuous observable black eye/neck exterior; rear/depth/passage continuation fully estimated, no OEM material/part-boundary assertion';o['not_built']='Broadblue annular region and silver sleeve are NEXT separate units; no elastomer/cap function, weld or hidden press-fit invented'
world=bpy.data.worlds.new('Eye isolated neutral studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.16,.16,1);world.node_tree.nodes['Background'].inputs[1].default_value=.3;sc.world=world;target=Vector((0,0,cz))
for name,loc,power,size in [('Key',(-.08,-.12,-.025),1.6,.12),('Fill',(.10,-.06,-.13),.6,.10),('Rim',(.04,.08,-.055),1.1,.08)]:
    l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='RECTANGLE';l.size=size;l.size_y=size*.55;ob=bpy.data.objects.new(name,l);sc.collection.objects.link(ob);ob.location=Vector(loc)+Vector((0,0,cz+.1115));ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new('SNS eye study camera');ob=bpy.data.objects.new(cam.name,cam);sc.collection.objects.link(ob);ob.location=(0,-.16,cz);ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler();cam.lens=100;cam.sensor_fit='HORIZONTAL';cam.sensor_width=36;cam.clip_start=.001;cam.clip_end=10;sc.camera=ob;sc.render.resolution_x=1000;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);root.select_set(True);bpy.context.view_layer.objects.active=o;src=H/'rear-sns-opposite-eye-exterior-study-v2.blend';glb=H/'rear-sns-opposite-eye-exterior-study-v2.glb';bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_extras=True)
j={'schema':1,'source_sha256':sha(src),'export_sha256':sha(glb),'builder_sha256':sha(Path(__file__)),'outline_recipe_sha256':sha(H/'outline_v1.py'),'parameters_sha256':sha(H/'parameters-study-v2.json'),'object':o.name,'objects':[o.name],'root':root.name,'collection':C.name,'vertices':len(V),'triangles':len(F),'minimum_source_triangle_area_m2':min(areas),'minimum_source_normal_dot':mindot,'edge_valence_counts':dict(Counter(edges.values())),'positive_volume_m3':volume,'outer_curve_curvature_sample_count':len(audit),'minimum_sampled_abs_curvature_radius_m':minradius,'outer_inward_rounding_m':rc,'guard_scope':'Sampled source curve curvature guard, not a global exact certificate or OEM radius','front_back_flat_normals':'Exactly transverse±Y at planar strip endpoints; neck root plane exactly-Z after proper orientation','construction':'One C2 outline with finite rounded outer/passage surfaces, no CSG/remesh/global bevel/weld','installation_transform':None,'external_libraries':[],'external_images':[],'art_accepted':False};(O/'build-report.json').write_text(json.dumps(j,indent=2)+'\n');print('SNS_BODY_EYE_EXTERIOR_BUILT',j['source_sha256'],j['export_sha256'],len(F),mindot)
