"""Original separate LH outerleg, relatedPF121018, bounded unseen interfaces."""
import bpy,bmesh,math,json,hashlib,tempfile,subprocess,shutil,os
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/fork-outer-left-v1';P=json.loads((HERE/'parameters.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
col=bpy.data.collections.new('WEWA_FORK_OUTER_LEFT_ISOLATED');s.collection.children.link(col);construction=bpy.data.collections.new('OUTER_LEFT_ORIGINAL_VOLUMES_AND_CUTTERS');s.collection.children.link(construction);studio=bpy.data.collections.new('STUDIO_NOT_EXPORTED');s.collection.children.link(studio)
def obj(name,vs,fs):
 m=bpy.data.meshes.new(name);m.from_pydata(vs,[],fs);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(m);bm.free();o=bpy.data.objects.new(name,m);construction.objects.link(o);return o
def bezier(points,steps=12):
 a,b,c,d=[Vector(p)for p in points];return [(1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d for t in[k/steps for k in range(steps+1)]]
def heel_sections():
 sections=[]
 for i in range(25):
  theta=math.pi/2*i/24;sections.append((.0163*math.sin(theta),.01875*math.sin(theta),-.018*math.cos(theta),2+.8*math.sin(theta)**4))
 for i in range(1,37):
  t=i/36;u=1-t
  rx=u**3*.0163+3*u*u*t*.0163+3*u*t*t*.01875+t**3*.01875
  ry=u**3*.01875+3*u*u*t*.01875+3*u*t*t*.01875+t**3*.01875
  z=3*u*u*t*.020+3*u*t*t*.023+t**3*.045
  n=2.8-.8*(3*t*t-2*t*t*t);sections.append((rx,ry,z,n))
 return sections
profile=heel_sections()
def path(points,steps=12):
 for q in bezier(points,steps):
  last=profile[-1]if profile else None
  previous=Vector((last[0],last[1]if len(last)==2 else last[2]))if last is not None else None
  if previous is None or(q-previous).length>1e-10:profile.append(q)
# Exterior bottom/shoulder/body/neck, then open annulus and estimated blind cavity.
path([(.01875,.045),(.01875,.12),(.0200,.245),(.0205,.300)],55)
path([(.0205,.300),(.0206,.304),(.0238,.304),(.024,.308)],14)
path([(.024,.308),(.024,.314),(.024,.321),(.024,.3235)],10)
path([(.024,.3235),(.024,.3246),(.0238,.325),(.0232,.325)],8)
path([(.0232,.325),(.0228,.325),(.0218,.325),(.0215,.3247)],6)
path([(.0215,.3247),(.0215,.321),(.0215,.316),(.0215,.313)],10)
path([(.0215,.313),(.0215,.310),(.0158,.310),(.0158,.307)],14)
path([(.0158,.307),(.0158,.23),(.0158,.13),(.0158,.057)],45)
path([(.0158,.057),(.0158,.0555),(.0148,.055),(0,.055)],12)
def lathe_poles(name,profile):
 N=P['radial_segments'];vertices=[];rings=[];faces=[]
 for section in profile:
  if len(section)==2:r,z=section;rx=ry=r;exponent=2
  else:rx,ry,z,exponent=section
  if abs(rx)<1e-12:rings.append([len(vertices)]);vertices.append((0,0,z))
  else:
   rings.append(list(range(len(vertices),len(vertices)+N)))
   for j in range(N):
    c=math.cos(math.tau*j/N);d=math.sin(math.tau*j/N);vertices.append((rx*math.copysign(abs(c)**(2/exponent),c),ry*math.copysign(abs(d)**(2/exponent),d),z))
 for k,a in enumerate(rings):
  b=rings[(k+1)%len(rings)]
  if len(a)==len(b)==1:continue
  if len(a)==1:faces.extend((a[0],b[(j+1)%N],b[j])for j in range(N))
  elif len(b)==1:faces.extend((a[j],a[(j+1)%N],b[0])for j in range(N))
  else:faces.extend((a[j],a[(j+1)%N],b[(j+1)%N],b[j])for j in range(N))
 return obj(name,vertices,faces)
def smooth_closed(controls,steps=10):
 c=[Vector(p)for p in controls];out=[]
 for i in range(len(c)):
  a,b,d,e=[c[k%len(c)]for k in[i-1,i,i+1,i+2]]
  for j in range(steps):
   t=j/steps;out.append(.5*(2*b+(-a+d)*t+(2*a-5*b+4*d-e)*t*t+(-a+3*b-3*d+e)*t*t*t))
 return out
def prism_x(name,outline,x0,x1,radius=0):
 n=len(outline);v=[(x,p[0],p[1])for x in[x0,x1]for p in outline];f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)];o=obj(name,v,f)
 if radius:
  b=o.modifiers.new('Original edge radii before solid union','BEVEL');b.width=radius;b.segments=4;b.limit_method='ANGLE';b.angle_limit=.5
 return o
def cylinder_x(name,r,depth,center,radius=0):
 bpy.ops.mesh.primitive_cylinder_add(vertices=160,radius=r,depth=depth,location=center);o=bpy.context.object
 for c in list(o.users_collection):c.objects.unlink(o)
 construction.objects.link(o);o.name=name;o.rotation_euler.y=math.pi/2
 if radius:
  b=o.modifiers.new('Original barrel edge radius before union','BEVEL');b.width=radius;b.segments=4;b.limit_method='ANGLE';b.angle_limit=.5
 return o
def rounded_rectangle(yhalf,zmin,zmax,radius,steps=12):
 points=[]
 for cy,cz,a0 in[(yhalf-radius,zmin+radius,-math.pi/2),(yhalf-radius,zmax-radius,0),(-yhalf+radius,zmax-radius,math.pi/2),(-yhalf+radius,zmin+radius,math.pi)]:
  points.extend((cy+radius*math.cos(a0+a*math.pi/2/steps),cz+radius*math.sin(a0+a*math.pi/2/steps))for a in range(steps+1))
 return points
base=lathe_poles('Original continuous heel hollow lowerleg and expandedneck',profile);features=[];drills=[]
# Heel and tube are already one continuous original surface; no overlapping
# volume union at the cast body transition. Uncalibrated proportions estimated.

features.append(cylinder_x('Observed axleeye raised barrel',P['axle_boss_outer_radius_working_m'],P['axle_boss_width_working_m'],(0,0,0),.0006))
ear_positive=smooth_closed([(.013,.201),(.023,.202),(.031,.208),(.034,.218),(.031,.228),(.023,.234),(.013,.235)],9)
for side in[-1,1]:
 outline=[(side*p[0],p[1])for p in ear_positive];features.append(prism_x('Observed integral mid mounting ear '+str(side),outline,-P['ear_thickness_working_m']/2,P['ear_thickness_working_m']/2,.0012));drills.append(cylinder_x('Estimated visible ear aperture '+str(side),P['ear_hole_radius_working_m'],.070,(0,side*.027,.218)))
features.append(prism_x('Observed inboard longitudinal feature - functionunknown',rounded_rectangle(.010,.015,.055,.002),-.022,-.012,.0006))
drills.append(cylinder_x('True axle passage - diameter estimated',P['axle_bore_diameter_working_m']/2,.10,(0,0,0)))
# Small outboard edge break visible in the related photograph; width estimated.
edge=P['outboard_axle_entry_chamfer_working_m'];start=P['axle_boss_width_working_m']/2-edge;depth=.004
bpy.ops.mesh.primitive_cone_add(vertices=160,radius1=P['axle_bore_diameter_working_m']/2,radius2=P['axle_bore_diameter_working_m']/2+depth,depth=depth,location=(start+depth/2,0,0));entry=bpy.context.object
for c in list(entry.users_collection):c.objects.unlink(entry)
construction.objects.link(entry);entry.name='Estimated observed outboard axle aperture edgebreak';entry.rotation_euler.y=math.pi/2;drills.append(entry)
drills.append(prism_x('Estimated bounded recess in observed inboardfeature',rounded_rectangle(.007,.0215,.0485,.0015),-.035,-.019,.00035))
operand_checks=[]
def volume(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(m);v0=bm.calc_volume(signed=True);before=len(bm.verts);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-10);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);nm=sum(not e.is_manifold for e in bm.edges);assert not nm,(o.name,nm);v1=bm.calc_volume(signed=True);assert v1>0;clean=bpy.data.meshes.new('Temporary evaluated solid operand');bm.to_mesh(clean);bm.free();clean.calc_loop_triangles();row={'name':o.name,'vertices':[list(o.matrix_world@v.co)for v in clean.vertices],'triangles':[list(t.vertices)for t in clean.loop_triangles]};operand_checks.append({'name':o.name,'evaluated_vertices_before':before,'clean_vertices':len(clean.vertices),'signed_volume_before_m3':v0,'signed_volume_after_m3':v1,'nonmanifold_edges':nm});bpy.data.meshes.remove(clean);ev.to_mesh_clear();return row
csg=ROOT/'assets-src/moto-components/front-brake-plate/csg.py'
with tempfile.TemporaryDirectory(prefix='wewa-fork-outer-left-')as t:
 inp=Path(t)/'input.json';out=Path(t)/'output.json';inp.write_text(json.dumps({'base':volume(base),'features':[volume(o)for o in features],'drills':[volume(o)for o in drills]}));env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'};subprocess.run([shutil.which('python'),str(csg),str(inp),str(out)],check=True,env=env);fused=json.loads(out.read_text())
o=obj('LH fork outer body - relatedPF121018 candidate',fused['vertices'],fused['triangles']);construction.objects.unlink(o);col.objects.link(o);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-10);bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
# Reconnect only coplanar cap diagonals, preserving every point/boundary.
# The initial Boolean triangulation left four zero Mikk tangents on slivers.
flat_retriangulation=[]
for plane in[-.022,-.019,-.008,.008,-P['axle_boss_width_working_m']/2,P['axle_boss_width_working_m']/2]:
 faces=[f for f in bm.faces if all(abs(v.co.x-plane)<2e-8 for v in f.verts)];selected=set(faces);edges=[e for e in bm.edges if len(e.link_faces)==2 and all(f in selected for f in e.link_faces)]
 if not edges:continue
 before=bm.calc_volume(signed=True);positions={tuple(v.co)for v in bm.verts};result=bmesh.ops.beautify_fill(bm,faces=faces,edges=edges,method='AREA');bmesh.ops.recalc_face_normals(bm,faces=bm.faces);after=bm.calc_volume(signed=True);assert positions=={tuple(v.co)for v in bm.verts}and abs(after/before-1)<1e-7
 flat_retriangulation.append({'plane_x_m':plane,'faces':len(faces),'candidate_internal_edges':len(edges),'volume_relative_change':abs(after/before-1),'vertex_positions_preserved':True,'operation':'Blenderbeautify_fill AREA, coplanar interior diagonals only'})
bm.to_mesh(o.data);bm.free();o.data.update();o.data.set_sharp_from_angle(angle=.65)
# Preserve curved wall interpolation and explicit planar machining/pocket faces.
for f in o.data.polygons:
 points=[o.data.vertices[i].co for i in f.vertices];flat=False
 for x in[-.022,-.019,-.008,.008,-P['axle_boss_width_working_m']/2,P['axle_boss_width_working_m']/2]:
  if all(abs(p.x-x)<3e-7 for p in points):flat=True
 if all(abs(p.z-.055)<3e-7 for p in points)or all(abs(p.z-.325)<3e-7 for p in points):flat=True
 f.use_smooth=not flat
o.data.update();m=bpy.data.materials.new('Neutral outerleg geometry - finalfinish pending');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.22,.24,.26,1);p.inputs['Roughness'].default_value=.30;o.data.materials.append(m)
# Physical source UVs before any normal maps; poles use planar projection.
uv=o.data.uv_layers.new(name='Estimated10mm dominant box projection')
for f in o.data.polygons:
 axis=max(range(3),key=lambda a:abs(f.normal[a]));sign=1 if f.normal[axis]>=0 else-1
 for li in f.loop_indices:
  v=o.data.vertices[o.data.loops[li].vertex_index].co;pair=(sign*v.y,v.z)if axis==0 else(-sign*v.x,v.z)if axis==1 else(sign*v.x,v.y);uv.data[li].uv=(pair[0]/.010,pair[1]/.010)
for x in construction.objects:x.hide_render=True;x.hide_set(True)
o.data.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(o.data);unseen=set(bm.verts);shells=0
while unseen:
 shells+=1;stack=[unseen.pop()]
 while stack:
  for ed in stack.pop().link_edges:
   for v in ed.verts:
    if v in unseen:unseen.remove(v);stack.append(v)
areas=[(o.data.vertices[t.vertices[1]].co-o.data.vertices[t.vertices[0]].co).cross(o.data.vertices[t.vertices[2]].co-o.data.vertices[t.vertices[0]].co).length/2 for t in o.data.loop_triangles];nm=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);bm.free();tree=BVHTree.FromPolygons([v.co for v in o.data.vertices],[list(t.vertices)for t in o.data.loop_triangles],all_triangles=True);probes=[]
for label,y,z in[('axle',0,0),('ear_front',-.027,.218),('ear_rear',.027,.218)]:
 clear=tree.ray_cast(Vector((-.060,y,z)),Vector((1,0,0)),.12)[0]is None;probes.append({'name':label,'centre_yz_m':[y,z],'axis_X_clear':clear});assert clear,(label,probes)
floor=tree.ray_cast(Vector((0,0,.4)),Vector((0,0,-1)),.5)[0];pocket=tree.ray_cast(Vector((-.05,0,.035)),Vector((1,0,0)),.1)[0];rim=tree.ray_cast(Vector((-.05,.0085,.035)),Vector((1,0,0)),.1)[0];assert floor and abs(floor.z-.055)<.00005;assert pocket and abs(pocket.x+.019)<.00005;assert rim and abs(rim.x+.022)<.0002
r={'component_id':P['component_id'],'revision':P['revision'],'collection':col.name,'frame':P['frame'],'vertices':len(o.data.vertices),'triangles':len(o.data.loop_triangles),'connected_shells':shells,'nonmanifold_edges':nm,'signed_volume_m3':vol,'min_triangle_area_m2':min(areas),'zero_area_triangles_at_1e18_m2':sum(a<=1e-18 for a in areas),'passage_probes':probes,'estimated_blind_cavity_floor_z_actual_m':floor.z,'inboard_pocket_floor_x_actual_m':pocket.x,'inboard_pad_face_x_actual_m':rim.x,'pocket_depth_actual_m':pocket.x-rim.x,'coplanar_retriangulation':flat_retriangulation,'construction_operand_checks':operand_checks,'csg_tool':{k:fused[k]for k in['tool','tool_version','solid_components']},'csg_helper_sha256':hashlib.sha256(csg.read_bytes()).hexdigest(),'csg_stages':fused['stages'],'all_dimensions_estimated':True,'hidden_hydraulics_modelled':False,'exact_RDC_verified':False,'cast_identifier_glyphs_modelled':False,'bellows_interface_verified':False,'art_accepted':False};(OUT/'preflight-diagnostic.json').write_text(json.dumps(r,indent=2)+'\n');assert shells==1 and not nm and not r['zero_area_triangles_at_1e18_m2']and vol>0,r
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.gltf(filepath=str(HERE/'fork-outer-left-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True)
w=bpy.data.worlds.new('Outerleg neutral studio');w.use_nodes=True;s.world=w;w.node_tree.nodes['Background'].inputs[0].default_value=(.30,.32,.35,1);w.node_tree.nodes['Background'].inputs[1].default_value=.45
for name,loc,power,size in[('KEY',(.40,.35,.52),10,.35),('FILL',(-.35,.30,.22),5,.30),('EDGE',(.25,-.35,.30),7,.30)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;x=bpy.data.objects.new(name,d);studio.objects.link(x);x.location=loc;x.rotation_euler=(Vector((0,0,.15))-x.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('OUTER_LEFT_CAMERA',bpy.data.cameras.new('OUTER_LEFT_CAMERA'));studio.objects.link(cam);s.camera=cam;cam.location=(.60,.14,.30);cam.rotation_euler=(Vector((0,0,.15))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.44;cam.data.clip_start=.001;cam.data.clip_end=5;s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.render.resolution_x=1000;s.render.resolution_y=1400;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'fork-outer-left-v1.blend'),compress=True);r['source_sha256']=hashlib.sha256((HERE/'fork-outer-left-v1.blend').read_bytes()).hexdigest();r['export_sha256']=hashlib.sha256((HERE/'fork-outer-left-inspection.glb').read_bytes()).hexdigest();(OUT/'source-geometry-check.json').write_text(json.dumps(r,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');print('WEWA_FORK_OUTER_LEFT',json.dumps(r))
