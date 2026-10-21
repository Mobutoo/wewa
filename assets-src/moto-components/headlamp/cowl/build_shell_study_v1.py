"""Original bounded cowl shell study. Related PF7401X3 photos, not measured RDC.
Finite parametric wall and rolled boundaries, no hidden hardware, material or assembly.
"""
import bpy,bmesh,math,json,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/headlamp-cowl-shell-study-v1';O.mkdir(parents=True,exist_ok=True);plan=R/'creative/research/headlamp-cowl/shell-study-plan-v1.json';P=json.loads(plan.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
C=bpy.data.collections.new('WEWA_HEADLAMP_COWL_SHELL_STUDY');s.collection.children.link(C);T=bpy.data.collections.new('Cowl shape studio - not exported');s.collection.children.link(T)
W=.0025;NA=256;NQ=112;NC=12

def section(th):
 ct=math.cos(th);st=math.sin(th);outer=.115+.006*st*st+.007*max(0,-ct)**2;rear=.025+.12*((1-ct)/2)**.85;rr=outer-.004+.005*st*st
 return [( .1035,0),(.1075,-.0007),(outer-.004,0),(outer,.004),(outer+.001,min(.014,rear*.22)),(outer+.0015,rear*.35),(rr,rear*.8),(rr-.0015,rear)]
def cat(pts,u):
 # Clamped cubic B-spline evaluated by de Boor; bounded by control polygon.
 n=len(pts)-1;p=3;knots=[0.]*(p+1)+[j/(n-p+1)for j in range(1,n-p+1)]+[1.]*(p+1)
 u=max(0,min(1,u));k=n if u==1 else next(i for i in range(p,n+1)if knots[i]<=u<knots[i+1]);d=[np.array(pts[k-p+j],dtype=np.float64)for j in range(p+1)]
 for r in range(1,p+1):
  for j in range(p,r-1,-1):
   lo=knots[j+k-p];hi=knots[j+1+k-r];alpha=(u-lo)/(hi-lo)if hi>lo else 0.;d[j]=(1-alpha)*d[j-1]+alpha*d[j]
 return d[p]

def mid(th,q):
 r,y=cat(section(th),q);return np.array((r*math.sin(th),y,r*math.cos(th)),dtype=np.float64)
def frame(th,q):
 e=1e-5;dt=(mid(th+e,q)-mid(th-e,q))/(2*e);lo=max(0,q-e);hi=min(1,q+e);dq=(mid(th,hi)-mid(th,lo))/(hi-lo);n=np.cross(dt,dq);n/=np.linalg.norm(n);b=dq-dt*np.dot(dq,dt)/np.dot(dt,dt);b/=np.linalg.norm(b);return n,b
# Perimeter: exterior front->rear; rounded rear cut; interior rear->front; rounded aperture cut.
rows=[]
for k in range(NQ+1):rows.append(('outer',k/NQ,0))
for k in range(1,NC):rows.append(('rear',1,k*math.pi/NC))
for k in range(NQ,-1,-1):rows.append(('inner',k/NQ,0))
for k in range(1,NC):rows.append(('front',0,k*math.pi/NC))

def point(th,desc):
 kind,q,a=desc;p=mid(th,q);n,b=frame(th,q)
 if kind=='outer':return p+n*W/2
 if kind=='inner':return p-n*W/2
 if kind=='rear':return p+(n*math.cos(a)+b*math.sin(a))*W/2
 return p+(-n*math.cos(a)-b*math.sin(a))*W/2

verts=[tuple(point(math.tau*j/NA,row))for row in rows for j in range(NA)];NN=len(rows);faces=[]
for i in range(NN):
 for j in range(NA):faces.append((i*NA+j,i*NA+(j+1)%NA,((i+1)%NN)*NA+(j+1)%NA,((i+1)%NN)*NA+j))
m=bpy.data.meshes.new('Original finite cowl spline sections with rounded wall returns');m.from_pydata(verts,[],faces);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);volume=bm.calc_volume(signed=True);nonmanifold=sum(not e.is_manifold for e in bm.edges);components=0;todo=set(bm.verts)
while todo:
 components+=1;stack=[todo.pop()]
 while stack:
  for e in stack.pop().link_edges:
   for v in e.verts:
    if v in todo:todo.remove(v);stack.append(v)
bm.to_mesh(m);bm.free();assert volume>0 and nonmanifold==0 and components==1
# Actual finite surface normals from incident section derivatives; no WeightedNormal/global bevel.
for p in m.polygons:p.use_smooth=True
uv=m.uv_layers.new(name='Original cowl angular-section UV')
for i,p in enumerate(m.polygons):
 row=i//NA;j=i%NA;coords=[(j/NA,row/NN),((j+1)/NA,row/NN),((j+1)/NA,(row+1)/NN),(j/NA,(row+1)/NN)]
 for li,v in zip(p.loop_indices,coords):uv.data[li].uv=v
m.update();m.calc_loop_triangles();areas=[t.area for t in m.loop_triangles];mindot=1
for t in m.loop_triangles:
 a,b,c=[m.vertices[k].co for k in t.vertices];normal=(b-a).cross(c-a).normalized()
 for li in t.loops:mindot=min(mindot,normal.dot(m.corner_normals[li].vector))
bad=[]
for t in m.loop_triangles:
 a,b,c=[m.vertices[k].co for k in t.vertices];normal=(b-a).cross(c-a).normalized();dot=min(normal.dot(m.corner_normals[li].vector)for li in t.loops)
 if dot<.9:bad.append({'polygon':t.polygon_index,'row_index':t.polygon_index//NA,'theta_index':t.polygon_index%NA,'section':rows[t.polygon_index//NA],'min_normal_dot':dot,'triangle':list(t.vertices),'points':[list(v)for v in [a,b,c]]})
if bad:
 debug=Path('/workspace/wewa-assets/work-in-progress/headlamp-cowl-shell-study-v1');debug.mkdir(parents=True,exist_ok=True);(debug/'bad-triangles.json').write_text(json.dumps({'recipe_sha256':sha(Path(__file__)),'bad_count':len(bad),'bad':sorted(bad,key=lambda r:r['min_normal_dot'])[:40]},indent=2)+'\n')
assert min(areas)>0 and mindot>.9,(min(areas),mindot)
mat=bpy.data.materials.new('WEWA cowl neutral shape gray - study only');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.19,.19,.19,1);bs.inputs['Roughness'].default_value=.32
obj=bpy.data.objects.new('Cowl continuous finite shell - partial conditional study',m);C.objects.link(obj);m.materials.append(mat);obj['structural_closed_volume']=True;obj['estimated_geometry']=True
root=bpy.data.objects.new('HEADLAMP_COWL_ISOLATED_FRAME_UNPLACED',None);C.objects.link(root);obj.parent=root
w=bpy.data.worlds.new('Cowl neutral shape world');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1);w.node_tree.nodes['Background'].inputs[1].default_value=.25;s.world=w
for name,loc,power,size in [('key',(-.22,-.25,.33),12,.3),('fill',(.28,.05,.17),8,.3),('edge',(-.12,.30,.25),15,.22)]:
 l=bpy.data.lights.new('Cowl '+name,'AREA');l.energy=power;l.size=size;o=bpy.data.objects.new(l.name,l);T.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,.05,0))-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('Cowl inspection camera',bpy.data.cameras.new('Cowl inspection camera'));T.objects.link(cam);s.camera=cam;cam.location=(.30,-.52,.27);cam.rotation_euler=(Vector((0,.05,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=65;cam.data.clip_start=.001;cam.data.clip_end=10
s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.resolution_x=900;s.render.resolution_y=850;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-2
bpy.context.view_layer.update();source=H/'headlamp-cowl-shell-study-v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);root.select_set(True);bpy.context.view_layer.objects.active=obj;export=H/'headlamp-cowl-shell-study-v1.glb';bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_cameras=False,export_lights=False,export_yup=True,export_extras=True)
report={'schema':1,'revision':'headlamp-cowl-shell-study-v1','source_sha256':sha(source),'export_sha256':sha(export),'shape_plan_sha256':sha(plan),'collection':C.name,'root':root.name,'object':obj.name,'vertices':len(m.vertices),'actual_triangles':len(areas),'min_triangle_area_m2':min(areas),'minimum_triangle_corner_normal_dot':mindot,'non_manifold_edges':nonmanifold,'connected_components':components,'positive_signed_volume_m3':volume,'all_dimensions_estimated':True,'nominal_mid_surface_normal_wall_m':W,'state':'Partial finite shell only; no scallops/keyhole/pads/ribs/hardware/paint built yet. Orientation/depth conditional, not a completed cowl.','first_gray_and_reflection_required':True,'art_accepted':False};(O/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');print('COWL_SHELL_STUDY',json.dumps(report))
