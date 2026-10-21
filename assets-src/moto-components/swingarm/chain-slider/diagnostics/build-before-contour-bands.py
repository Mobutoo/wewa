"""Native finite ring/fork candidate, real voids/rounded sections; no imported mesh.
Endmouth paths and opposed running face unobserved: envelope only, not qualified.
"""
import bpy,bmesh,numpy as np,math,json,hashlib,sys
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/swingarm-chain-slider-v1';sys.path.insert(0,str(H));from profile_shape import shape,normal2,inside,distance,front_field
P=json.loads((H/'parameters.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();loops=shape(P);be=P['edge_radius_m_estimated'];width=P['axial_width_X_m_estimated'];normals=[normal2(a)for a in loops];caps=[a-be*n for a,n in zip(loops,normals)];points=[];edges=[]
# Every genuine boundary is constrained before interior samples.
for a in caps:
 j=len(points);points.extend(a.tolist());edges.extend((j+i,j+(i+1)%len(a))for i in range(len(a)))
def domain(q):
 keep=inside(q,caps[0])
 for hole in caps[1:]:keep&=~inside(q,hole)
 return keep
for pitch,detail in [(.0006,False),(.00020,True)]:
 y,z=np.meshgrid(np.arange(-.022+pitch*.31,.164,pitch),np.arange(-.022+pitch*.27,.023,pitch));q=np.column_stack([y.ravel(),z.ravel()]);q=q[domain(q)];d=distance(q,caps);q=q[(d>.00005)&((d<.0023)if detail else np.ones(len(q),bool))];points.extend(q.tolist())
unique=[];seen=set()
for a in points:
 k=tuple(np.round(a,10))
 if k not in seen:seen.add(k);unique.append(Vector(a))
print('SLIDER_CDT_INPUT',len(unique),flush=True);xy,_,faces,*_=delaunay_2d_cdt(unique,edges,[list(range(len(caps[0])))],1,1e-9,False);xy=np.asarray([a[:]for a in xy]);faces=np.asarray(faces,np.int64);assert faces.ndim==2 and faces.shape[1]==3;faces=faces[domain(xy[faces].mean(axis=1))];tri=xy[faces];cross=(tri[:,1,0]-tri[:,0,0])*(tri[:,2,1]-tri[:,0,1])-(tri[:,1,1]-tri[:,0,1])*(tri[:,2,0]-tri[:,0,0]);assert np.all(cross!=0);faces[cross<0]=faces[cross<0,::-1];area=float(abs(cross).sum()/2);ar=lambda p:abs(.5*np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1]));expected=ar(caps[0])-sum(ar(a)for a in caps[1:]);assert abs(area-expected)<1e-9,(area,expected);used=sorted(set(faces.ravel()));remap={old:i for i,old in enumerate(used)};xy=xy[used];faces=[tuple(remap[i]for i in f)for f in faces];N=len(xy);height=front_field(xy,caps);e=2e-7;dy=(front_field(xy+[e,0],caps)-front_field(xy-[e,0],caps))/(2*e);dz=(front_field(xy+[0,e],caps)-front_field(xy-[0,e],caps))/(2*e);frontN=np.column_stack([np.ones(N),-dy,-dz]);frontN/=np.linalg.norm(frontN,axis=1,keepdims=True);verts=np.vstack([np.column_stack([width/2+height,xy]),np.column_stack([np.full(N,-width/2),xy])]).tolist();F=list(faces)+[tuple(i+N for i in f[::-1])for f in faces];UV=[tuple(xy[i]/.005)for f in faces for i in f]+[tuple(xy[i]/.005)for f in faces for i in f[::-1]];NS=[frontN[i]for f in faces for i in f]+[np.array([-1.,0,0])for f in faces for i in f];lookup={tuple(np.round(a,9)):i for i,a in enumerate(xy)}
def find(a):
 k=tuple(np.round(a,9))
 if k in lookup:return lookup[k]
 d=np.linalg.norm(xy-a,axis=1);j=int(d.argmin());assert d[j]<2e-8;return j
for loop,out,cap in zip(loops,normals,caps):
 front=[find(a)for a in cap];back=[i+N for i in front];last=front;last_n=[(1.,0,0)]*len(loop);along=np.concatenate([[0],np.cumsum(np.linalg.norm(np.roll(loop,-1,axis=0)-loop,axis=1))])/.005;oldprof=0.;rows=[]
 # Frontcap→bevel→straight side→rear bevel→same rearcap boundary, shared indices.
 for a in np.linspace(math.pi/2,0,13)[1:]:rows.append((width/2-be+be*math.sin(a),be*(1-math.cos(a)),math.sin(a),math.cos(a),be*(math.pi/2-a)))
 for u in np.linspace(0,1,7)[1:]:rows.append(((width/2-be)*(1-2*u),0.,0.,1.,be*math.pi/2+u*(width-2*be)))
 for a in np.linspace(0,math.pi/2,13)[1:-1]:rows.append((-(width/2-be+be*math.sin(a)),be*(1-math.cos(a)),-math.sin(a),math.cos(a),be*math.pi/2+width-2*be+be*a))
 rows.append((None,None,-1.,0.,width-2*be+be*math.pi))
 for x,d,nx,nr,prof in rows:
  current=back if x is None else list(range(len(verts),len(verts)+len(loop)));nn=[(nx,nr*n[0],nr*n[1])for n in out]
  if x is not None:verts.extend((x,*(a-d*n))for a,n in zip(loop,out))
  for i in range(len(loop)):
   j=(i+1)%len(loop);ids=[last[i],current[i],current[j],last[j]];uv=[(along[i],oldprof/.005),(along[i],prof/.005),(along[i+1],prof/.005),(along[i+1],oldprof/.005)];ns=[last_n[i],nn[i],nn[j],last_n[j]]
   for k in [(0,1,2),(0,2,3)]:F.append(tuple(ids[t]for t in k));UV.extend(uv[t]for t in k);NS.extend(ns[t]for t in k)
  last=current;last_n=nn;oldprof=prof
V=np.asarray(verts,float);T=V[np.asarray(F)];volume=float(np.einsum('ij,ij->i',T[:,0],np.cross(T[:,1],T[:,2])).sum()/6);assert volume>0
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;col=bpy.data.collections.new(P['collection']);s.collection.children.link(col);studio=bpy.data.collections.new('LOCAL_NEUTRAL_STUDIO_NOT_EXPORT');s.collection.children.link(studio);m=bpy.data.meshes.new('Native closed slider frame with shared rounded boundaries');m.from_pydata(V.tolist(),[],F);m.update();assert not m.validate(clean_customdata=False);m.polygons.foreach_set('use_smooth',np.ones(len(F),bool));uv=m.uv_layers.new(name='Original5mm caps and section-length boundary charts');uv.data.foreach_set('uv',np.asarray(UV,np.float32).ravel());m.normals_split_custom_set(NS);m.update();m.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(m);nm=sum(not a.is_manifold for a in bm.edges);vol=bm.calc_volume(signed=True);chi=len(bm.verts)-len(bm.edges)+len(bm.faces);bm.free();assert nm==0 and chi==-2 and vol>0,(nm,chi,vol);areas=[a.area for a in m.loop_triangles];assert min(areas)>1e-18;o=bpy.data.objects.new('RelatedJB122003 ring fork candidate, tipmouths unresolved',m);col.objects.link(o);o['component_id']=P['component_id'];o['all_dimensions_estimated']=True;o['tip_mouths_not_built']=True;o['opposed_runningface_documented']=False;mat=bpy.data.materials.new('Neutral geometry gray only, not final rubber');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.20,.21,.23,1);p.inputs['Roughness'].default_value=.30;m.materials.append(mat)
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.max_bounces=8;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-.8;s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.20,.23,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.3
for name,loc,power,size in [('KEY',(.15,-.1,.18),2.,.20),('FILL',(-.16,.05,.08),1.,.18),('EDGE',(.10,.25,.03),1.5,.15),('LOWER',(.13,.05,-.15),.6,.18)]:
 l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=size;lo=bpy.data.objects.new(name,l);studio.objects.link(lo);lo.location=loc;lo.rotation_euler=(Vector((0,.07,0))-lo.location).to_track_quat('-Z','Y').to_euler()
c=bpy.data.cameras.new('Slider isolated camera');cam=bpy.data.objects.new('CAMERA',c);studio.objects.link(cam);s.camera=cam;c.type='ORTHO';c.ortho_scale=.23;c.clip_start=.001;c.clip_end=5;cam.location=(.30,.24,.22);cam.rotation_euler=(Vector((0,.07,0))-cam.location).to_track_quat('-Z','Y').to_euler();bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.gltf(filepath=str(H/'swingarm-chain-slider-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True);bpy.ops.wm.save_as_mainfile(filepath=str(H/'swingarm-chain-slider-v1.blend'),compress=True);r={'component_id':P['component_id'],'revision':P['revision'],'source_sha256':sha(H/'swingarm-chain-slider-v1.blend'),'export_sha256':sha(H/'swingarm-chain-slider-inspection.glb'),'vertices':len(V),'triangles':len(F),'nonmanifold_edges':nm,'euler_characteristic':chi,'signed_volume_m3':vol,'minimum_triangle_area_m2':min(areas),'CDT_cap_domain_area_m2':area,'expected_cap_domain_area_m2':expected,'large_ring_and_first_window_genuinely_open':True,'tip_mouths_built':False,'opposed_runningface_documented':False,'all_metric_parameters_estimated':True,'current_RDC_identity_verified':False,'assembled_fit_verified':False,'art_accepted':False};(O/'source-geometry-check.json').write_text(json.dumps(r,indent=2)+'\n');(H/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');print('CHAIN_SLIDER_SOURCE',json.dumps(r))
