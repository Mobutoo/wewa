"""Staged bodywork child production; no inferred user reception or OEM dimensions."""
import bpy,sys,json,hashlib,math,struct
from pathlib import Path
from collections import Counter,defaultdict
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from body_completion_geometry_v1 import plate,loft,ring
key,stage=sys.argv[sys.argv.index('--')+1:];H=R/'assets-src/moto-components'/key;P=json.loads((H/'parameters-v1.json').read_text());rev=P['revision'];O=R/'creative/reviews'/rev;O.mkdir(exist_ok=True,parents=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=H/(rev+'.blend');gray=H/(rev+'-gray.blend')
def write(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
for p in[Path(__file__),R/'tools/body_completion_geometry_v1.py']:
 d=O/'protocols';d.mkdir(exist_ok=True);(d/(sha(p)+'-'+p.name)).write_bytes(p.read_bytes())
def digest(m):
 m.calc_loop_triangles();return hashlib.sha256(repr(([(tuple(v.co))for v in m.vertices],[tuple(t.vertices)for t in m.loop_triangles],[(tuple(u.uv))for u in m.uv_layers.active.data])).encode()).hexdigest()
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def save_export(path):
 ob=bpy.data.objects['EXTERIOR_CHILD'];bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True,export_tangents=False,export_animations=False)
def settings():
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.cycles.max_bounces=6;s.render.threads_mode='FIXED';s.render.threads=2;s.view_layers[0].cycles.denoising_store_passes=True;s.render.resolution_x=900;s.render.resolution_y=700;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0;s.view_settings.gamma=1;s.unit_settings.system='METRIC';bpy.context.preferences.filepaths.save_version=0
if stage=='geometry':
 assert (R/P['research']).exists();bpy.ops.wm.read_factory_settings(use_empty=True);settings();V,F,meta={'plate':plate,'loft':loft,'ring':ring}[P['builder']](P['shape']);m=bpy.data.meshes.new(P['component_id']);m.from_pydata(V,[],F);m.update();assert not m.validate();m.calc_loop_triangles();assert min(t.area for t in m.loop_triangles)>1e-14
 coll=bpy.data.collections.new(P['collection']);bpy.context.scene.collection.children.link(coll);ob=bpy.data.objects.new('EXTERIOR_CHILD',m);coll.objects.link(ob);uv=m.uv_layers.new(name='Original source chart')
 low=Vector(tuple(min(v[i]for v in V)for i in range(3)));high=Vector(tuple(max(v[i]for v in V)for i in range(3)));size=max(high-low);center=(low+high)/2
 for f in m.polygons:
  f.use_smooth=P['builder']!='plate'
  for li in f.loop_indices:
   v=m.vertices[m.loops[li].vertex_index].co;uv.data[li].uv=((v.x-center.x)/size+.5,(v.y-center.y)/size+.5)
 edges=Counter(tuple(sorted((a,b)))for f in F for a,b in zip(f,f[1:]+f[:1]));assert all(n<=2 for n in edges.values());boundary=[e for e,n in edges.items()if n==1];g=defaultdict(set)
 for a,b in boundary:g[a].add(b);g[b].add(a)
 assert all(len(v)==2 for v in g.values());unseen=set(g);loops=0
 while unseen:
  loops+=1;todo=[unseen.pop()]
  while todo:
   for j in g[todo.pop()]:
    if j in unseen:unseen.remove(j);todo.append(j)
 assert loops==meta['expected_boundary_loops'],(loops,meta)
 mat=bpy.data.materials.new('Original neutral gray');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.18,.18,.18,1);bs.inputs['Roughness'].default_value=.32;m.materials.append(mat)
 ob['scope']=P['scope'];ob['dimensions_status']='Authored bounded estimates, not OEM measurements';ob['art_accepted']=False
 s=bpy.context.scene;world=bpy.data.worlds.new('Original neutral studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.12,.12,1);world.node_tree.nodes['Background'].inputs[1].default_value=.4;s.world=world
 for name,offset,power,k in [('Key',(-.8,-1,1.5),200,1.1),('Fill',(1,.3,.8),90,.9),('Rim',(-.6,1,-.5),130,.7)]:
  l=bpy.data.lights.new(name,'AREA');l.energy=power*size*size;l.shape='RECTANGLE';l.size=k*size;l.size_y=k*size*.6;o=bpy.data.objects.new(name,l);s.collection.objects.link(o);o.location=center+Vector(offset)*size;aim(o,center)
 cam=bpy.data.objects.new('Original isolated camera',bpy.data.cameras.new('Original isolated camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=size*1.65;cam.data.clip_start=.0001;cam.data.clip_end=100
 bpy.ops.wm.save_as_mainfile(filepath=str(gray),compress=True);save_export(H/(rev+'-gray.glb'));write('geometry-check.json',dict(component_id=P['component_id'],triangles=len(m.loop_triangles),vertices=len(m.vertices),boundary_loops=loops,boundary_edges=len(boundary),bounds={'min':list(low),'max':list(high)},minimum_triangle_area=min(t.area for t in m.loop_triangles),geometry_digest=digest(m),source_sha256=sha(gray),export_sha256=sha(H/(rev+'-gray.glb')),protocol_sha256=sha(Path(__file__)),shape_protocol_sha256=sha(R/'tools/body_completion_geometry_v1.py'),metadata=meta,art_accepted=False))
else:
 bpy.ops.wm.open_mainfile(filepath=str(source if stage in('preview','final')else gray));settings();ob=bpy.data.objects['EXTERIOR_CHILD'];m=ob.data;before=digest(m);s=bpy.context.scene;bb=[ob.matrix_world@Vector(v)for v in ob.bound_box];low=Vector(tuple(min(v[i]for v in bb)for i in range(3)));high=Vector(tuple(max(v[i]for v in bb)for i in range(3)));size=max(high-low);center=(low+high)/2
 if stage=='material':
  assert json.loads((O/'gray-review.json').read_text())['actually_read'];bs=m.materials[0].node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=P['material']['linear_color'];bs.inputs['Roughness'].default_value=P['material']['roughness'];bs.inputs['Metallic'].default_value=P['material'].get('metallic',0)
  if 'transmission' in P['material']:bs.inputs['Transmission Weight'].default_value=P['material']['transmission'];bs.inputs['IOR'].default_value=1.49
  assert digest(m)==before;bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True);save_export(H/(rev+'.glb'));write('source-geometry-check.json',dict(source_sha256=sha(source),export_sha256=sha(H/(rev+'.glb')),gray_material_source_geometry_uv_equal=True,geometry_digest=before,triangles=len(m.loop_triangles),scope='Source P/I/UV identical, not material calibration or installed fit'))
 elif stage in('gray','preview','final'):
  if stage=='final':assert json.loads((O/'preview-review.json').read_text())['actually_read']
  views=[]
  def view(name,eye,neutral=False):
   s.camera.location=center+Vector(eye)*size;aim(s.camera,center);s.cycles.samples=96 if stage=='final'else 16
   if neutral:
    for l in bpy.data.lights:l.energy=0
    w=bpy.data.worlds.new('Neutral sky comparison');w.use_nodes=True;nt=w.node_tree;tex=nt.nodes.new('ShaderNodeTexEnvironment');tex.image=bpy.data.images.load(str(R/'app/public/materials/kloppenheim_06_puresky_1k.hdr'));nt.links.new(tex.outputs['Color'],nt.nodes['Background'].inputs['Color']);nt.nodes['Background'].inputs['Strength'].default_value=.65;s.world=w
   raw=O/'raw';raw.mkdir(exist_ok=True);s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(raw/(name+'.exr'));bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/(name+'.png')),scene=s);views.append(dict(name=name,PNG_sha256=sha(O/(name+'.png')),actually_saved=True,samples=s.cycles.samples,camera_eye=list(s.camera.location),camera_target=list(center)))
  if stage=='gray':
   view('gray-front',(0,0,3));view('gray-quarter',(1,-1.2,2.0));view('gray-reverse',(-1,1,-1.8))
  elif stage=='preview':view('preview-studio',(1,-1.2,2));view('preview-neutral',(1,-1.2,2),True)
  else:view('whole-front',(0,0,3));view('whole-quarter',(1,-1.2,2));view('neutral-outdoor',(1,-1.2,2),True)
  write('render-report.json'if stage=='final'else stage+'-render-report.json',dict(revision=rev,source_sha256=sha(source if stage!='gray'else gray),export_sha256=sha(H/(rev+'.glb'))if stage!='gray'else sha(H/(rev+'-gray.glb')),views=views,source_geometry_unchanged=digest(m)==before,protocol_sha256=sha(Path(__file__)),shape_protocol_sha256=sha(R/'tools/body_completion_geometry_v1.py'),exposure=0,gamma=1,calibrated=False,scope='Original isolated native views; no artistic, optical, OEM dimension or mobile/fit reception'))
 else:raise ValueError(stage)
