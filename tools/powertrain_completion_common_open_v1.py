"""Worker-only versioned source/export/render helper for explicit open skins and closed children. No supplied part geometry or shared registry writes."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from collections import Counter
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(folder,name,data):(folder/name).write_text(json.dumps(data,indent=2)+'\n')
def digest(mesh):
 mesh.calc_loop_triangles();return hashlib.sha256(repr(([tuple(v.co)for v in mesh.vertices],[tuple(t.vertices)for t in mesh.loop_triangles])).encode()).hexdigest()
def mesh_object(name,V,F):
 m=bpy.data.meshes.new(name);m.from_pydata(V,[],F);m.update();assert not m.validate();ob=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(ob)
 for f in m.polygons:f.use_smooth=True
 if hasattr(m,'set_sharp_from_angle'):m.set_sharp_from_angle(angle=math.radians(40))
 return ob
def export(H,name):
 bpy.ops.object.select_all(action='DESELECT')
 for ob in bpy.context.scene.objects:
  if ob.type=='MESH' and not ob.hide_render:ob.select_set(True);bpy.context.view_layer.objects.active=ob
 bpy.ops.export_scene.gltf(filepath=str(H/name),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_tangents=False)
def look(ob,t):ob.rotation_euler=(Vector(t)-ob.location).to_track_quat('-Z','Y').to_euler()
def bounds():
 pts=[ob.matrix_world@v.co for ob in bpy.context.scene.objects if ob.type=='MESH'and not ob.hide_render for v in ob.data.vertices];lo=Vector([min(v[i]for v in pts)for i in range(3)]);hi=Vector([max(v[i]for v in pts)for i in range(3)]);return (lo+hi)/2,max(hi-lo),lo,hi
def finish_source(H,O,P):
 H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True);bpy.context.preferences.filepaths.save_version=0;s=bpy.context.scene;s.unit_settings.system='METRIC';s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.cycles.max_bounces=5;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=900;s.render.resolution_y=700;s.render.resolution_percentage=100;s.view_layers[0].cycles.denoising_store_passes=True;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
 mat=bpy.data.materials.new('Neutral gray form review');mat.use_nodes=True;b=mat.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(.18,.18,.18,1);b.inputs['Roughness'].default_value=.3
 rows=[]
 for ob in list(s.objects):
  if ob.type!='MESH'or ob.hide_render:continue
  m=ob.data;m.calc_loop_triangles();m.materials.clear();m.materials.append(mat);count=Counter(tuple(sorted((a,b)))for f in m.polygons for a,b in zip(list(f.vertices),list(f.vertices[1:])+[f.vertices[0]]));boundary=sum(n==1 for n in count.values());assert boundary==P.get('expected_boundaries_by_object',{}).get(ob.name,P.get('expected_boundary_edges',0));assert max(count.values())==2;assert min(t.area for t in m.loop_triangles)>1e-14
  volume=sum(m.vertices[t.vertices[0]].co.dot(m.vertices[t.vertices[1]].co.cross(m.vertices[t.vertices[2]].co))/6 for t in m.loop_triangles);assert boundary>0 or volume>0
  rows.append(dict(object=ob.name,vertices=len(m.vertices),triangles=len(m.loop_triangles),boundary_edges=boundary,minimum_area=min(t.area for t in m.loop_triangles),volume_m3=volume if boundary==0 else None,open_surface_not_a_solid=boundary>0,geometry_digest=digest(m)))
 c,size,lo,hi=bounds();world=bpy.data.worlds.new('Neutral uncalibrated review');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.12,.12,1);world.node_tree.nodes['Background'].inputs[1].default_value=.4;s.world=world
 for name,direction,power,extent in [('Key',(-.7,1.1,1.6),3.2,.9),('Fill',(1,-.4,1.2),1.0,.8),('Rim',(.4,.8,-.25),1.4,.6)]:
  l=bpy.data.lights.new(name,'AREA');l.energy=power*(size/.3)**2;l.shape='DISK';l.size=extent*size;o=bpy.data.objects.new(name,l);s.collection.objects.link(o);o.location=c+Vector(direction)*size;look(o,c)
 cam=bpy.data.objects.new('Whole child camera',bpy.data.cameras.new('Whole child camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=size*1.65;cam.data.clip_start=max(size*.001,.00001);cam.data.clip_end=max(size*30,10);cam.location=c+Vector((1.1,.7,2.6))*size;look(cam,c)
 bpy.ops.wm.save_as_mainfile(filepath=str(H/'child-gray.blend'),compress=True);export(H,'child-gray.glb');write(O,'geometry-check.json',dict(objects=rows,bounds_m=[list(lo),list(hi)],parameters=P,source_sha256=sha(H/'child-gray.blend'),export_sha256=sha(H/'child-gray.glb'),art_accepted=False))
def stage(review,source_dir,mode):
 from bpy_extras.object_utils import world_to_camera_view
 H=R/'assets-src/moto-components'/source_dir;O=R/'creative/reviews'/review;P=json.loads((H/'parameters.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(H/('child-candidate.blend'if mode in ['preview','final']else'child-gray.blend')));s=bpy.context.scene
 before={ob.name:digest(ob.data)for ob in s.objects if ob.type=='MESH'and not ob.hide_render}
 if mode=='material':
  assert json.loads((O/'gray-review.json').read_text())['read_for_exterior_study'];material=P['material'];m=bpy.data.materials.new(material['name']);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=material['base_color_linear'];b.inputs['Metallic'].default_value=material['metallic'];b.inputs['Roughness'].default_value=material['roughness']
  for ob in s.objects:
   if ob.name in before:ob.data.materials.clear();ob.data.materials.append(m);assert digest(ob.data)==before[ob.name]
  bpy.ops.wm.save_as_mainfile(filepath=str(H/'child-candidate.blend'),compress=True);export(H,'child-candidate.glb');write(O,'material-transfer-check.json',dict(geometry_digest_before=before,geometry_digest_after={ob.name:digest(ob.data)for ob in s.objects if ob.name in before},geometry_identical=True,scope='Uniform proposed PBR response; no measured chemistry/grain or vendor pixels',art_accepted=False));return
 if mode=='final':assert json.loads((O/'preview-review.json').read_text())['read_for_exterior_study']
 c,size,lo,hi=bounds();rows=[];views=[('profile',(0,0,3)),('quarter',(1.1,.7,2.6))]if mode!='preview'else[('quarter',(1.1,.7,2.6))]
 if mode=='gray':views.append(('edge',(-2,.4,.8)))
 for name,dir in views:
  s.camera.location=c+Vector(dir)*size;look(s.camera,c);bpy.context.view_layer.update();points=[world_to_camera_view(s,s.camera,ob.matrix_world@v.co)for ob in s.objects if ob.name in before for v in ob.data.vertices];mins=[min(v[i]for v in points)for i in range(3)];maxs=[max(v[i]for v in points)for i in range(3)];assert min(mins[:2])>.01 and max(maxs[:2])<.99;assert mins[2]>s.camera.data.clip_start and maxs[2]<s.camera.data.clip_end
  samples=96 if mode=='final'else 16;s.cycles.samples=samples;label=mode+'-'+name;(O/'raw').mkdir(exist_ok=True);s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(O/'raw'/(label+'.exr'));bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/(label+'.png')),scene=s)
  rows.append(dict(view=label,samples=samples,resolution_px=[900,700],png=label+'.png',exr='raw/'+label+'.exr',png_sha256=sha(O/(label+'.png')),camera=list(s.camera.location),target=list(c),ortho_scale=s.camera.data.ortho_scale,actual_vertex_frame_min=mins,actual_vertex_frame_max=maxs))
 write(O,mode+'-render-report.json',dict(views=rows,geometry_unchanged=all(digest(bpy.data.objects[n].data)==d for n,d in before.items()),protocol_sha256=sha(Path(__file__)),art_accepted=False,physical_iphone_tested=False))
