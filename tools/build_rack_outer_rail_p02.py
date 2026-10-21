"""P02 bounded original outer U rail; no vendor pixels or hidden attachments."""
import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];H=ROOT/'assets-src/moto-components/rack-outer-rail';O=ROOT/'creative/reviews/rack-outer-rail-study-v1';O.mkdir(exist_ok=True,parents=True)
P=json.loads((H/'parameters-study-v3.json').read_text());stage=sys.argv[sys.argv.index('--')+1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def digest(ob):
 m=ob.data;m.calc_loop_triangles();return hashlib.sha256(repr(([(tuple(v.co))for v in m.vertices],[tuple(t.vertices)for t in m.loop_triangles],[(tuple(u.uv))for u in m.uv_layers.active.data])).encode()).hexdigest()
def look(ob,t):ob.rotation_euler=(Vector(t)-ob.location).to_track_quat('-Z','Y').to_euler()
def export(n):
 bpy.ops.object.select_all(action='DESELECT');ob=bpy.data.objects['RACK_OUTER_RAIL'];ob.select_set(True);bpy.context.view_layer.objects.active=ob
 bpy.ops.export_scene.gltf(filepath=str(H/n),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_tangents=False)
def render(name,eye,gray=False,reflection=False):
 s=bpy.context.scene;s.camera.location=eye;look(s.camera,(0,0,.007));s.camera.data.type='ORTHO';s.camera.data.ortho_scale=.75
 s.cycles.samples=16 if gray else (12 if stage=='preview' else 96)
 s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(O/'raw'/(name+'.exr'));(O/'raw').mkdir(exist_ok=True)
 bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/(name+'.png')),scene=s)
 return dict(view=name,png=name+'.png',exr='raw/'+name+'.exr',samples=s.cycles.samples,camera=list(eye),sha256=sha(O/(name+'.png')))
if stage=='geometry':
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
 raw=[Vector(v) for v in P['centerline_m']];pts=[raw[0],raw[0]]+raw+[raw[-1],raw[-1]];dense=[]
 for i in range(1,len(pts)-2):
  a,b,c,d=[pts[max(0,min(len(pts)-1,k))] for k in (i-1,i,i+1,i+2)]
  for j in range(P['samples_per_span']):
   t=j/P['samples_per_span'];dense.append(((1-t)**3*a+(3*t**3-6*t*t+4)*b+(-3*t**3+3*t*t+3*t+1)*c+t**3*d)/6)
 dense.append(pts[-1]);dense=[p for i,p in enumerate(dense) if i==0 or (p-dense[i-1]).length>1e-8]
 from bisect import bisect_right
 length=[0.]
 for a,b in zip(dense,dense[1:]):length.append(length[-1]+(b-a).length)
 count=math.ceil(length[-1]/P['arc_length_resample_step_m']);sampled=[]
 for j in range(count+1):
  distance=length[-1]*j/count;k=min(len(dense)-2,max(0,bisect_right(length,distance)-1));sampled.append(dense[k].lerp(dense[k+1],(distance-length[k])/(length[k+1]-length[k])))
 dense=sampled;n=P['radial_samples'];V=[];F=[];last=None;shift=Vector(P['center_shift_m'])
 for i,p in enumerate(dense):
  tangent=(dense[min(i+1,len(dense)-1)]-dense[max(0,i-1)]).normalized()
  if last is None:normal=tangent.cross(Vector((0,0,1))).normalized()
  else:normal=(last-tangent*last.dot(tangent)).normalized()
  binormal=tangent.cross(normal).normalized();last=normal
  for j in range(n):
   theta=2*math.pi*j/n;V.append(tuple(p-shift+P['tube_radius_m']*(normal*math.cos(theta)+binormal*math.sin(theta))))
 for i in range(len(dense)-1):
  for j in range(n):q=(j+1)%n;a=i*n;b=a+n;F.append((a+j,a+q,b+q,b+j))
 m=bpy.data.meshes.new('Original bounded swept external rail');m.from_pydata(V,[],F);m.update();assert not m.validate();m.calc_loop_triangles()
 ob=bpy.data.objects.new('RACK_OUTER_RAIL',m);coll=bpy.data.collections.new('WEWA_RACK_OUTER_RAIL_STUDY');bpy.context.scene.collection.children.link(coll);coll.objects.link(ob)
 uv=m.uv_layers.new(name='Original swept-rail study UV')
 for f in m.polygons:
  f.use_smooth=True
  for li in f.loop_indices:
   idx=m.loops[li].vertex_index;u=idx%n/n
   if idx%n==0 and any(v%n==n-1 for v in f.vertices):u=1.0
   uv.data[li].uv=(u,(idx//n)/(len(dense)-1))
 counts=Counter(tuple(sorted((a,b))) for f in F for a,b in zip(f,f[1:]+f[:1]));assert max(counts.values())==2;assert sum(v==1 for v in counts.values())==2*n
 assert min(t.area for t in m.loop_triangles)>1e-13
 mat=bpy.data.materials.new('Gray form review');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.18,.18,.18,1);bs.inputs['Roughness'].default_value=.3;m.materials.append(mat)
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=2;s.cycles.max_bounces=5;s.view_layers[0].cycles.denoising_store_passes=True
 s.render.resolution_x=900;s.render.resolution_y=700;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.unit_settings.system='METRIC'
 w=bpy.data.worlds.new('Original studio world');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.12,.12,.12,1);w.node_tree.nodes['Background'].inputs[1].default_value=.4;s.world=w
 for name,loc,power,size in [('Key',(-.40,.4,.7),45,.55),('Fill',(.45,-.3,.55),26,.4),('Rim',(.1,.45,-.15),24,.35)]:
  l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=size;o=bpy.data.objects.new(name,l);s.collection.objects.link(o);o.location=loc;look(o,(0,0,0))
 cam=bpy.data.objects.new('Study camera',bpy.data.cameras.new('Study camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.clip_start=.001;cam.data.clip_end=20
 ob['scope']='Bounded U rail only; tube exterior is estimated; no wall thickness, brackets or flattened ends claimed';ob['art_accepted']=False
 bpy.ops.wm.save_as_mainfile(filepath=str(H/'rack-outer-rail-study-v1.blend'),compress=True);export('rack-outer-rail-study-v1.glb')
 write('geometry-check.json',dict(component_id=P['component_id'],vertices=len(V),triangles=len(m.loop_triangles),open_boundary_edges=2*n,expected_boundary='Two deliberately open review cuts before unmade flattened ends',nonmanifold_branch_edges=sum(x>2 for x in counts.values()),min_triangle_area=min(t.area for t in m.loop_triangles),dimensions_m=list(ob.dimensions),geometry_digest=digest(ob),source_sha256=sha(H/'rack-outer-rail-study-v1.blend'),export_sha256=sha(H/'rack-outer-rail-study-v1.glb'),protocol_sha256=sha(Path(__file__)),art_accepted=False))
elif stage in ('gray','material','preview','final'):
 bpy.ops.wm.open_mainfile(filepath=str(H/('rack-outer-rail-candidate-v1.blend' if stage in ('preview','final') else 'rack-outer-rail-study-v1.blend')));ob=bpy.data.objects['RACK_OUTER_RAIL'];before=digest(ob)
 if stage=='material':
  assert json.loads((O/'gray-review.json').read_text())['read_for_exterior_study']
  m=ob.data;m.materials.clear();mat=bpy.data.materials.new('Original clean black coat - substrate unknown');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.009,.010,.012,1);bs.inputs['Roughness'].default_value=.42;m.materials.append(mat)
  for f in m.polygons:f.material_index=0
  assert digest(ob)==before
  bpy.ops.wm.save_as_mainfile(filepath=str(H/'rack-outer-rail-candidate-v1.blend'),compress=True);export('rack-outer-rail-candidate-v1.glb');write('material-transfer-check.json',dict(gray_geometry_digest=before,material_geometry_digest=digest(ob),identical=True,scope='No geometry or UV changes; original plain black coat, no vendor pixels'))
 else:
  if stage=='final':assert json.loads((O/'preview-review.json').read_text())['read_for_exterior_study']
  views=[]
  if stage=='gray':
   for n,e in [('gray-profile',(0,0,.95)),('gray-quarter',(.65,-.72,.52)),('gray-edge',(-.75,.42,.32))]:views.append(render(n,e,True))
  elif stage=='preview':
   views.append(render('preview-studio',(.65,-.72,.52)))
   s=bpy.context.scene
   for l in bpy.data.lights:l.energy=0
   w=bpy.data.worlds.new('Neutral outdoor HDRI');w.use_nodes=True;nt=w.node_tree;tex=nt.nodes.new('ShaderNodeTexEnvironment');hdr=ROOT/'app/public/materials/kloppenheim_06_puresky_1k.hdr';tex.image=bpy.data.images.load(str(hdr));nt.links.new(tex.outputs['Color'],nt.nodes['Background'].inputs['Color']);nt.nodes['Background'].inputs['Strength'].default_value=.65
   s.world=w;views.append(render('preview-neutral',(.65,-.72,.52)))
  else:
   views.append(render('whole-profile',(0,0,.95)));views.append(render('whole-quarter',(.65,-.72,.52)))
   s=bpy.context.scene
   for l in bpy.data.lights:l.energy=0
   w=bpy.data.worlds.new('Neutral outdoor HDRI');w.use_nodes=True;nt=w.node_tree;tex=nt.nodes.new('ShaderNodeTexEnvironment');hdr=ROOT/'app/public/materials/kloppenheim_06_puresky_1k.hdr';tex.image=bpy.data.images.load(str(hdr));nt.links.new(tex.outputs['Color'],nt.nodes['Background'].inputs['Color']);nt.nodes['Background'].inputs['Strength'].default_value=.65;s.world=w;views.append(render('neutral-outdoor',(.65,-.72,.52)))
  write(stage+'-render-report.json',dict(views=views,geometry_unchanged=digest(ob)==before,protocol_sha256=sha(Path(__file__)),exposure=0,gamma=1,view_transform='AgX Medium High Contrast',neutral_strength=.65,calibrated=False,scope='Original bounded exterior study; not installed-fit or artistic reception'))
else:raise ValueError(stage)
