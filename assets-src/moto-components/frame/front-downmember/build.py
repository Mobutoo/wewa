"""Original non-round swept framefrontdownmember; all metrics and hiddensections estimated."""
import bpy,bmesh,math,json,hashlib,tempfile,subprocess,shutil,os
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/frame-front-downmember-v1';P=json.loads((HERE/'parameters.json').read_text());bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
col=bpy.data.collections.new('WEWA_FRAME_FRONT_DOWNMEMBER_ISOLATED');s.collection.children.link(col);construction=bpy.data.collections.new('ORIGINAL_SWEEP_AND_COLLAR_OPERANDS');s.collection.children.link(construction);studio=bpy.data.collections.new('STUDIO_NOT_EXPORTED');s.collection.children.link(studio)
def obj(name,vs,fs):
 m=bpy.data.meshes.new(name);m.from_pydata(vs,[],fs);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(m);bm.free();o=bpy.data.objects.new(name,m);construction.objects.link(o);return o
def cylinder_x(name,r,depth,center,radius=0):
 bpy.ops.mesh.primitive_cylinder_add(vertices=160,radius=r,depth=depth,location=center);o=bpy.context.object
 for c in list(o.users_collection):c.objects.unlink(o)
 construction.objects.link(o);o.name=name;o.rotation_euler.y=math.pi/2
 if radius:
  b=o.modifiers.new('Original barrel edge radius before union','BEVEL');b.width=radius;b.segments=4;b.limit_method='ANGLE';b.angle_limit=.5
 return o

def section(t):
 # Cubic centreline chosen from observed gentle descendingfront/rearflattening.
 u=1-t;Y=3*u*u*t*.080+3*u*t*t*.210+t**3*P['rear_span_working_m'];Z=3*u*u*t*(-.140)+3*u*t*t*(-.330)-t**3*P['rear_drop_working_m'];dy=3*u*u*.080+6*u*t*(.210-.080)+3*t*t*(P['rear_span_working_m']-.210);dz=3*u*u*(-.140)+6*u*t*(-.330+.140)+3*t*t*(-P['rear_drop_working_m']+.330);V=Vector((0,-dz,dy)).normalized();return Vector((0,Y,Z)),V

def boundary(hw,hh,rad,steps=12):
 out=[]
 for cx,cv,start in[(hw-rad,-hh+rad,-math.pi/2),(hw-rad,hh-rad,0),(-hw+rad,hh-rad,math.pi/2),(-hw+rad,-hh+rad,math.pi)]:
  for k in range(steps+1):
   a=start+math.pi/2*k/steps;out.append((cx+rad*math.cos(a),cv+rad*math.sin(a)))
 return out

def tube():
 vertices=[];rings=[[],[]];steps=80;N=52
 for inner in[False,True]:
  for i in range(steps+1):
   t=i/steps;C,V=section(t);flare=max(0,(t-.83)/.17)**2;w=(P['front_outer_width_m']*(1-t)+P['rear_outer_width_m']*t)/2+.003*flare;hh=(P['front_outer_height_m']*(1-t)+P['rear_outer_height_m']*t)/2+.002*flare;wall=P['wall_working_m']if inner else 0;profile=boundary(w-wall,hh-wall,P['corner_radius_working_m']-wall);assert len(profile)==N;ring=[]
   for x,v in profile:ring.append(len(vertices));vertices.append(tuple(C+Vector((x,0,0))+V*v))
   rings[int(inner)].append(ring)
 faces=[]
 for inner in[False,True]:
  for i in range(steps):
   a=rings[int(inner)][i];b=rings[int(inner)][i+1]
   for j in range(N):
    f=(a[j],a[(j+1)%N],b[(j+1)%N],b[j]);faces.append(tuple(reversed(f))if inner else f)
 for i in[0,steps]:
  a=rings[0][i];b=rings[1][i]
  for j in range(N):
   f=(a[j],b[j],b[(j+1)%N],a[(j+1)%N]);faces.append(tuple(reversed(f))if i else f)
 return obj('Original continuous swept open non-round envelope',vertices,faces)
base=tube();features=[];drills=[];openings=[]
for i,y in enumerate(P['side_openings_y_m']):
 lo=0.;hi=1.
 for _ in range(50):
  t=(lo+hi)/2
  if section(t)[0].y<y:lo=t
  else:hi=t
 t=(lo+hi)/2;C,V=section(t);x=(P['front_outer_width_m']*(1-t)+P['rear_outer_width_m']*t)/2;drills.append(cylinder_x('Body opening candidate, fixingnotincluded '+str(i+1),P['bore_radius_m'],.065,(.0325,C.y,C.z)));openings.append({'index':i+1,'centre_yz_m':[C.y,C.z],'outer_face_x_m':x})
operand_checks=[]
def volume(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(m);v0=bm.calc_volume(signed=True);before=len(bm.verts);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-10);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);nm=sum(not e.is_manifold for e in bm.edges);assert not nm,(o.name,nm);v1=bm.calc_volume(signed=True);assert v1>0;clean=bpy.data.meshes.new('Temporary evaluated solid operand');bm.to_mesh(clean);bm.free();clean.calc_loop_triangles();row={'name':o.name,'vertices':[list(o.matrix_world@v.co)for v in clean.vertices],'triangles':[list(t.vertices)for t in clean.loop_triangles]};operand_checks.append({'name':o.name,'evaluated_vertices_before':before,'clean_vertices':len(clean.vertices),'signed_volume_before_m3':v0,'signed_volume_after_m3':v1,'nonmanifold_edges':nm});bpy.data.meshes.remove(clean);ev.to_mesh_clear();return row
csg=ROOT/'assets-src/moto-components/front-brake-plate/csg.py'
with tempfile.TemporaryDirectory(prefix='wewa-frame-downmember-')as t:
 inp=Path(t)/'input.json';out=Path(t)/'output.json';inp.write_text(json.dumps({'base':volume(base),'features':[volume(o)for o in features],'drills':[volume(o)for o in drills]}));env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'};subprocess.run([shutil.which('python'),str(csg),str(inp),str(out)],check=True,env=env);fused=json.loads(out.read_text())

o=obj('Front framedownmember non-round isolated candidate',fused['vertices'],fused['triangles']);construction.objects.unlink(o);col.objects.link(o);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-10);bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
triangulation=[]
for p in openings:
 x=p['outer_face_x_m'];faces=[f for f in bm.faces if all(abs(v.co.x-x)<2e-8 for v in f.verts)];selected=set(faces);edges=[e for e in bm.edges if len(e.link_faces)==2 and all(f in selected for f in e.link_faces)]
 if edges:
  before=bm.calc_volume(signed=True);points={tuple(v.co)for v in bm.verts};bmesh.ops.beautify_fill(bm,faces=faces,edges=edges,method='AREA');bmesh.ops.recalc_face_normals(bm,faces=bm.faces);assert points=={tuple(v.co)for v in bm.verts};triangulation.append({'plane_x_m':x,'faces':len(faces),'position_preserved':True,'volume_relative_change':abs(bm.calc_volume(signed=True)/before-1)})
bm.to_mesh(o.data);bm.free();o.data.update();o.data.set_sharp_from_angle(angle=.60)
for f in o.data.polygons:
 f.use_smooth=not any(all(abs(o.data.vertices[v].co.x-p['outer_face_x_m'])<3e-7 for v in f.vertices)for p in openings)
o.data.update();uv=o.data.uv_layers.new(name='Estimated20mm dominantplane charts')
for f in o.data.polygons:
 axis=max(range(3),key=lambda a:abs(f.normal[a]));sign=1 if f.normal[axis]>=0 else-1
 for li in f.loop_indices:
  v=o.data.vertices[o.data.loops[li].vertex_index].co;q=(sign*v.y,v.z)if axis==0 else(-sign*v.x,v.z)if axis==1 else(sign*v.x,v.y);uv.data[li].uv=(q[0]/.02,q[1]/.02)
m=bpy.data.materials.new('Neutral framebackbone - G3');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.28,.30,.33,1);p.inputs['Roughness'].default_value=.30;o.data.materials.append(m)
for x in construction.objects:x.hide_render=True;x.hide_set(True)
o.data.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(o.data);nm=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);unseen=set(bm.verts);shells=0
while unseen:
 shells+=1;stack=[unseen.pop()]
 while stack:
  for e in stack.pop().link_edges:
   for v in e.verts:
    if v in unseen:unseen.remove(v);stack.append(v)
bm.free();areas=[(o.data.vertices[t.vertices[1]].co-o.data.vertices[t.vertices[0]].co).cross(o.data.vertices[t.vertices[2]].co-o.data.vertices[t.vertices[0]].co).length/2 for t in o.data.loop_triangles];tree=BVHTree.FromPolygons([v.co for v in o.data.vertices],[list(t.vertices)for t in o.data.loop_triangles],all_triangles=True);probes=[]
for p in openings:
 y,z=p['centre_yz_m'];hit=tree.ray_cast(Vector((.06,y,z)),Vector((-1,0,0)),.06)[0];back=tree.ray_cast(Vector((-.06,y,z)),Vector((1,0,0)),.06)[0];assert hit is None and back is not None,p;probes.append({**p,'positiveX_halfpassage_clear':True,'opposite_wall_not_mirrored_clear':False})
assert shells==1 and not nm and vol>0 and min(areas)>1e-18
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;export=HERE/'frame-front-downmember-inspection.glb';bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True)
w=bpy.data.worlds.new('Framedownmember neutral studio');w.use_nodes=True;s.world=w;w.node_tree.nodes['Background'].inputs[0].default_value=(.30,.32,.35,1);w.node_tree.nodes['Background'].inputs[1].default_value=.4
for name,loc,power,size in[('KEY',(.4,.35,.35),8,.35),('FILL',(-.35,.2,.2),4,.3),('EDGE',(.1,-.25,.3),5,.35)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;x=bpy.data.objects.new(name,d);studio.objects.link(x);x.location=loc;x.rotation_euler=(Vector((0,.125,-.20))-x.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('FRAME_DOWNMEMBER_CAMERA',bpy.data.cameras.new('FRAME_DOWNMEMBER_CAMERA'));studio.objects.link(cam);s.camera=cam;cam.location=(.65,.05,.05);cam.rotation_euler=(Vector((0,.125,-.20))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.58;cam.data.clip_start=.001;cam.data.clip_end=5;s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.render.resolution_x=1400;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';source=HERE/'frame-front-downmember-v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
r={'component_id':P['component_id'],'revision':P['revision'],'collection':col.name,'frame':P['frame'],'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'vertices':len(o.data.vertices),'triangles':len(o.data.loop_triangles),'connected_shells':shells,'nonmanifold_edges':nm,'signed_volume_m3':vol,'min_triangle_area_m2':min(areas),'zero_area_triangles_at_1e18_m2':sum(a<=1e-18 for a in areas),'body_openings':openings,'passage_probes':probes,'construction_operand_checks':operand_checks,'coplanar_retriangulation':triangulation,'csg_tool':{k:fused[k]for k in['tool','tool_version','solid_components']},'csg_helper_sha256':hashlib.sha256(csg.read_bytes()).hexdigest(),'all_physical_dimensions_estimated':True,'physical_photo_side_verified':False,'hidden_thread_or_mechanism_modelled':False,'complete_frame_built':False,'art_accepted':False};(OUT/'source-geometry-check.json').write_text(json.dumps(r,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');print('WEWA_FRAME_DOWNMEMBER',json.dumps(r))
