"""Finite wrapped panel SHAPE STUDY. No fabricated holes, mount or photometric claim."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/instrument-visor-shell-study-v1';OUT.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();g=json.loads((HERE/'planar-grid-v1.json').read_text());outline=json.loads((HERE/'outline-v1.json').read_text());bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;source=bpy.data.collections.new('WEWA_INSTRUMENT_VISOR_SHELL_STUDY');s.collection.children.link(source);guides=bpy.data.collections.new('VISOR original editable curve guides');s.collection.children.link(guides);studio=bpy.data.collections.new('VISOR neutral studio not exported');s.collection.children.link(studio);angle=math.radians(42);U=Vector((1,0,0));V=Vector((0,math.sin(angle),math.cos(angle)));N=U.cross(V);origin=Vector((0,-.285,0));half=.125;sag=.040;thickness=.0025

def surface(x,t):return origin+U*x+V*t-N*sag*(x/half)**2

def normal(x):return(N+U*(2*sag*x/(half*half))).normalized()
verts=[]
for sign in [1,-1]:
 for x,t in g['vertices_2D_m']:verts.append(tuple(surface(x,t)+normal(x)*(sign*thickness/2)))
count=len(g['vertices_2D_m']);faces=[tuple(f)for f in g['triangles']]+[tuple(i+count for i in reversed(f))for f in g['triangles']];directed={}
for f in g['triangles']:
 for a,b in zip(f,f[1:]+f[:1]):
  key=tuple(sorted((a,b)))
  if key in directed:directed[key]=None
  else:directed[key]=(a,b)
boundary=[e for e in directed.values()if e is not None]
for a,b in boundary:faces.append((a,a+count,b+count,b))
data=bpy.data.meshes.new('Original wrapped visor shell finite wall, edge finish pending');data.from_pydata(verts,[],faces);data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(data);bm.free();ob=bpy.data.objects.new('Visor finite curved shell - conditional estimated study',data);source.objects.link(ob)
# Normals follow the analytic front/back surfaces; side remains a sharp study cut.
# No smooth face/side averaging, which would invent a calotte at an unrounded edge.
side_tangents={}
for a,b in boundary:
 direction=(surface(*g['vertices_2D_m'][b])-surface(*g['vertices_2D_m'][a])).normalized()
 for i in [a,b]:side_tangents[i]=side_tangents.get(i,Vector())+direction
loops=[];triangles=len(g['triangles'])
for f in data.polygons:
 f.use_smooth=True
 for li in f.loop_indices:
  i=data.loops[li].vertex_index;base=i%count;n=normal(g['vertices_2D_m'][base][0])
  if f.index<triangles:n=n
  elif f.index<2*triangles:n=-n
  else:n=side_tangents[base].normalized().cross(n).normalized()
  loops.append(n)
data.normals_split_custom_set(loops);uv=data.uv_layers.new(name='Original panel midsurface physical10mm UV')
successor={a:b for a,b in boundary};start=next(iter(successor));boundary_s={start:0.};cursor=start
while True:
 following=successor[cursor];distance=(surface(*g['vertices_2D_m'][following])-surface(*g['vertices_2D_m'][cursor])).length
 if following==start:perimeter=boundary_s[cursor]+distance;break
 boundary_s[following]=boundary_s[cursor]+distance;cursor=following
def transverse_arc(x):
 a=2*sag/(half*half)
 return .5*(x*math.sqrt(1+(a*x)**2)+math.asinh(a*x)/a)
for f in data.polygons:
 base_ids=[data.loops[li].vertex_index%count for li in f.loop_indices]
 seam=f.index>=2*triangles and max(boundary_s[i]for i in base_ids)-min(boundary_s[i]for i in base_ids)>perimeter/2
 for li in f.loop_indices:
  vertex=data.loops[li].vertex_index;base=vertex%count;x,t=g['vertices_2D_m'][base]
  if f.index<2*triangles:uv.data[li].uv=(transverse_arc(x)/.010,t/.010)
  else:
   arc=boundary_s[base]+(perimeter if seam and boundary_s[base]<perimeter/2 else 0)
   uv.data[li].uv=(arc/.010,(0 if vertex<count else thickness)/.010)
root=bpy.data.objects.new('VISOR_PANEL_MOUNT_ESTIMATED',None);source.objects.link(root);ob.parent=root
m=bpy.data.materials.new('VISOR shape study neutral polymer gray, no final material');m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.18,.18,.18,1);p.inputs['Roughness'].default_value=.42;ob.data.materials.append(m)
curve=bpy.data.curves.new('Original contour guide, editable C2 coefficients in outline-v1.json','CURVE');curve.dimensions='3D';sp=curve.splines.new('POLY');sp.points.add(len(outline['working_planar_outline_m'])-1)
for p,co in zip(sp.points,outline['working_planar_outline_m']):p.co=(*surface(*co),1)
sp.use_cyclic_u=True;guide=bpy.data.objects.new(curve.name,curve);guides.objects.link(guide);guide.hide_render=True;guide.hide_set(True)
# Physical closure and real evaluated triangle area, not object-name assertions.
bm=bmesh.new();bm.from_mesh(data);todo=set(bm.verts);components=0
while todo:
 components+=1;stack=[todo.pop()]
 while stack:
  for edge in stack.pop().link_edges:
   for v in edge.verts:
    if v in todo:todo.remove(v);stack.append(v)
data.calc_loop_triangles();areas=[t.area for t in data.loop_triangles];geometry={'vertices':len(data.vertices),'faces':len(data.polygons),'triangles':len(areas),'components':components,'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume_m3':bm.calc_volume(signed=True),'exact_zero_area_triangles':sum(a==0 for a in areas),'min_triangle_area_m2':min(areas)};bm.free();assert geometry['components']==1 and geometry['non_manifold_edges']==0 and geometry['signed_volume_m3']>0 and geometry['exact_zero_area_triangles']==0,geometry
bpy.ops.object.select_all(action='DESELECT');root.select_set(True);ob.select_set(True);bpy.context.view_layer.objects.active=ob;export=HERE/'instrument-visor-shell-study-v1.glb';bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_apply=True,export_tangents=False)
# Gray studio and large reflected areas expose curvature before smoked optics.
def studio_move(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 studio.objects.link(o)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.045));floor=bpy.context.object;floor.name='VISOR neutral floor';studio_move(floor);fm=bpy.data.materials.new('VISOR neutral floor gray');fm.diffuse_color=(.10,.115,.13,1);fm.use_nodes=True;fm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.10,.115,.13,1);fm.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8;floor.data.materials.append(fm)
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.45,.48,.52,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.3
for name,loc,power,size in [('key',(.40,-.70,.62),100, .45),('fill',(-.45,.05,.35),75,.40),('rim',(0,.4,.55),90,.35)]:
 light=bpy.data.lights.new('VISOR '+name,'AREA');light.energy=power;light.shape='RECTANGLE';light.size=size;light.size_y=size*.65;o=bpy.data.objects.new(light.name,light);studio.objects.link(o);o.location=loc;o.rotation_euler=(surface(0,.1425)-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new('VISOR_CAMERA');cam.clip_start=.001;cam.clip_end=10;o=bpy.data.objects.new('VISOR_CAMERA',cam);studio.objects.link(o);s.camera=o;target=surface(0,.1425);o.location=target+N*.7;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler();cam.lens=70;s.render.engine='CYCLES';s.cycles.samples=8;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.render.resolution_x=700;s.render.resolution_y=700;s.render.resolution_percentage=100;dest=HERE/'instrument-visor-shell-study-v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
report={'schema':1,'revision':'instrument-visor-shell-study-v1','source_sha256':sha(dest),'export_sha256':sha(export),'collection':source.name,'root':root.name,'object':ob.name,'geometry':geometry,'source_grid_sha256':sha(HERE/'planar-grid-v1.json'),'source_outline_sha256':sha(HERE/'outline-v1.json'),'frame':{'U':list(U),'up_V':list(V),'front_N':list(N),'origin_m':list(origin)},'working_parameters':{'width_m':.250,'developed_height_m':.285,'rake_deg':42,'transverse_wrap_sag_m':sag,'normal_wall_thickness_m':thickness},'limits':['All detailed physical dimensions and section parameters remain estimates; not camera calibrated.','This is a shape study with an intentional sharp cut edge; tiny molded edge radius/return treatment not yet modeled.','Fixing centres/diameters and hidden return flanges unresolved; no invented holes or fasteners.','Neutral gray is not a final smoked-polymer material.','All-required-components-built is false; no artistic reception.'],'art_accepted':False};(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');print('VISOR_CURVED_SHELL_STUDY',geometry,report['source_sha256'],report['export_sha256'])
