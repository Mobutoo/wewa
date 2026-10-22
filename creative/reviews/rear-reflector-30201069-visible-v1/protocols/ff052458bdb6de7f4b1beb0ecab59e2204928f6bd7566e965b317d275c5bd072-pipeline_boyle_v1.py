"""Boyle single30201069 staged protocol. Based on read-only pipelinev17; no frozen edits."""
import bpy,sys,json,hashlib,math
from pathlib import Path
from collections import Counter
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(H));from geometry_boyle_v1 import make
P=json.loads((H/'parameters-v1.json').read_text());rev=P['revision'];O=R/'creative/reviews'/rev;stage=sys.argv[sys.argv.index('--')+1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,o):(O/n).write_text(json.dumps(o,indent=2)+'\n')
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def digest(m):
 m.calc_loop_triangles();return hashlib.sha256(repr(([(tuple(v.co))for v in m.vertices],[tuple(t.vertices)for t in m.loop_triangles],[tuple(v.uv)for v in m.uv_layers.active.data])).encode()).hexdigest()
def setup():
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.cycles.max_bounces=6;s.render.threads_mode='FIXED';s.render.threads=2;s.view_layers[0].cycles.denoising_store_passes=True;s.render.resolution_x=900;s.render.resolution_y=700;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0;s.view_settings.gamma=1;s.unit_settings.system='METRIC';bpy.context.preferences.filepaths.save_version=0
 return s
def export(suffix):
 ob=bpy.data.objects['EXTERIOR_CHILD'];bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 bpy.ops.export_scene.gltf(filepath=str(H/(rev+suffix+'.glb')),export_format='GLB',use_selection=True,export_apply=True,export_tangents=False,export_animations=False)
 m=ob.data;m.calc_loop_triangles();native=[]
 for t in m.loop_triangles:
  corners=[]
  for li in t.loops:
   v=m.vertices[m.loops[li].vertex_index].co;n=m.corner_normals[li].vector;u=m.uv_layers.active.data[li].uv
   corners.append([v.x,v.z,-v.y,n.x,n.z,-n.y,u.x,1-u.y])
  native.append(corners)
 write('native-corners'+suffix+'.json',dict(triangles=native,world_matrix=[list(r)for r in ob.matrix_world],axis_map='x,z,-y andUVvflip',component_id=P['component_id']))
if stage=='geometry':
 bpy.ops.wm.read_factory_settings(use_empty=True);s=setup();V,F,M=make(P['shape']);m=bpy.data.meshes.new(P['component_id']);m.from_pydata(V,[],F);m.update();assert not m.validate();m.calc_loop_triangles();assert min(t.area for t in m.loop_triangles)>1e-14
 coll=bpy.data.collections.new(P['collection']);s.collection.children.link(coll);ob=bpy.data.objects.new('EXTERIOR_CHILD',m);coll.objects.link(ob);uv=m.uv_layers.new(name='Original planar chart')
 for f,matid in zip(m.polygons,M):
  f.material_index=matid;f.use_smooth=matid==1
  for li in f.loop_indices:
   v=m.vertices[m.loops[li].vertex_index].co;uv.data[li].uv=(v.x/.080+.5,v.y/.050+.5)
 for name in ['Original gray visible face','Original gray visible frame']:
  mat=bpy.data.materials.new(name);mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.18,.18,.18,1);bs.inputs['Roughness'].default_value=.32;mat.use_backface_culling=True;m.materials.append(mat)
 edges=Counter(tuple(sorted((a,b)))for f in F for a,b in zip(f,f[1:]+f[:1]));assert max(edges.values())==2;boundary=[e for e,n in edges.items()if n==1];assert len(boundary)==100
 ob['component_id']=P['component_id'];ob['scope']=P['scope'];ob['art_accepted']=False;ob['rear_cut']='OPEN at localZ0; unknown back omitted, not actual thin shell'
 world=bpy.data.worlds.new('Original studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.12,.12,1);world.node_tree.nodes['Background'].inputs[1].default_value=.4;s.world=world
 size=.080;center=Vector((0,0,.003))
 for name,offset,power,k in [('Key',(-.8,-1,1.5),200,1.1),('Fill',(1,.3,.8),90,.9),('Rim',(-.6,1,-.5),130,.7)]:
  l=bpy.data.lights.new(name,'AREA');l.energy=power*size*size;l.shape='RECTANGLE';l.size=k*size;l.size_y=k*size*.6;o=bpy.data.objects.new(name,l);s.collection.objects.link(o);o.location=center+Vector(offset)*size;aim(o,center)
 cam=bpy.data.objects.new('Boyle isolated camera',bpy.data.cameras.new('Boyle isolated camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.123;cam.data.clip_start=.0001;cam.data.clip_end=10
 bpy.ops.wm.save_as_mainfile(filepath=str(H/(rev+'-gray.blend')),compress=True);export('-gray');write('geometry-check.json',dict(component_id=P['component_id'],vertices=len(V),triangles=len(m.loop_triangles),boundary_loops=1,boundary_edges=len(boundary),minimum_triangle_area_m2=min(t.area for t in m.loop_triangles),bounds_m=dict(min=[min(v[i]for v in V)for i in range(3)],max=[max(v[i]for v in V)for i in range(3)]),geometry_digest=digest(m),open_cut='Z0rear, deliberate observation cut no back',art_accepted=False))
else:
 gray=stage in ['gray','graycut','material'];bpy.ops.wm.open_mainfile(filepath=str(H/(rev+('-gray'if gray else '')+'.blend')),use_scripts=False);s=setup();ob=bpy.data.objects['EXTERIOR_CHILD'];m=ob.data;before=digest(m)
 if stage=='material':
  assert json.loads((O/'gray-review.json').read_text())['actually_read']
  face,frame=m.materials;face.name='Original ruby apparent-cell interpretation';frame.name='Original charcoal visible surround'
  bs=face.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.23,.0018,.003,1);bs.inputs['Roughness'].default_value=.22;bs.inputs['Metallic'].default_value=.22;bs.inputs['Coat Weight'].default_value=.45;bs.inputs['Coat Roughness'].default_value=.17
  # Authored regular apparent checker/cell NORMALS, not sourcepixels or internal optical prisms.
  N=512;pix=[]
  for y in range(N):
   for x in range(N):
    u=(x+.5)/N*40;v=(y+.5)/N*25;fu=u%1;fv=v%1;cell=(int(u)+int(v))%2;nx=.23*(1 if fu<.5 else -1);ny=.23*(1 if fv<.5 else -1)
    if cell:nx,ny=-ny,nx
    if min(fu,1-fu,fv,1-fv)<.06:nx*=.3;ny*=.3
    nz=math.sqrt(1-nx*nx-ny*ny);pix.extend((nx*.5+.5,ny*.5+.5,nz*.5+.5,1))
  im=bpy.data.images.new('Original apparent cell normals512',width=N,height=N,alpha=True);im.colorspace_settings.name='Non-Color';im.pixels=pix;im.filepath_raw=str(H/'original-apparent-cell-normal.png');im.file_format='PNG';im.save();im.pack();nt=face.node_tree;tex=nt.nodes.new('ShaderNodeTexImage');tex.image=im;normal=nt.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.55;nt.links.new(tex.outputs['Color'],normal.inputs['Color']);nt.links.new(normal.outputs['Normal'],bs.inputs['Normal'])
  fb=frame.node_tree.nodes['Principled BSDF'];fb.inputs['Base Color'].default_value=(.009,.0095,.012,1);fb.inputs['Roughness'].default_value=.3
  assert digest(m)==before;bpy.ops.wm.save_as_mainfile(filepath=str(H/(rev+'.blend')),compress=True);export('');write('source-geometry-check.json',dict(source_sha256=sha(H/(rev+'.blend')),export_sha256=sha(H/(rev+'.glb')),geometry_uv_equal_to_gray=True,geometry_digest=before,material_scope='Original apparent cells normals only, no internal prisms or retroreflection claim',sourcepixels_used=False))
 elif stage in ['gray','graycut','preview','final']:
  if stage=='final':assert json.loads((O/'preview-review.json').read_text())['actually_read']
  views=[]
  def view(name,neutral=False):
   eye=P['view_eyes'][name];s.camera.location=Vector((0,0,.003))+Vector(eye)*.08;aim(s.camera,(0,0,.003));s.cycles.samples=96 if stage=='final'else 16
   if neutral:
    for l in bpy.data.lights:l.energy=0
    world=bpy.data.worlds.new('Neutral HDR comparison');world.use_nodes=True;nt=world.node_tree;tex=nt.nodes.new('ShaderNodeTexEnvironment');tex.image=bpy.data.images.load(str(R/'app/public/materials/kloppenheim_06_puresky_1k.hdr'));nt.links.new(tex.outputs['Color'],nt.nodes['Background'].inputs['Color']);nt.nodes['Background'].inputs['Strength'].default_value=.65;s.world=world
   sys.path.insert(0,str(R/'tools'))
   # Whole-piece framing is checked by own projection below; shared function API not invoked.
   from bpy_extras.object_utils import world_to_camera_view
   bpy.context.view_layer.update()
   pts=[world_to_camera_view(s,s.camera,ob.matrix_world@Vector(v))for v in ob.bound_box];fr=dict(min=[min(v[i]for v in pts)for i in range(3)],max=[max(v[i]for v in pts)for i in range(3)]);assert fr['min'][0]>.02 and fr['min'][1]>.02 and fr['max'][0]<.98 and fr['max'][1]<.98 and fr['min'][2]>s.camera.data.clip_start
   if name=='gray-reverse':
    for mat in m.materials:
     nt=mat.node_tree;out=nt.nodes.get('Material Output');bs=nt.nodes.get('Principled BSDF');geo=nt.nodes.new('ShaderNodeNewGeometry');trans=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(geo.outputs['Backfacing'],mix.inputs[0]);nt.links.new(bs.outputs[0],mix.inputs[1]);nt.links.new(trans.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs['Surface'])
   raw=O/'raw';raw.mkdir(exist_ok=True);s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(raw/(name+'.exr'));bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/(name+'.png')),scene=s)
   views.append(dict(name=name,samples=s.cycles.samples,resolution_px=[900,700],camera_eye=list(s.camera.location),target=[0,0,.003],framing=fr,PNG_sha256=sha(O/(name+'.png')),raw_sha256=sha(raw/(name+'.exr'))))
  names=['gray-reverse']if stage=='graycut'else ['gray-front','gray-quarter','gray-reverse']if stage=='gray'else['preview-studio','preview-neutral']if stage=='preview'else['whole-front','whole-quarter','neutral-outdoor']
  for name in names:view(name,'neutral'in name)
  write('render-report.json'if stage=='final'else stage+'-render-report.json',dict(component_id=P['component_id'],views=views,source_geometry_unchanged=digest(m)==before,exposure=0,gamma=1,calibrated=False,protocol_sha256=sha(Path(__file__))))
 else:raise ValueError(stage)
