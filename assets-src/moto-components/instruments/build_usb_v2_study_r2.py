"""G3 original USB surround/insert shape study; all dimensions and relief estimated.
This file does not edit the historical instrument source or claim a recovered camera.
"""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/instruments-usb-v2-study-r2';OUT.mkdir(parents=True,exist_ok=True)
planpath=ROOT/'creative/research/instruments-v2/usb-shape-plan-r2.json';P=json.loads(planpath.read_text());ref=Path(P['reference_private_path']);assert hashlib.sha256(ref.read_bytes()).hexdigest()==P['reference_sha256']
base=HERE/'instruments-v1.blend';base_sha=hashlib.sha256(base.read_bytes()).hexdigest();assert base_sha=='e3321cee34967f7749dbfa8650fe01c404137c55cfb5c42881363f098cb91ec0'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
parts=bpy.data.collections.new('WEWA_INSTRUMENT_USB_STUDY_V2');scene.collection.children.link(parts);guides=bpy.data.collections.new('USB original editable contour guides v2');scene.collection.children.link(guides);studio=bpy.data.collections.new('USB_STUDY_STUDIO_NOT_EXPORTED');scene.collection.children.link(studio)
root=bpy.data.objects.new('INSTRUMENT_USB_STUDY_MOUNT',None);parts.objects.link(root);root.location=(0,-.12,.075);root.rotation_euler=tuple(math.radians(x)for x in[58,0,180]);root['all_dimensions_estimated']=True;root['part_count_not_certified']=True;root['art_accepted']=False
C=Vector((0,.038));T=P['working_shape_transform'];sx=T['x_scale_m_per_px_estimated'];sy=T['y_scale_m_per_px_estimated'];anchor=T['native_anchor_px'];N=256

def xy(p):return Vector((C.x+(p[0]-anchor[0])*sx,C.y+(p[1]-anchor[1])*sy))
def evaluate(segments):
 points=[]
 for segment in segments:
  a,b,c,d=[xy(p)for p in segment]
  for k in range(64):
   t=k/64;points.append((1-t)**3*a+3*t*(1-t)**2*b+3*t*t*(1-t)*c+t**3*d)
 return points

def guide(name,segments):
 data=bpy.data.curves.new(name,'CURVE');data.dimensions='2D';data.resolution_u=16;s=data.splines.new('BEZIER');s.bezier_points.add(len(segments)-1);s.use_cyclic_u=True
 for i,(p,seg)in enumerate(zip(s.bezier_points,segments)):
  p.co=(*xy(seg[0]),0);p.handle_left_type='FREE';p.handle_right_type='FREE';p.handle_left=(*xy(segments[(i-1)%len(segments)][2]),0);p.handle_right=(*xy(seg[1]),0)
 o=bpy.data.objects.new(name,data);guides.objects.link(o);o.hide_render=True;o.hide_set(True);return o

def radial(poly):
 def cross(a,b):return a.x*b.y-a.y*b.x
 result=[]
 for i in range(N):
  a=math.tau*i/N;direction=Vector((math.cos(a),math.sin(a)));hits=[]
  for aa,bb in zip(poly,poly[1:]+poly[:1]):
   v=bb-aa;den=cross(direction,v)
   if abs(den)<1e-14:continue
   t=cross(aa-C,v)/den;u=cross(aa-C,direction)/den
   if t>0 and -.000001<=u<1.000001:hits.append(t)
  hits.sort();unique=[]
  for h in hits:
   if not unique or abs(h-unique[-1])>1e-9:unique.append(h)
  assert len(unique)==1,(i,unique)
  result.append(C+direction*unique[0])
 return result
outer=radial(evaluate(P['outer_bezier_px']));inner=radial(evaluate(P['capsule_bezier_px']));guide('EDITABLE contoured surround native outline v2',P['outer_bezier_px']);guide('EDITABLE capsule boundary native outline v2',P['capsule_bezier_px']);guides.hide_render=True

def scale(poly,f):return [C+(p-C)*f for p in poly]
def blend(a,b,f):return [(1-f)*x+f*y for x,y in zip(a,b)]
def material(name,color):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*color,1);n.inputs['Roughness'].default_value=.42;return m
clay=material('USB shape neutral gray - no documentary BRDF claim',(.22,.22,.22))

def loft(name,sections):
 vertices=[];rings=[]
 for contour,z in sections:
  ids=[]
  for p in([C]if contour is None else contour):ids.append(len(vertices));vertices.append((p.x,p.y,z))
  rings.append(ids)
 faces=[]
 for j,a in enumerate(rings):
  b=rings[(j+1)%len(rings)]
  if len(a)==len(b)==1:continue
  for i in range(N):faces.append((a[0],b[(i+1)%N],b[i])if len(a)==1 else(a[i],a[(i+1)%N],b[0])if len(b)==1 else(a[i],a[(i+1)%N],b[(i+1)%N],b[i]))
 data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(data);bm.free();o=bpy.data.objects.new(name,data);parts.objects.link(o);o.parent=root;o.data.materials.append(clay);o['structural_closed_volume']=True;o['construction_estimate_not_OEM_part_count']=True
 for p in data.polygons:p.use_smooth=(max(data.vertices[i].co.z for i in p.vertices)-min(data.vertices[i].co.z for i in p.vertices)>1e-9)
 return o
base_sections=[(None,.031),(scale(outer,.965),.031),(scale(outer,.99),.0313),(outer,.032),(outer,.0335),(scale(outer,.99),.0343),(scale(outer,.975),.0347),(scale(outer,.965),.0348),(blend(scale(outer,.965),scale(inner,1.20),.33),.0348),(blend(scale(outer,.965),scale(inner,1.20),.67),.0348),(scale(inner,1.20),.0348),(scale(inner,1.16),.0350),(scale(inner,1.12),.0355),(scale(inner,1.075),.0363),(scale(inner,1.040),.0368),(scale(inner,1.025),.0368),(scale(inner,1.005),.0363),(scale(inner,1.005),.0330),(None,.0330)]
insert_sections=[(None,.03315),(scale(inner,.97),.03315),(scale(inner,.985),.0334),(scale(inner,.985),.0347),(scale(inner,.97),.03505),(scale(inner,.90),.0353),(scale(inner,.60),.03538),(None,.0354)]
base_obj=loft('USB contoured surround - closed v2',base_sections);insert=loft('USB inset capsule face - closed v2',insert_sections)
bpy.context.view_layer.update();rows=[]
for o in [base_obj,insert]:
 bm=bmesh.new();bm.from_mesh(o.data);edges=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);left=set(bm.verts);components=0
 while left:
  components+=1;pending=[left.pop()]
  while pending:
   for e in pending.pop().link_edges:
    for v in e.verts:
     if v in left:left.remove(v);pending.append(v)
 bm.free();o.data.calc_loop_triangles();areas=[(o.data.vertices[t.vertices[1]].co-o.data.vertices[t.vertices[0]].co).cross(o.data.vertices[t.vertices[2]].co-o.data.vertices[t.vertices[0]].co).length/2 for t in o.data.loop_triangles];assert edges==0 and components==1 and vol>0 and min(areas)>0,(o.name,edges,components,vol,min(areas));rows.append({'object':o.name,'closed_connected_positive_volume':True,'non_manifold_edges':edges,'connected_components':components,'volume_m3':vol,'triangles':len(areas),'minimum_triangle_area_m2':min(areas),'local_bounds_m':[[min(v.co[k]for v in o.data.vertices),max(v.co[k]for v in o.data.vertices)]for k in range(3)]})
trees=[BVHTree.FromPolygons([v.co for v in o.data.vertices],[tuple(p.vertices)for p in o.data.polygons])for o in[base_obj,insert]];crossings=len(trees[0].overlap(trees[1]));assert crossings==0,crossings
bpy.ops.object.select_all(action='DESELECT')
for o in parts.objects:o.select_set(True)
bpy.context.view_layer.objects.active=base_obj;glb=HERE/'instruments-usb-v2-study-r2.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True,export_tangents=False)
# Neutral studio, separate from the two study solids.
world=bpy.data.worlds.new('USB study neutral world');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.28,.28,.28,1);world.node_tree.nodes['Background'].inputs[1].default_value=.30;scene.world=world
q=root.matrix_world.to_3x3();normal=q@Vector((0,0,1));u=q@Vector((1,0,0));v=q@Vector((0,1,0));target=root.matrix_world@Vector((0,.038,.0345))
for name,offset,power,size in [('USB_GRAY_KEY',normal*.20-u*.08+v*.10,.8,.18),('USB_GRAY_FILL',normal*.15+u*.12,.32,.15),('USB_GRAY_EDGE',normal*.05-v*.13,.288,.10)]:
 light=bpy.data.lights.new(name,'AREA');light.energy=power;light.shape='DISK';light.size=size;o=bpy.data.objects.new(name,light);studio.objects.link(o);o.location=target+offset;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('USB_V2_SHAPE_CAMERA',bpy.data.cameras.new('USB_V2_SHAPE_CAMERA'));studio.objects.link(cam);cam.data.lens=70;cam.data.clip_start=.001;cam.data.clip_end=10;scene.camera=cam;cam.location=target+normal*.15+u*.035+v*.020;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.engine='CYCLES';scene.cycles.samples=96;scene.cycles.use_denoising=True;scene.cycles.denoiser='OPENIMAGEDENOISE';scene.cycles.denoising_use_gpu=False;scene.render.resolution_x=1000;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
path=HERE/'instruments-usb-v2-study-r2.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);assert hashlib.sha256(base.read_bytes()).hexdigest()==base_sha
report={'schema':1,'scope':'G3 gray shape study only, not integrated/final instrumentv2 or physical part count','source_path':str(path.relative_to(ROOT)),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'export_path':str(glb.relative_to(ROOT)),'export_sha256':hashlib.sha256(glb.read_bytes()).hexdigest(),'historical_instruments_source_unchanged_sha256':base_sha,'plan_path':str(planpath.relative_to(ROOT)),'plan_sha256':hashlib.sha256(planpath.read_bytes()).hexdigest(),'bodies':rows,'surround_insert_BVH_crossings':crossings,'lip_top_z_m_estimated':.0368,'insert_face_top_z_m_estimated':.0354,'recess_m_estimated':.0014,'insert_bottom_to_pocket_floor_m_estimated':.00015,'all_dimensions_and_depths_estimated':True,'camera_recovered':False,'exact_OEM_part_count_known':False,'whole_cluster_interface_not_yet_tested':True,'art_accepted':False};(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');print('USB_STUDY_SOURCE',report['source_sha256'],report['export_sha256'])
