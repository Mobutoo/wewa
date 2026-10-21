"""Original finite first photographed terminal: paddle, lug and two truebores.
Paired circularbends form estimatedoffset; no tube/weld/opposite copied.
"""
import bpy,bmesh,numpy as np,math,json,hashlib,sys
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-protection-terminal-a-v1';sys.path.insert(0,str(H));from profile_shape import shape,normal2,inside,warp,section,neutral
P=json.loads((H/'parameters.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();loops=shape(P);be=P['cutedge_radius_m'];width=P['thickness_m'];normals=[normal2(a)for a in loops];caps=[a-be*n for a,n in zip(loops,normals)];points=[];edges=[]
# Every genuine boundary is constrained before interior samples.
for a in caps:
 j=len(points);points.extend(a.tolist());edges.extend((j+i,j+(i+1)%len(a))for i in range(len(a)))
def domain(q):
 keep=inside(q,caps[0])
 for hole in caps[1:]:keep&=~inside(q,hole)
 return keep
constraint_count=len(points)
pitch=P['grid_pitch_m'];bend_angle,bend_radius,bend_line,start,v1,v2,end,zend=section(P);bounds=np.vstack(caps);lo=bounds.min(0);hi=bounds.max(0);ys=np.arange(lo[0]+pitch*.31,hi[0],pitch);bendrows=np.linspace(start,end,int(math.ceil((end-start)/P['bend_grid_step_m']))+1);zs=np.unique(np.concatenate([np.arange(lo[1]+pitch*.27,hi[1],pitch),bendrows,[start,v1,v2,end]]));y,z=np.meshgrid(ys,zs);q=np.column_stack([y.ravel(),z.ravel()]);q=q[domain(q)];points.extend(q.tolist())
unique=[];seen=set()
for a in points:
 k=tuple(np.round(a,10))
 if k not in seen:seen.add(k);unique.append(Vector(a))
assert len(unique)>=constraint_count
print('TERMINAL_A_CDT_INPUT',len(unique),flush=True);xy,_,faces,*_=delaunay_2d_cdt(unique,edges,[list(range(len(caps[0])))],1,1e-9,False);xy=np.asarray([a[:]for a in xy]);faces=np.asarray(faces,np.int64);assert faces.ndim==2 and faces.shape[1]==3;faces=faces[domain(xy[faces].mean(axis=1))];tri=xy[faces];cross=(tri[:,1,0]-tri[:,0,0])*(tri[:,2,1]-tri[:,0,1])-(tri[:,1,1]-tri[:,0,1])*(tri[:,2,0]-tri[:,0,0]);assert np.all(cross!=0);faces[cross<0]=faces[cross<0,::-1];area=float(abs(cross).sum()/2);ar=lambda p:abs(.5*np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1]));expected=ar(caps[0])-sum(ar(a)for a in caps[1:]);assert abs(area-expected)<1e-9,(area,expected);used=sorted(set(faces.ravel()));remap={old:i for i,old in enumerate(used)};xy=xy[used];faces=[tuple(remap[i]for i in f)for f in faces];N=len(xy);height=np.zeros(N);frontN=np.tile([1.,0,0],(N,1));verts=np.vstack([np.column_stack([width/2+height,xy]),np.column_stack([np.full(N,-width/2),xy])]).tolist();F=list(faces)+[tuple(i+N for i in f[::-1])for f in faces];UV=[tuple(xy[i]/.010)for f in faces for i in f]+[tuple(xy[i]/.010)for f in faces for i in f[::-1]];NS=[frontN[i]for f in faces for i in f]+[np.array([-1.,0,0])for f in faces for i in f];lookup={tuple(np.round(a,9)):i for i,a in enumerate(xy)}
def find(a):
 k=tuple(np.round(a,9))
 if k in lookup:return lookup[k]
 d=np.linalg.norm(xy-a,axis=1);j=int(d.argmin());assert d[j]<2e-8;return j
for loop,out,cap in zip(loops,normals,caps):
 front=[find(a)for a in cap];back=[i+N for i in front];last=front;last_n=[(1.,0,0)]*len(loop);along=np.concatenate([[0],np.cumsum(np.linalg.norm(np.roll(loop,-1,axis=0)-loop,axis=1))])/.010;oldprof=0.;rows=[]
 # Frontcap→bevel→straight side→rear bevel→same rearcap boundary, shared indices.
 for a in np.linspace(math.pi/2,0,13)[1:]:rows.append((width/2-be+be*math.sin(a),be*(1-math.cos(a)),math.sin(a),math.cos(a),be*(math.pi/2-a)))
 for u in np.linspace(0,1,7)[1:]:rows.append(((width/2-be)*(1-2*u),0.,0.,1.,be*math.pi/2+u*(width-2*be)))
 for a in np.linspace(0,math.pi/2,13)[1:-1]:rows.append((-(width/2-be+be*math.sin(a)),be*(1-math.cos(a)),-math.sin(a),math.cos(a),be*math.pi/2+width-2*be+be*a))
 rows.append((None,None,-1.,0.,width-2*be+be*math.pi))
 for x,d,nx,nr,prof in rows:
  current=back if x is None else list(range(len(verts),len(verts)+len(loop)));nn=[(nx,nr*n[0],nr*n[1])for n in out]
  if x is not None:verts.extend((x,*(a-d*n))for a,n in zip(loop,out))
  for i in range(len(loop)):
   j=(i+1)%len(loop);ids=[last[i],current[i],current[j],last[j]];uv=[(along[i],oldprof/.010),(along[i],prof/.010),(along[i+1],prof/.010),(along[i+1],oldprof/.010)];ns=[last_n[i],nn[i],nn[j],last_n[j]]
   for k in [(0,1,2),(0,2,3)]:F.append(tuple(ids[t]for t in k));UV.extend(uv[t]for t in k);NS.extend(ns[t]for t in k)
  last=current;last_n=nn;oldprof=prof
developed=np.asarray(verts,float);V,NS=warp(developed,NS,F,P);V=V.astype(np.float32);T=V[np.asarray(F)];volume=float(np.einsum('ij,ij->i',T[:,0],np.cross(T[:,1],T[:,2])).sum()/6);assert volume>0
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;col=bpy.data.collections.new(P['collection']);s.collection.children.link(col);studio=bpy.data.collections.new('LOCAL_NEUTRAL_STUDIO_NOT_EXPORT');s.collection.children.link(studio);m=bpy.data.meshes.new('Original twohole paddle and lug with continuous doublebend and shared rounded cutedges');m.from_pydata(V.tolist(),[],F);m.update();assert not m.validate(clean_customdata=False);m.polygons.foreach_set('use_smooth',np.ones(len(F),bool));uv=m.uv_layers.new(name='Original10mm developedsheet and cutedge charts');uv.data.foreach_set('uv',np.asarray(UV,np.float32).ravel());# Route truly planar cap faces to geometric flat normals, keeping curved sections authored.
NS=np.asarray(NS,float);flat_count=0
for poly in m.polygons:
 q=developed[list(poly.vertices)]
 cap=(np.ptp(q[:,0])<1e-12 and abs(abs(q[0,0])-P['thickness_m']/2)<1e-12)
 planar=(np.max(q[:,2])<start-1e-8 or np.min(q[:,2])>end+1e-8)
 if cap and planar:
  poly.use_smooth=False;NS[list(poly.loop_indices)]=0.;flat_count+=1
m.normals_split_custom_set(NS);m.update();m.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(m);nm=sum(not a.is_manifold for a in bm.edges);vol=bm.calc_volume(signed=True);chi=len(bm.verts)-len(bm.edges)+len(bm.faces);bm.free();assert nm==0 and chi==-2 and vol>0,(nm,chi,vol);areas=[a.area for a in m.loop_triangles];assert min(areas)>1e-18;o=bpy.data.objects.new('First observed terminal-A only, tube weld opposite and hook absent',m);col.objects.link(o);o['component_id']=P['component_id'];o['all_dimensions_estimated']=True;o['tube_weld_opposite_hook_or_spacer_built']=False;o['installed_mount_verified']=False;mat=bpy.data.materials.new('Neutral geometry gray only, not final paint');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.20,.21,.23,1);p.inputs['Roughness'].default_value=.30;m.materials.append(mat)
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.max_bounces=8;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-.8;s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.20,.23,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.3
for name,loc,power,size in [('KEY',(.15,-.1,.18),1.2,.20),('FILL',(-.16,-.05,.08),.6,.18),('EDGE',(.10,.25,.03),.9,.15),('LOWER',(.13,.05,-.15),.4,.18)]:
 l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=size;lo=bpy.data.objects.new(name,l);studio.objects.link(lo);lo.location=loc;lo.rotation_euler=(Vector((0,.005,.025))-lo.location).to_track_quat('-Z','Y').to_euler()
c=bpy.data.cameras.new('Slider isolated camera');cam=bpy.data.objects.new('CAMERA',c);studio.objects.link(cam);s.camera=cam;c.type='ORTHO';c.ortho_scale=.14;c.clip_start=.001;c.clip_end=5;cam.location=(.12,-.22,.10);cam.rotation_euler=(Vector((0,.005,.025))-cam.location).to_track_quat('-Z','Y').to_euler();bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.gltf(filepath=str(H/'engine-protection-terminal-a-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True);bpy.ops.wm.save_as_mainfile(filepath=str(H/'engine-protection-terminal-a-v1.blend'),compress=True);r={'component_id':P['component_id'],'revision':P['revision'],'source_sha256':sha(H/'engine-protection-terminal-a-v1.blend'),'export_sha256':sha(H/'engine-protection-terminal-a-inspection.glb'),'vertices':len(V),'triangles':len(F),'nonmanifold_edges':nm,'euler_characteristic':chi,'signed_volume_m3':vol,'minimum_triangle_area_m2':min(areas),'CDT_cap_domain_area_m2':area,'expected_cap_domain_area_m2':expected,'true_planar_faces_flat_routed':flat_count,'two_round_bores_genuinely_open':True,'tube_weld_opposite_hook_or_spacer_built':False,'doublebend_and_thickness_measured':False,'small_dark_mark_is_third_bore_certified':False,'bounds_m':[V.min(0).tolist(),V.max(0).tolist()],'derived_neutral_section':{'angle_rad':bend_angle,'mean_radius_m':bend_radius,'straight_developed_length_m':bend_line,'bend_start_V_m':start,'first_end_V_m':v1,'second_start_V_m':v2,'end_V_m':end,'physical_end_Z_m':zend,'compression_VminusZ_m':end-zend},'frame':P['frame'],'all_metric_parameters_estimated':True,'current_RDC_identity_verified':False,'assembled_fit_verified':False,'art_accepted':False};(O/'source-geometry-check.json').write_text(json.dumps(r,indent=2)+'\n');(H/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');print('GUARD_TERMINAL_A_SOURCE',json.dumps(r))
