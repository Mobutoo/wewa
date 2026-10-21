"""P01 bounded original exterior study; no vendor texture or hidden mounting geometry."""
import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];H=ROOT/'assets-src/moto-components/side-cover-left';O=ROOT/'creative/reviews/side-cover-left-study-v1';O.mkdir(exist_ok=True,parents=True)
P=json.loads((H/'parameters-study-v1.json').read_text());stage=sys.argv[sys.argv.index('--')+1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def digest(ob):
 m=ob.data;m.calc_loop_triangles();return hashlib.sha256(repr(([(tuple(v.co))for v in m.vertices],[tuple(t.vertices)for t in m.loop_triangles],[(tuple(u.uv))for u in m.uv_layers.active.data])).encode()).hexdigest()
def look(ob,t):ob.rotation_euler=(Vector(t)-ob.location).to_track_quat('-Z','Y').to_euler()
def export(n):
 bpy.ops.object.select_all(action='DESELECT');ob=bpy.data.objects['LEFT_COVER_OUTER_SKIN'];ob.select_set(True);bpy.context.view_layer.objects.active=ob
 bpy.ops.export_scene.gltf(filepath=str(H/n),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_tangents=False)
def render(name,eye,gray=False,reflection=False):
 s=bpy.context.scene;s.camera.location=eye;look(s.camera,(0,0,.007));s.camera.data.type='ORTHO';s.camera.data.ortho_scale=.37
 s.cycles.samples=16 if gray else (12 if stage=='preview' else 96)
 s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(O/'raw'/(name+'.exr'));(O/'raw').mkdir(exist_ok=True)
 bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/(name+'.png')),scene=s)
 return dict(view=name,png=name+'.png',exr='raw/'+name+'.exr',samples=s.cycles.samples,camera=list(eye),sha256=sha(O/(name+'.png')))
if stage=='geometry':
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
 pts=[Vector(((x-568)*P['meters_per_pixel'],(359-y)*P['meters_per_pixel'])) for x,y in P['profile_pixels']];N=len(pts);curve=[]
 for i in range(N):
  a,b,c,d=[pts[k%N] for k in (i-1,i,i+1,i+2)]
  for j in range(P['contour_samples_per_span']):
   t=j/P['contour_samples_per_span'];curve.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
 # Clockwise source screen points become clockwise XY: reverse for outward +Z.
 area=sum(a.x*b.y-b.x*a.y for a,b in zip(curve,curve[1:]+curve[:1]));
 if area<0:curve.reverse()
 n=len(curve);R=P['radial_rings'];V=[(0,0,P['bulge_m'])];F=[]
 for k in range(1,R+1):
  r=k/R
  for p in curve:V.append((r*p.x,r*p.y,P['bulge_m']*(1-r*r)))
 for j in range(n):F.append((0,1+j,1+(j+1)%n))
 for k in range(R-1):
  a=1+k*n;b=a+n
  for j in range(n):q=(j+1)%n;F.append((a+j,b+j,b+q,a+q))
 # Rounded short visible return, terminating at open review boundary (not a rear pan).
 prev=1+(R-1)*n
 for k in range(1,9):
  t=k/8;start=len(V)
  for p in curve:V.append((p.x*(1-.008*(1-math.cos(t*math.pi/2))),p.y*(1-.008*(1-math.cos(t*math.pi/2))),-P['return_depth_m']*math.sin(t*math.pi/2)))
  for j in range(n):q=(j+1)%n;F.append((prev+j,start+j,start+q,prev+q))
  prev=start
 m=bpy.data.meshes.new('Original photo-inferred radial surface with open return');m.from_pydata(V,[],F);m.update();assert not m.validate();m.calc_loop_triangles()
 ob=bpy.data.objects.new('LEFT_COVER_OUTER_SKIN',m);coll=bpy.data.collections.new('WEWA_SIDE_COVER_LEFT_STUDY');bpy.context.scene.collection.children.link(coll);coll.objects.link(ob)
 uv=m.uv_layers.new(name='Original planar study UV')
 for f in m.polygons:
  f.use_smooth=True
  for li in f.loop_indices:
   v=m.vertices[m.loops[li].vertex_index].co;uv.data[li].uv=(v.x/.30+.5,v.y/.18+.5)
 counts=Counter(tuple(sorted((a,b))) for f in F for a,b in zip(f,f[1:]+f[:1]));assert max(counts.values())==2;assert sum(v==1 for v in counts.values())==n
 assert min(t.area for t in m.loop_triangles)>1e-13
 mat=bpy.data.materials.new('Gray form review');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.18,.18,.18,1);bs.inputs['Roughness'].default_value=.3;m.materials.append(mat)
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=2;s.cycles.max_bounces=5;s.view_layers[0].cycles.denoising_store_passes=True
 s.render.resolution_x=900;s.render.resolution_y=700;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.unit_settings.system='METRIC'
 w=bpy.data.worlds.new('Original studio world');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.12,.12,.12,1);w.node_tree.nodes['Background'].inputs[1].default_value=.4;s.world=w
 for name,loc,power,size in [('Key',(-.22,.3,.4),22,.30),('Fill',(.28,-.1,.3),8,.24),('Rim',(.1,.3,-.05),12,.2)]:
  l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=size;o=bpy.data.objects.new(name,l);s.collection.objects.link(o);o.location=loc;look(o,(0,0,0))
 cam=bpy.data.objects.new('Study camera',bpy.data.cameras.new('Study camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.clip_start=.001;cam.data.clip_end=20
 ob['scope']='Bounded exterior skin only; return is estimated; no mounting pins or thickness claimed';ob['art_accepted']=False
 bpy.ops.wm.save_as_mainfile(filepath=str(H/'side-cover-left-study-v1.blend'),compress=True);export('side-cover-left-study-v1.glb')
 write('geometry-check.json',dict(component_id=P['component_id'],vertices=len(V),triangles=len(m.loop_triangles),open_boundary_edges=n,expected_boundary='One deliberately open rear return loop',nonmanifold_branch_edges=sum(x>2 for x in counts.values()),min_triangle_area=min(t.area for t in m.loop_triangles),dimensions_m=list(ob.dimensions),geometry_digest=digest(ob),source_sha256=sha(H/'side-cover-left-study-v1.blend'),export_sha256=sha(H/'side-cover-left-study-v1.glb'),protocol_sha256=sha(Path(__file__)),art_accepted=False))
elif stage in ('gray','material','preview','final'):
 bpy.ops.wm.open_mainfile(filepath=str(H/('side-cover-left-candidate-v1.blend' if stage in ('preview','final') else 'side-cover-left-study-v1.blend')));ob=bpy.data.objects['LEFT_COVER_OUTER_SKIN'];before=digest(ob)
 if stage=='material':
  assert json.loads((O/'gray-review.json').read_text())['read_for_exterior_study']
  m=ob.data;m.materials.clear()
  mat=bpy.data.materials.new('Original smooth red-black study paint');mat.use_nodes=True;nodes=mat.node_tree.nodes;bs=nodes['Principled BSDF'];bs.inputs['Roughness'].default_value=.35
  tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(H/'textures/original-red-black-study-v1.png'));tex.image.colorspace_settings.name='sRGB';tex.interpolation='Linear';tex.image.pack();mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);m.materials.append(mat)
  for f in m.polygons:f.material_index=0
  assert digest(ob)==before
  bpy.ops.wm.save_as_mainfile(filepath=str(H/'side-cover-left-candidate-v1.blend'),compress=True);export('side-cover-left-candidate-v1.glb');write('material-transfer-check.json',dict(gray_geometry_digest=before,material_geometry_digest=digest(ob),identical=True,scope='No geometry or UV changes; original plain colors, no vendor pixels'))
 else:
  if stage=='final':assert json.loads((O/'preview-review.json').read_text())['read_for_exterior_study']
  views=[]
  if stage=='gray':
   for n,e in [('gray-profile',(0,0,.5)),('gray-quarter',(.24,.12,.46)),('gray-edge',(-.34,-.13,.20))]:views.append(render(n,e,True))
  elif stage=='preview':
   views.append(render('preview-studio',(.24,.12,.46)))
   s=bpy.context.scene
   for l in bpy.data.lights:l.energy=0
   w=bpy.data.worlds.new('Neutral outdoor HDRI');w.use_nodes=True;nt=w.node_tree;tex=nt.nodes.new('ShaderNodeTexEnvironment');hdr=ROOT/'app/public/materials/kloppenheim_06_puresky_1k.hdr';tex.image=bpy.data.images.load(str(hdr));nt.links.new(tex.outputs['Color'],nt.nodes['Background'].inputs['Color']);nt.nodes['Background'].inputs['Strength'].default_value=.65
   s.world=w;views.append(render('preview-neutral',(.24,.12,.46)))
  else:
   views.append(render('whole-profile',(0,0,.5)));views.append(render('whole-quarter',(.24,.12,.46)))
   s=bpy.context.scene
   for l in bpy.data.lights:l.energy=0
   w=bpy.data.worlds.new('Neutral outdoor HDRI');w.use_nodes=True;nt=w.node_tree;tex=nt.nodes.new('ShaderNodeTexEnvironment');hdr=ROOT/'app/public/materials/kloppenheim_06_puresky_1k.hdr';tex.image=bpy.data.images.load(str(hdr));nt.links.new(tex.outputs['Color'],nt.nodes['Background'].inputs['Color']);nt.nodes['Background'].inputs['Strength'].default_value=.65;s.world=w;views.append(render('neutral-outdoor',(.24,.12,.46)))
  write(stage+'-render-report.json',dict(views=views,geometry_unchanged=digest(ob)==before,protocol_sha256=sha(Path(__file__)),exposure=0,gamma=1,view_transform='AgX Medium High Contrast',neutral_strength=.65,calibrated=False,scope='Original bounded exterior study; not installed-fit or artistic reception'))
else:raise ValueError(stage)
