"""Original upper/lateral skin study; no hidden tank pan or measured dimensions."""
import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/fuel-tank-shell-study-v1';O.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Section data are authored exploration values. Not manufacturer tank dimensions.
P=json.loads((H/'parameters-study-v1.json').read_text())
def slopes(xs,ys):
 ds=[(ys[i+1]-ys[i])/(xs[i+1]-xs[i])for i in range(len(xs)-1)];ss=[ds[0]]
 for i in range(1,len(xs)-1):
  if ds[i-1]*ds[i]<=0:ss.append(0.)
  else:
   a=xs[i]-xs[i-1];b=xs[i+1]-xs[i];w1=2*b+a;w2=b+2*a;ss.append((w1+w2)/(w1/ds[i-1]+w2/ds[i]))
 return ss+[ds[-1]]
def interp(xs,ys,t,start=None,end=None):
 ss=slopes(xs,ys)
 if start is not None:ss[0]=start
 if end is not None:ss[-1]=end
 k=next((i for i in range(len(xs)-1)if t<=xs[i+1]),len(xs)-2);h=xs[k+1]-xs[k];f=(t-xs[k])/h
 return(2*f**3-3*f*f+1)*ys[k]+(f**3-2*f*f+f)*h*ss[k]+(-2*f**3+3*f*f)*ys[k+1]+(f**3-f*f)*h*ss[k+1]
U=P['longitudinal_stations'];C=P['cross_profile']
def surface(u,v):
 vv=abs(v);sgn=-1 if v<0 else 1
 vals={k:interp(U['u'],U[k],u)for k in ['y','halfwidth','crown_z','lower_z','crown_sweep_y']}
 xf=interp(C['s'],C['halfwidth_fraction'],vv)
 zf=interp(C['s'],C['height_fraction'],vv,start=0)
 # A separately controlled longitudinal sweep bends front crown back; it is not an underside tunnel.
 y=vals['y']+vals['crown_sweep_y']*zf
 x=sgn*vals['halfwidth']*xf
 z=vals['lower_z']+(vals['crown_z']-vals['lower_z'])*zf
 return Vector((x,y,z))
def normal(u,v):
 e=1e-5;ua=max(0,u-e);ub=min(1,u+e);va=max(-1,v-e);vb=min(1,v+e)
 du=(surface(ub,v)-surface(ua,v))/(ub-ua);dv=(surface(u,vb)-surface(u,va))/(vb-va)
 return dv.cross(du).normalized()
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True;scene.cycles.denoiser='OPENIMAGEDENOISE';scene.render.threads_mode='FIXED';scene.render.threads=1
coll=bpy.data.collections.new('WEWA_FUEL_TANK_UPPER_SKIN_STUDY');scene.collection.children.link(coll)
root=bpy.data.objects.new('FUEL_TANK_SKIN_ESTIMATED_DATUM',None);coll.objects.link(root)
nu=P['grid']['longitudinal'];nv=P['grid']['cross'];thick=P['skin_thickness_m'];verts=[];norm=[];faces=[];uvs=[];regions=[]
for i in range(nu+1):
 u=i/nu
 for j in range(nv+1):
  v=-1+2*j/nv;verts.append(surface(u,v));norm.append(normal(u,v))
n=len(verts);verts +=[verts[i]-thick*norm[i]for i in range(n)]
def f(ix,uv,r):faces.append(ix);uvs.append(uv);regions.append(r)
for i in range(nu):
 for j in range(nv):
  a=i*(nv+1)+j;b=a+1;c=a+nv+1;d=c+1;u0=i/nu;u1=(i+1)/nu;v0=j/nv;v1=(j+1)/nv
  f((a,b,d),[(u0,v0),(u0,v1),(u1,v1)],0);f((a,d,c),[(u0,v0),(u1,v1),(u1,v0)],0)
  f((n+a,n+d,n+b),[(u0,v0),(u1,v1),(u0,v1)],1);f((n+a,n+c,n+d),[(u0,v0),(u1,v0),(u1,v1)],1)
# Ordered perimeter of the open skin parameter domain. This closes wall thickness only.
edge=list(range(nv+1))+[i*(nv+1)+nv for i in range(1,nu+1)]+[nu*(nv+1)+j for j in range(nv-1,-1,-1)]+[i*(nv+1)for i in range(nu-1,0,-1)]
for k,a in enumerate(edge):
 b=edge[(k+1)%len(edge)];s0=k/len(edge);s1=(k+1)/len(edge)
 f((a,n+b,b),[(s0,0),(s1,1),(s1,0)],2);f((a,n+a,n+b),[(s0,0),(s0,1),(s1,1)],2)
mesh=bpy.data.meshes.new('Explicit Hermite skin with finite declared boundary');mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new('Tank upper and lateral skin - estimated shape study',mesh);coll.objects.link(obj);obj.parent=root
mat=bpy.data.materials.new('Neutral gray inspection - not final tankpaint');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.18,.18,.18,1);bs.inputs['Roughness'].default_value=.32;bs.inputs['Metallic'].default_value=0;mesh.materials.append(mat)
uv=mesh.uv_layers.new(name='Surface parameter UV original')
loopnorm=[]
for p in mesh.polygons:
 p.use_smooth=p.index<len(regions)and regions[p.index]<2
 for k,l in enumerate(p.loop_indices):
  uv.data[l].uv=uvs[p.index][k]
  vi=mesh.loops[l].vertex_index;loopnorm.append(tuple(norm[vi]if regions[p.index]==0 else -norm[vi-n]if regions[p.index]==1 else p.normal))
mesh.normals_split_custom_set(loopnorm)
region=mesh.attributes.new('SKIN_REGION','INT','FACE')
for i,x in enumerate(regions):region.data[i].value=x
obj['scope']='Visible upper/lateral skin only; front/rear/bottom boundaries estimated. No lowerpan/tunnel or fluid volume.';obj['reference']='RDC125HD photos and related52PF1825, no exactcode confirmation';obj['dimensions']='Authored exploration parameters, not measured tank cotes'
world=bpy.data.worlds.new('Neutral studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1);world.node_tree.nodes['Background'].inputs[1].default_value=.3;scene.world=world
for name,loc,energy,size in [('Key',(-.5,-.6,.65),55,.55),('Fill',(.65,.10,.25),25,.6),('Strip',(.05,.7,.5),45,.35)]:
 light=bpy.data.lights.new(name,'AREA');light.energy=energy;light.shape='RECTANGLE';light.size=size;light.size_y=.18 if name=='Strip'else size;o=bpy.data.objects.new(name,light);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,.12,-.23))-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new('Study camera');co=bpy.data.objects.new('Study camera',cam);scene.collection.objects.link(co);co.location=(.85,-.8,.5);co.rotation_euler=(Vector((0,.12,-.23))-co.location).to_track_quat('-Z','Y').to_euler();cam.lens=60;cam.clip_start=.001;cam.clip_end=20;scene.camera=co;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.render.resolution_x=1000;scene.render.resolution_y=800;scene.render.resolution_percentage=100
bpy.context.view_layer.objects.active=obj;bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);root.select_set(True)
source=H/'fuel-tank-shell-study-v1.blend';export=H/'fuel-tank-shell-study-v1.glb';bpy.ops.wm.save_as_mainfile(filepath=str(source));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_extras=True)
areas=[p.area for p in mesh.polygons];from collections import Counter
edges=Counter(tuple(sorted((a,b)))for face in faces for a,b in zip(face,face[1:]+face[:1]));vol=sum(Vector(verts[a]).dot(Vector(verts[b]).cross(Vector(verts[c])))/6 for a,b,c in faces)
report={'schema':1,'source_sha256':sha(source),'export_sha256':sha(export),'parameters_sha256':sha(H/'parameters-study-v1.json'),'builder_sha256':sha(Path(__file__)),'object':obj.name,'collection':coll.name,'vertices':len(verts),'triangles':len(faces),'exact_zero_area_triangles':sum(a==0 for a in areas),'minimum_triangle_area_m2':min(areas),'wall_volume_m3':vol,'volume_is':'Skin material only, no tankcapacity inferred','non_two_face_edges':sum(c!=2 for c in edges.values()),'external_libraries':len(bpy.data.libraries),'external_images':[],'normals':'Parametric surface finite derivative, flat boundary thickness faces; not corrected output buffers','included':'Top and lateral skin with explicit cut boundaries','excluded':['Fluid volume','Tunnel','Lowerpan','Hidden mount','Filler neck pending detailstage','Red/WEWA pending grayreview'],'actual_dimensions_measured':False,'G2_passed':False,'art_accepted':False}
assert min(areas)>0 and vol>0 and not report['non_two_face_edges'];(O/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('TANK_BUILD',json.dumps(report))
