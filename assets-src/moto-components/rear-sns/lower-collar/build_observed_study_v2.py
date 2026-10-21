"""One PF-E1 collar edge fragment; finite-sector study, not full circumference."""
import bpy, json, math, hashlib
from pathlib import Path
from collections import Counter
from mathutils import Vector

H=Path(__file__).resolve().parent; R=H.parents[3]
O=R/'creative/reviews/rear-sns-lower-collar-observed-study-v2'; O.mkdir(parents=True,exist_ok=True)
P=json.loads((H/'parameters-observed-study-v2.json').read_text())
assert (R/'creative/research/rear-sns-collar/G0-G2-observed-fragments-plan-v2.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
A=P['angular_samples']; W=P['wall_samples']; L=P['free_lip_halfround_samples']
t0=math.radians(P['theta_start_degrees']); span=math.radians(P['theta_end_degrees'])-t0
r0=P['lower_outer_radius_m']; r1=P['upper_outer_radius_m']; thick=P['radial_wall_thickness_m']; rho=thick/2; top=P['top_z_m']
def smooth(t): return t**3*(10+t*(-15+6*t))
def dsmooth(t): return 30*t*t*(t-1)**2
def edge(t):
    theta_degrees=P['theta_start_degrees']+(P['theta_end_degrees']-P['theta_start_degrees'])*t
    seg=next((s for s in P['edge_fragments'] if theta_degrees<=s['theta1_degrees']+1e-10),P['edge_fragments'][-1])
    width=math.radians(seg['theta1_degrees']-seg['theta0_degrees']); u=max(0,min(1,(theta_degrees-seg['theta0_degrees'])/(seg['theta1_degrees']-seg['theta0_degrees'])))
    dz=seg['z1_m']-seg['z0_m'];h=seg['recess_height_m']
    return seg['z0_m']+dz*smooth(u)+h*64*u**3*(1-u)**3,(dz*dsmooth(u)+h*192*u*u*(1-u)**2*(1-2*u))/width
# Profile follows outer wall upwards, top strip, inner wall downwards and rounded free lip.
profile=[('outer',i/W) for i in range(W+1)]+[('inner',i/W) for i in range(W,-1,-1)]+[('lip',i/L) for i in range(1,L)]
K=len(profile); V=[]
def coords(kind,u,t):
    ez,ed=edge(t)
    if kind in ('outer','inner'):
        q=u; rr=r0+(r1-r0)*smooth(q)-(thick if kind=='inner' else 0)
        return rr,ez*(1-q)+top*q
    beta=math.pi*(1-u)
    return r0-rho+rho*math.cos(beta),ez-rho*math.sin(beta)
def point(rr,z,theta): return (rr*math.sin(theta),-rr*math.cos(theta),z)
for a in range(A+1):
    t=a/A; theta=t0+span*t
    for kind,u in profile:
        rr,z=coords(kind,u,t); V.append(point(rr,z,theta))
F=[]; UV=[]; CN=[]
def normal(section,u,t):
    theta=t0+span*t; ez,ed=edge(t)
    if section=='outer':
        rr,z=coords('outer',u,t); ru=(r1-r0)*dsmooth(u); zu=top-ez; zt=ed*(1-u)
    elif section=='inner':
        rr,z=coords('inner',u,t); ru=-(r1-r0)*dsmooth(u); zu=-(top-ez); zt=ed*(1-u)
    elif section=='top': rr=r1-thick*u; ru=-thick; zu=0; zt=0
    else:
        beta=math.pi*(1-u); rr=r0-rho+rho*math.cos(beta); ru=rho*math.pi*math.sin(beta); zu=rho*math.pi*math.cos(beta); zt=ed
    pt=Vector((rr*math.cos(theta),rr*math.sin(theta),zt)); pu=Vector((ru*math.sin(theta),-ru*math.cos(theta),zu))
    return tuple(pt.cross(pu).normalized())
def add(ids,uv,ns): F.append(tuple(ids)); UV.append(uv); CN.append(ns)
for a in range(A):
    for j in range(K):
        n=(j+1)%K
        if j<W: sec='outer'; u0=j/W; u1=(j+1)/W
        elif j==W: sec='top'; u0=0; u1=1
        elif j<2*W+1: sec='inner'; u0=(2*W+1-j)/W; u1=u0-1/W
        else: sec='lip'; u0=(j-(2*W+1))/L; u1=u0+1/L
        ids=[a*K+j,(a+1)*K+j,(a+1)*K+n,a*K+n]
        uvs=[(a/A,j/K),((a+1)/A,j/K),((a+1)/A,(j+1)/K),(a/A,(j+1)/K)]
        ns=[normal(sec,u0,a/A),normal(sec,u0,(a+1)/A),normal(sec,u1,(a+1)/A),normal(sec,u1,a/A)]
        for tri in [(0,1,2),(0,2,3)]:add([ids[i] for i in tri],[uvs[i]for i in tri],[ns[i]for i in tri])
# Explicit angular study-cut caps, sharing every wall/lip boundary vertex.
for a,sign in [(0,-1),(A,1)]:
    theta=t0+span*a/A; ez,_=edge(a/A); center=len(V);V.append(point(r0-rho,ez,theta)); expected=Vector((sign*math.cos(theta),sign*math.sin(theta),0))
    def cap(ids):
        p,q,r=[Vector(V[i]) for i in ids]
        if (q-p).cross(r-p).dot(expected)<0:ids=list(reversed(ids))
        uv=[]
        for i in ids:
            p=V[i];rad=p[0]*math.sin(theta)-p[1]*math.cos(theta);uv.append(((rad-r0)/(r1-r0+thick),(p[2]-P['free_edge_end_z_m'])/(top-P['free_edge_end_z_m'])))
        add(ids,uv,[tuple(expected)]*3)
    b=a*K; inner=lambda i:b+2*W+1-i
    cap([b,b+1,center]);cap([b+1,inner(1),center]);cap([inner(1),inner(0),center])
    for i in range(1,W):cap([b+i,b+i+1,inner(i+1)]);cap([b+i,inner(i+1),inner(i)])
    lip=[inner(0)]+[b+j for j in range(2*W+2,K)]+[b]
    for p,q in zip(lip,lip[1:]):cap([center,p,q])
edges=Counter(tuple(sorted((a,b)))for f in F for a,b in zip(f,f[1:]+f[:1])); assert set(edges.values())=={2}
volume=sum(Vector(V[a]).dot(Vector(V[b]).cross(Vector(V[c])))/6 for a,b,c in F);assert volume>0
areas=[(Vector(V[b])-Vector(V[a])).cross(Vector(V[c])-Vector(V[a])).length/2 for a,b,c in F];assert min(areas)>1e-16
mindot=min((Vector(V[b])-Vector(V[a])).cross(Vector(V[c])-Vector(V[a])).normalized().dot(Vector(n)) for f,ns in zip(F,CN)for a,b,c in[f]for n in ns);assert mindot>.9,mindot
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.render.engine='CYCLES';sc.cycles.samples=12;sc.cycles.use_denoising=True;sc.cycles.denoiser='OPENIMAGEDENOISE';sc.cycles.denoising_use_gpu=False;sc.render.threads_mode='FIXED';sc.render.threads=1;bpy.context.view_layer.cycles.denoising_store_passes=True
C=bpy.data.collections.new('WEWA_REAR_SNS_LOWER_COLLAR_ARC_STUDY');sc.collection.children.link(C);root=bpy.data.objects.new('REAR_SNS_LOWER_COLLAR_ARC_UNPLACED_DATUM',None);C.objects.link(root)
m=bpy.data.meshes.new('Original finite scalloped collar E1 sector');m.from_pydata(V,[],F);m.update();o=bpy.data.objects.new('PF-E1 E2 E3 collar edge sector - estimated',m);C.objects.link(o);o.parent=root;uv=m.uv_layers.new(name='Original collar sector profile UV');norms=[]
for p in m.polygons:
    p.use_smooth=True
    for k,li in enumerate(p.loop_indices):uv.data[li].uv=UV[p.index][k];norms.append(CN[p.index][k])
m.normals_split_custom_set(norms);mat=bpy.data.materials.new('Collar neutral gray study - not final paint');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.18,.18,.18,1);bs.inputs['Roughness'].default_value=.32;m.materials.append(mat)
o['scope']='Three observed PF-E1/E2/E3 edge hypotheses only; angular end cuts are study caps, not full collar or physical ends';o['unknowns']='Full circumference/count, section, actual seat/function/cotes/RDC identity';o['visible_not_built']='Upper transition fragments not yet constrained; E4 remains ambiguous'
world=bpy.data.worlds.new('Collar isolated neutral studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.16,.16,1);world.node_tree.nodes['Background'].inputs[1].default_value=.3;sc.world=world;target=Vector((-.011,-.014,-.014))
for name,loc,power,size in [('Key',(-.07,-.10,.06),.7,.08),('Fill',(.05,-.06,-.02),.3,.06),('Rim',(.03,.03,.04),.6,.04)]:
    l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='RECTANGLE';l.size=size;l.size_y=size*.55;ob=bpy.data.objects.new(name,l);sc.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new('Collar arc study camera');ob=bpy.data.objects.new(cam.name,cam);sc.collection.objects.link(ob);ob.location=(-.060,-.085,.018);ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler();cam.lens=70;cam.sensor_fit='HORIZONTAL';cam.sensor_width=36;cam.clip_start=.001;cam.clip_end=10;sc.camera=ob;sc.render.resolution_x=1000;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);root.select_set(True);bpy.context.view_layer.objects.active=o;src=H/'rear-sns-lower-collar-observed-study-v2.blend';glb=H/'rear-sns-lower-collar-observed-study-v2.glb';bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_extras=True)
report={'schema':1,'source_sha256':sha(src),'export_sha256':sha(glb),'builder_sha256':sha(Path(__file__)),'parameters_sha256':sha(H/'parameters-observed-study-v2.json'),'object':o.name,'objects':[o.name],'root':root.name,'collection':C.name,'vertices':len(V),'triangles':len(F),'minimum_source_triangle_area_m2':min(areas),'minimum_source_normal_dot':mindot,'edge_valence_counts':dict(Counter(edges.values())),'positive_volume_m3':volume,'intentional_study_caps':2,'construction':'Shared finite sector; analytic normals; one edge recess; rounded free lip; no CSG/bevel/remesh','authored_minimum_radial_clearance_vs_barrel_m':r0-thick-.0153,'full_collar_built':False,'observed_fragments_built':['PF-E1','PF-E2','PF-E3'],'installation_transform':None,'external_images':[],'external_libraries':[],'art_accepted':False}
(O/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('COLLAR_ONE_ARC_BUILT',report['source_sha256'],report['export_sha256'],len(F),mindot)
