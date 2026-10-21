"""Editable conditional housing core before rear ears/ribs; not a complete candidate.
Related bareYDY02002 photos. Estimated local sections, no calibratedRDC fit.
"""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/headlamp-housing-core-study-v2';O.mkdir(parents=True,exist_ok=True);plan=json.loads((R/'creative/research/headlamp/housing-shape-plan-v1.json').read_text());P=plan['parameters'];v=lambda n:P[n]['value'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;C=bpy.data.collections.new('WEWA_HEADLAMP_HOUSING_CORE_STUDY');s.collection.children.link(C);T=bpy.data.collections.new('Housing studio not exported');s.collection.children.link(T)
RIN=v('central_opening_radius_m');ROUT=v('mouth_outer_radius_m');WALL=v('nominal_normal_wall_m');ER=v('moulded_edge_radius_m');FLOOR=v('axial_depth_to_central_opening_m');LIP=.008+WALL/2

def smooth(t):
 t=max(0,min(1,t));return t*t*t*(10+t*(-15+6*t))
def gauss(x,z,cx,cz,sx,sz,amp):return -amp*math.exp(-((x-cx)/sx)**4-((z-cz)/sz)**4)
def surface(x,z):
 r=math.hypot(x,z);q=FLOOR+(LIP-FLOOR)*smooth((r-.063)/(.096-.063))
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
m=bpy.data.meshes.new('Original annular moulded source cage');m.from_pydata(verts,[],faces);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(m);bm.free();a=bpy.data.objects.new('Original regular hollow bowl construction',m);C.objects.link(a)
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
# Five separate small moulded face profiles with radii before union.
# This replaces the rejected soft displacementfield; no uniform hiddenwall claim.
import tempfile,subprocess,shutil
from mathutils.geometry import barycentric_transform
K=bpy.data.collections.new('Housing editable bowl and relief constructions - hidden');s.collection.children.link(K);C.objects.unlink(a);K.objects.link(a);base=a
relief_plan=json.loads((R/'creative/research/headlamp/housing-reliefs-plan-v2.json').read_text());features=[]
for row in relief_plan['reliefs']:
 coords=row['assigned_XZ_m'];nv=len(coords);vv=[]
 for side in [0,1]:
  for x,z in coords:
   q=.047-.015*(z-.017)/.043 if row['name']in['upper-left','upper-right']else .044 if row['name']=='upper-centre'else .043
   vv.append((x,q if side==0 else row['back_plane_Y_estimated_m'],z))
 ff=[tuple(reversed(range(nv))),tuple(range(nv,nv*2))]+[(i,(i+1)%nv,(i+1)%nv+nv,i+nv)for i in range(nv)];fm=bpy.data.meshes.new('Relief source profile '+row['name']);fm.from_pydata(vv,[],ff);fm.update();bm=bmesh.new();bm.from_mesh(fm);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(fm);bm.free()
 for poly in fm.polygons:poly.use_smooth=True
 fm.set_sharp_from_angle(angle=math.radians(35));fm.normals_split_custom_set([p.normal.copy()for p in fm.polygons for _ in p.loop_indices]);fo=bpy.data.objects.new('Editable finite moulded relief '+row['name'],fm);K.objects.link(fo);bevel=fo.modifiers.new('Intentional relief edge radius before union','BEVEL');bevel.limit_method='ANGLE';bevel.angle_limit=.4;bevel.width=row['edge_radius_estimated_m'];bevel.segments=8;bevel.harden_normals=True;bevel.use_clamp_overlap=True;features.append(fo)
bpy.context.view_layer.update()
def input_row(o):
 dg=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(dg);em=ev.to_mesh();em.calc_loop_triangles();r={'name':o.name,'vertices':[list(o.matrix_world@v.co)for v in em.vertices],'triangles':[list(t.vertices)for t in em.loop_triangles],'corner_normals':[[list(em.corner_normals[i].vector)for i in t.loops]for t in em.loop_triangles]};ev.to_mesh_clear();return r
inputs=[input_row(o)for o in [base]+features]
with tempfile.TemporaryDirectory(prefix='wewa-housing-')as td:
 inp=Path(td)/'in.json';out=Path(td)/'out.json';inp.write_text(json.dumps({'base':inputs[0],'features':inputs[1:],'drills':[]}));subprocess.run([shutil.which('python'),str(H/'housing_csg_worker_v2.py'),str(inp),str(out)],check=True);cs=json.loads(out.read_text())
cm=bpy.data.meshes.new('Original housing bowl and hard moulded reliefs');cm.from_pydata(cs['vertices'],[],cs['triangles']);cm.update();bm=bmesh.new();bm.from_mesh(cm);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(cm);bm.free();a=bpy.data.objects.new('Housing finite bowl and five moulded face reliefs - partial study',cm);C.objects.link(a);a.data.materials.append(mat);cn=[];min_csg_dot=1
for poly in cm.polygons:
 poly.use_smooth=True;own=cs['triangle_source_owners'][poly.index];fid=cs['triangle_source_face_ids'][poly.index];ref=inputs[own];idx=ref['triangles'][fid];p0,p1,p2=[Vector(ref['vertices'][k])for k in idx];n0,n1,n2=[Vector(n)for n in ref['corner_normals'][fid]];assert set(poly.vertices)==set(cs['triangles'][poly.index])
 for li in poly.loop_indices:
  point=cm.vertices[cm.loops[li].vertex_index].co;n=barycentric_transform(point,p0,p1,p2,n0,n1,n2).normalized();cn.append(n);min_csg_dot=min(min_csg_dot,n.dot(poly.normal))
cm.normals_split_custom_set(cn);K.hide_render=True;K.hide_viewport=True
root=bpy.data.objects.new('HEADLAMP_HOUSING_ISOLATED_FRAME_UNPLACED',None);C.objects.link(root);a.parent=root
w=bpy.data.worlds.new('Housing neutral studio');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.2,.2,.2,1);w.node_tree.nodes['Background'].inputs[1].default_value=.3;s.world=w
for n,loc,power,size in [('key',(.15,-.2,.25),22,.25),('fill',(-.2,.1,.15),12,.30),('edge',(.12,.20,.2),20,.24)]:
 l=bpy.data.lights.new('Housing '+n,'AREA');l.energy=power;l.size=size;o=bpy.data.objects.new(l.name,l);T.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,.03,0))-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('Housing inspection camera',bpy.data.cameras.new('Housing inspection camera'));T.objects.link(cam);s.camera=cam;cam.location=(.24,-.48,.19);cam.rotation_euler=(Vector((0,.03,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=65;cam.data.clip_start=.001;cam.data.clip_end=10;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.resolution_x=750;s.render.resolution_y=700;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-3
# Noexport of partial core. It is kept editable and explicitly incomplete.
bpy.context.view_layer.update();em=bpy.data.meshes.new_from_object(a.evaluated_get(bpy.context.evaluated_depsgraph_get()));em.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(em);nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free();areas=[t.area for t in em.loop_triangles];bpy.data.meshes.remove(em);assert not nonmanifold and volume>0 and min(areas)>0
source=H/'headlamp-housing-core-study-v2.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source));report={'schema':1,'revision':'headlamp-housing-core-study-v2','source_sha256':sha(source),'collection':C.name,'root':root.name,'object':a.name,'triangles':len(areas),'non_manifold_edges':nonmanifold,'signed_volume_m3':volume,'min_triangle_area_m2':min(areas),'source_unbevelled_min_face_custom_normal_dot':min_dot,'post_CSG_min_face_custom_normal_dot':min_csg_dot,'normal_provenance':'Exact inputvolume and originaltriangle IDs, barycentric interpolation of actual pre-union evaluatedcorner normals; no nearestsurface heuristic or global WeightedNormal','CSG_stages':cs['stages'],'nominal_normal_wall_m':WALL,'edge_radius_before_unions_m':ER,'known_missing_units':['Rear upper/side/lower mounting ears','Rear ribs','Mounting holes/slots','Uppercentre clip detail unresolved'],'state':'Partial core construction only; not a complete housing, no GLB or final96 planned for this intermediate','art_accepted':False};(O/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
