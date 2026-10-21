"""Conditional PF401007 related rear bucket, one original editable observable piece.
No claim of calibrated dimensions or currentRDC installed identity. Gray study only.
"""
import bpy,bmesh,json,math,hashlib,tempfile,subprocess,shutil
from pathlib import Path
from mathutils import Vector
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/headlamp-bucket-study-v1';O.mkdir(parents=True,exist_ok=True);plan=json.loads((R/'creative/research/headlamp/bucket-shape-plan-v1.json').read_text());P=plan['parameters'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
C=bpy.data.collections.new('WEWA_HEADLAMP_BUCKET_STUDY');s.collection.children.link(C);K=bpy.data.collections.new('Bucket editable construction - not exported');s.collection.children.link(K);T=bpy.data.collections.new('Bucket studio - not exported');s.collection.children.link(T)
mat=bpy.data.materials.new('WEWA bucket neutral gray shape study');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.18,.18,.18,1);bs.inputs['Roughness'].default_value=.34

def mesh(n,v,f,col=K):
 m=bpy.data.meshes.new(n);m.from_pydata(v,[],f);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(m);bm.free();a=bpy.data.objects.new(n,m);col.objects.link(a);return a

def lathe(n,profile,N=192,axis='Y',col=K):
 v=[];rings=[];f=[]
 for q,r in profile:
  ids=[]
  for j in range(1 if r==0 else N):
   angle=math.tau*j/N;p=(r*math.cos(angle),q,r*math.sin(angle)) if axis=='Y' else(q,r*math.cos(angle),r*math.sin(angle));ids.append(len(v));v.append(p)
  rings.append(ids)
 for a,b in zip(rings,rings[1:]+rings[:1]):
  if len(a)==len(b)==1:continue
  for j in range(N):
   k=(j+1)%N
   if len(a)==1:f.append((a[0],b[j],b[k]))
   elif len(b)==1:f.append((a[j],b[0],a[k]))
   else:f.append((a[j],b[j],b[k],a[k]))
 return mesh(n,v,f,col)

def pchip(xs,ys,x):
 xs=np.array(xs);ys=np.array(ys);h=np.diff(xs);d=np.diff(ys)/h;m=np.zeros(len(xs));m[0]=d[0];m[-1]=d[-1]
 for k in range(1,len(xs)-1):
  if d[k-1]*d[k]>0:
   w1=2*h[k]+h[k-1];w2=h[k]+2*h[k-1];m[k]=(w1+w2)/(w1/d[k-1]+w2/d[k])
 k=min(max(np.searchsorted(xs,x)-1,0),len(xs)-2);t=(x-xs[k])/h[k];return (2*t**3-3*t*t+1)*ys[k]+(t**3-2*t*t+t)*h[k]*m[k]+(-2*t**3+3*t*t)*ys[k+1]+(t**3-t*t)*h[k]*m[k+1]
# The visible main body is axisymmetric only as a working interpolation.
# Explicit rolled front lip is constructed before CSG; no global bevel afterwards.
q=[.0012,.008,.02,.04,.06,.08,.097,.106,.112];rr=[.1,.0998,.097,.091,.082,.072,.062,.046,0];outer=[(float(x),float(pchip(q,rr,x)))for x in np.linspace(.0012,.110,70)]+[(.112,0)]
inner=[(.1095,0)]+[(float(x),max(.001,float(pchip(q,rr,x)-.0025)))for x in np.linspace(.107,.0012,70)]
section=[(0,.09875),(.000366,.099634),(.0012,.1)]+outer[1:]+inner+[(.000366,.097866),(0,.09875)]
# Duplicate last station is removed: closure already implied by lathe.
section=section[:-1];base=lathe('Editable finite bucket shell - section estimate',section)

def box(n,c,d,r):
 bpy.ops.mesh.primitive_cube_add(size=1,location=c);a=bpy.context.object;a.name=n
 for co in list(a.users_collection):co.objects.unlink(a)
 K.objects.link(a);a.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if r:
  b=a.modifiers.new('Intentional moulded radius before CSG','BEVEL');b.width=r;b.segments=6;b.affect='EDGES'
 return a
features=[box('Editable raised rear central spine',(0,.108,0),(.036,.018,.151),.005)]
for sign in [-1,1]:
 profile=[(-.017,0),(-.017,.023),(-.0165,.025),(-.015,.027),(.012,.027),(.014,.0265),(.015,.025),(.015,0)]
 a=lathe('Editable side mount seat '+str(sign),profile,128,'X');a.location=(sign*.089,.055,0);features.append(a)
drills=[]
for sign in [-1,1]:drills.append(box('Editable rear cable window '+str(sign),(sign*.049,.103,.014),(.043,.100,.053),.009))
# One transverse cylinder opens the two seats, not a black surface decal.
a=lathe('Editable transverse seat aperture - hidden bare bore estimated',[(-.14,0),(-.14,.018),(.14,.018),(.14,0)],128,'X');a.location=(0,.055,0);drills.append(a)
bpy.context.view_layer.update()
def row(a):
 dg=bpy.context.evaluated_depsgraph_get();e=a.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();r={'name':a.name,'vertices':[list(a.matrix_world@v.co)for v in m.vertices],'triangles':[list(t.vertices)for t in m.loop_triangles]};e.to_mesh_clear();return r
with tempfile.TemporaryDirectory(prefix='wewa-bucket-')as tmp:
 inp=Path(tmp)/'in.json';out=Path(tmp)/'out.json';inp.write_text(json.dumps({'base':row(base),'features':[row(a)for a in features],'drills':[row(a)for a in drills]}));subprocess.run([shutil.which('python'),str(H/'bucket_csg_worker_v1.py'),str(inp),str(out)],check=True);result=json.loads(out.read_text())
a=mesh('Conditional PF401007 rear bucket - isolated gray estimate',result['vertices'],result['triangles'],C);a.data.materials.append(mat)
for f in a.data.polygons:f.use_smooth=True
a.data.set_sharp_from_angle(angle=math.radians(35));wn=a.modifiers.new('Local flat-preserving weighted normals, not geometry bevel','WEIGHTED_NORMAL');wn.keep_sharp=True;wn.weight=50
# Simple per-face dominant projection gives nonzero derivative on every triangle;
# it is a gray study chart, not a physically scaled texture layout or normal map.
m=a.data;m.uv_layers.new(name='GrayStudyPlanarCharts')
for p in m.polygons:
 axis=max(range(3),key=lambda i:abs(p.normal[i]));other=[i for i in range(3)if i!=axis]
 for li in p.loop_indices:
  v=m.vertices[m.loops[li].vertex_index].co;m.uv_layers.active.data[li].uv=(v[other[0]]/.1,v[other[1]]/.1)
root=bpy.data.objects.new('HEADLAMP_BUCKET_ISOLATED_ORIGIN_UNPLACED',None);C.objects.link(root);a.parent=root
K.hide_render=True;K.hide_viewport=True
w=bpy.data.worlds.new('Bucket neutral studio');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.22,.22,.22,1);w.node_tree.nodes['Background'].inputs[1].default_value=.3;s.world=w
for n,c,e,size in [('key',(.17,-.22,.3),40,.30),('fill',(-.22,.10,.17),25,.35),('edge',(.2,.20,.23),32,.24)]:
 l=bpy.data.lights.new('Bucket '+n,'AREA');l.energy=e;l.size=size;o=bpy.data.objects.new(l.name,l);T.objects.link(o);o.location=c;o.rotation_euler=(Vector((0,.05,0))-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('Bucket inspection camera',bpy.data.cameras.new('Bucket inspection camera'));T.objects.link(cam);s.camera=cam;cam.location=(.33,.42,.20);cam.rotation_euler=(Vector((0,.05,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=60;cam.data.clip_start=.001;cam.data.clip_end=10
s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.resolution_x=700;s.render.resolution_y=600;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-1
# Export evaluated surface and actual source topology checks before any rendering.
dg=bpy.context.evaluated_depsgraph_get();ev=a.evaluated_get(dg);em=ev.to_mesh();em.calc_loop_triangles();areas=[t.area for t in em.loop_triangles];bm=bmesh.new();bm.from_mesh(em);nm=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free();ev.to_mesh_clear();assert not nm and volume>0 and min(areas)>0,(nm,volume,min(areas))
bpy.ops.object.select_all(action='DESELECT');a.select_set(True);root.select_set(True);bpy.context.view_layer.objects.active=a
source=H/'headlamp-bucket-study-v1.blend';glb=H/'headlamp-bucket-study-v1.glb';bpy.ops.wm.save_as_mainfile(filepath=str(source));bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True,export_tangents=False,export_animations=False)
report={'schema':1,'revision':'headlamp-bucket-study-v1','source_sha256':sha(source),'export_sha256':sha(glb),'collection':C.name,'root':root.name,'object':a.name,'triangles':len(areas),'min_triangle_area_m2':min(areas),'exact_zero_area_triangles':sum(x==0 for x in areas),'non_manifold_edges':nm,'signed_volume_m3':volume,'CSG_stages':result['stages'],'parameters_plan':'creative/research/headlamp/bucket-shape-plan-v1.json','scope':'Unplaced gray conditional relatedPF401007 rearbucket only. No calibrated fit, grade or exactRDC identity. Front fastener seats and hidden inner ribs unresolved.','all_required_components_built':False,'art_accepted':False};(O/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='CSG_stages'}))
