"""Editable conditional housing core before rear ears/ribs; not a complete candidate.
Related bareYDY02002 photos. Estimated local sections, no calibratedRDC fit.
"""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/headlamp-housing-core-study-v1';O.mkdir(parents=True,exist_ok=True);plan=json.loads((R/'creative/research/headlamp/housing-shape-plan-v1.json').read_text());P=plan['parameters'];v=lambda n:P[n]['value'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;C=bpy.data.collections.new('WEWA_HEADLAMP_HOUSING_CORE_STUDY');s.collection.children.link(C);T=bpy.data.collections.new('Housing studio not exported');s.collection.children.link(T)
RIN=v('central_opening_radius_m');ROUT=v('mouth_outer_radius_m');WALL=v('nominal_normal_wall_m');ER=v('moulded_edge_radius_m');FLOOR=v('axial_depth_to_central_opening_m');LIP=.008+WALL/2

def smooth(t):
 t=max(0,min(1,t));return t*t*t*(10+t*(-15+6*t))
def gauss(x,z,cx,cz,sx,sz,amp):return -amp*math.exp(-((x-cx)/sx)**4-((z-cz)/sz)**4)
def surface(x,z):
 r=math.hypot(x,z);q=FLOOR+(LIP-FLOOR)*smooth((r-.063)/(.096-.063))
 # Observed five interior relief footprints, depth and rounded sections estimated.
 q+=gauss(x,z,0,.053,.009,.014,.0035)
 for sign in [-1,1]:
  t=(z-.019)/.050;envelope=smooth(t/.32)*(1-smooth((t-.86)/.14));width=.0025+.0065*max(0,min(1,t));q-=.0045*envelope*math.exp(-((x-sign*.043)/width)**4)
  q+=gauss(x,z,sign*.047,-.029,.008,.014,.004)
 return q
def normal(x,z):
 e=2e-5;fx=(surface(x+e,z)-surface(x-e,z))/(2*e);fz=(surface(x,z+e)-surface(x,z-e))/(2*e);return Vector((fx,-1,fz)).normalized()
NR=80;NA=256;points=[];norms=[]
for i in range(NR+1):
 r=RIN+(ROUT-RIN)*i/NR
 for j in range(NA):
  th=math.tau*j/NA;x=r*math.cos(th);z=r*math.sin(th);p=Vector((x,surface(x,z),z));n=normal(x,z);points.append(p);norms.append(n)
count=len(points);verts=[tuple(p+sign*WALL/2*n)for sign in [1,-1]for p,n in zip(points,norms)];faces=[];kinds=[]
for side in [0,1]:
 for i in range(NR):
  for j in range(NA):
   a=side*count+i*NA+j;b=side*count+i*NA+(j+1)%NA;c=side*count+(i+1)*NA+(j+1)%NA;d=side*count+(i+1)*NA+j;faces.append((a,b,c,d)if side==0 else(d,c,b,a));kinds.append('front'if side==0 else'back')
for row,kind in [(0,'inner-cut'),(NR,'outer-cut')]:
 for j in range(NA):
  a=row*NA+j;b=row*NA+(j+1)%NA;faces.append((a,a+count,b+count,b));kinds.append(kind)
m=bpy.data.meshes.new('Original annular moulded source cage');m.from_pydata(verts,[],faces);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(m);bm.free();a=bpy.data.objects.new('Housing annular finite core with five interior reliefs - unfinished study',m);C.objects.link(a)
loopnorm=[];min_dot=1
for p,k in zip(m.polygons,kinds):
 p.use_smooth=True
 for li in p.loop_indices:
  idx=m.loops[li].vertex_index;co=m.vertices[idx].co
  if k=='front':n=norms[idx]
  elif k=='back':n=-norms[idx-count]
  else:n=Vector((co.x,0,co.z)).normalized()*(1 if k=='outer-cut'else-1)
  # Sourcewinding checked independently; never flip arbitrary individual normals.
  loopnorm.append(n);min_dot=min(min_dot,n.dot(p.normal))
m.normals_split_custom_set(loopnorm)
weight=m.attributes.new('bevel_weight_edge','FLOAT','EDGE');boundary=set()
for side in [0,1]:
 for row in [0,NR]:
  boundary.update(side*count+row*NA+j for j in range(NA))
for e in m.edges:
 if all(i in boundary for i in e.vertices) and abs(e.vertices[0]-e.vertices[1])!=count:weight.data[e.index].value=1
be=a.modifiers.new('Intentional annular edge radius before any union','BEVEL');be.limit_method='WEIGHT';be.width=ER;be.segments=8;be.harden_normals=True;be.use_clamp_overlap=True
mat=bpy.data.materials.new('WEWA housing core neutral shape gray');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.18,.18,.18,1);bs.inputs['Roughness'].default_value=.35;a.data.materials.append(mat)
root=bpy.data.objects.new('HEADLAMP_HOUSING_ISOLATED_FRAME_UNPLACED',None);C.objects.link(root);a.parent=root
w=bpy.data.worlds.new('Housing neutral studio');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.2,.2,.2,1);w.node_tree.nodes['Background'].inputs[1].default_value=.3;s.world=w
for n,loc,power,size in [('key',(.15,-.2,.25),22,.25),('fill',(-.2,.1,.15),12,.30),('edge',(.12,.20,.2),20,.24)]:
 l=bpy.data.lights.new('Housing '+n,'AREA');l.energy=power;l.size=size;o=bpy.data.objects.new(l.name,l);T.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,.03,0))-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('Housing inspection camera',bpy.data.cameras.new('Housing inspection camera'));T.objects.link(cam);s.camera=cam;cam.location=(.24,-.48,.19);cam.rotation_euler=(Vector((0,.03,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=65;cam.data.clip_start=.001;cam.data.clip_end=10;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.resolution_x=750;s.render.resolution_y=700;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-3
# Noexport of partial core. It is kept editable and explicitly incomplete.
bpy.context.view_layer.update();em=bpy.data.meshes.new_from_object(a.evaluated_get(bpy.context.evaluated_depsgraph_get()));em.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(em);nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free();areas=[t.area for t in em.loop_triangles];bpy.data.meshes.remove(em);assert not nonmanifold and volume>0 and min(areas)>0
source=H/'headlamp-housing-core-study-v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source));report={'schema':1,'revision':'headlamp-housing-core-study-v1','source_sha256':sha(source),'collection':C.name,'root':root.name,'object':a.name,'triangles':len(areas),'non_manifold_edges':nonmanifold,'signed_volume_m3':volume,'min_triangle_area_m2':min(areas),'source_unbevelled_min_face_custom_normal_dot':min_dot,'nominal_normal_wall_m':WALL,'edge_radius_before_unions_m':ER,'known_missing_units':['Rear upper/side/lower mounting ears','Rear ribs','Mounting holes/slots','Uppercentre clip detail unresolved'],'state':'Partial core construction only; not a complete housing, no GLB or final96 planned for this intermediate','art_accepted':False};(O/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
