"""Unchanged original components in an explicit review-only rear-cluster pose."""
import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];key='rear-cluster-review-v2';H=R/'assets-src/moto-components'/key;O=R/'creative/reviews'/key;O.mkdir(exist_ok=True,parents=True);P=json.loads((H/'parameters-v1.json').read_text());stage=sys.argv[sys.argv.index('--')+1];src=H/(key+'.blend');glb=H/(key+'.glb');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,d):(O/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def settings():
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.cycles.samples=96;s.cycles.max_bounces=6;s.render.threads_mode='FIXED';s.render.threads=2;s.view_layers[0].cycles.denoising_store_passes=True;s.render.resolution_x=900;s.render.resolution_y=700;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0;s.view_settings.gamma=1;s.unit_settings.system='METRIC';bpy.context.preferences.filepaths.save_version=0
folder=O/'protocols';folder.mkdir(exist_ok=True);(folder/(sha(Path(__file__))+'-'+Path(__file__).name)).write_bytes(Path(__file__).read_bytes())
if stage=='build':
 bpy.ops.wm.read_factory_settings(use_empty=True);settings();s=bpy.context.scene;root=bpy.data.collections.new('WEWA_REAR_CLUSTER_REVIEW_ONLY');s.collection.children.link(root);origin=Vector(P['origin_source_world_m']);L=Matrix(((-1,0,0),(0,0,1),(0,1,0)));B=Matrix(((1,0,0),(0,0,-1),(0,1,0)));assert max(abs(v)for row in(L.transposed()@B-Matrix(((-1,0,0),(0,1,0),(0,0,-1))))for v in row)<1e-10
 rows=[];obs=[]
 for part in P['parts']:
  path=R/part['source'];assert sha(path)==part['source_sha256'];before=sha(path)
  with bpy.data.libraries.load(str(path),link=False)as(a,b):assert 'EXTERIOR_CHILD'in a.objects;b.objects=['EXTERIOR_CHILD']
  ob=b.objects[0];assert ob and ob.type=='MESH';ob.name=part['component_id'];root.objects.link(ob);m=ob.data;m.calc_loop_triangles();digest=hashlib.sha256(repr(([(tuple(v.co))for v in m.vertices],[tuple(t.vertices)for t in m.loop_triangles],[(tuple(u.uv))for u in m.uv_layers.active.data])).encode()).hexdigest();rot=B if part['rotation']=='body_forward'else L;ob.matrix_world=Matrix.Translation(origin+L@Vector(part['offset_rear_frame_m']))@rot.to_4x4();assert abs(ob.matrix_world.to_3x3().determinant()-1)<1e-8;ob['review_source']=part['source'];ob['physical_component_id']=part['component_id'];ob['placement_status']='Authored review-only; not fitted or received';assert sha(path)==before;obs.append(ob);rows.append(dict(component_id=part['component_id'],source=part['source'],source_sha256=before,source_unchanged=True,source_mesh_P_I_UV_digest=digest,vertices=len(m.vertices),triangles=len(m.loop_triangles),world_matrix=[list(v)for v in ob.matrix_world]))
 bpy.context.view_layer.update();corners=[ob.matrix_world@Vector(c)for ob in obs for c in ob.bound_box];lo=Vector([min(p[i]for p in corners)for i in range(3)]);hi=Vector([max(p[i]for p in corners)for i in range(3)]);center=(lo+hi)/2;size=max(hi-lo)
 w=bpy.data.worlds.new('Original assembly review studio');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.12,.12,.12,1);w.node_tree.nodes['Background'].inputs[1].default_value=.4;s.world=w
 for name,offset,power,k in [('Key',(-1,1.2,2),220,1.1),('Fill',(1,.7,.7),90,.9),('Rim',(-.5,-1,-.2),130,.7)]:
  d=bpy.data.lights.new(name,'AREA');d.energy=power*size*size;d.shape='RECTANGLE';d.size=k*size;d.size_y=k*size*.6;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=center+Vector(offset)*size;aim(o,center)
 cam=bpy.data.objects.new('Assembly review camera',bpy.data.cameras.new('Assembly review camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=size*1.65;cam.data.clip_start=.0001;cam.data.clip_end=100;cam.location=center+Vector((0,3,.5))*size;aim(cam,center)
 trees={o.name:BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices)for f in o.data.polygons],all_triangles=False,epsilon=0.)for o in obs};contacts=[]
 for i,a in enumerate(obs):
  for b in obs[i+1:]:contacts.append(dict(parts=[a.name,b.name],potential_triangle_contacts=len(trees[a.name].overlap(trees[b.name])),scope='BVH surface contact candidates, not enclosed-volume or mechanical acceptance'))
 bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True,export_tangents=False,export_animations=False);write('assembly-source-check.json',dict(source_sha256=sha(src),export_sha256=sha(glb),components=rows,triangles=sum(v['triangles']for v in rows),bounds_source_world_m=dict(min=list(lo),max=list(hi)),potential_surface_contacts=contacts,known_open_interfaces=P['known_open_interfaces'],scope=P['scope'],protocol_sha256=sha(Path(__file__)),art_accepted=False));write('source-geometry-check.json',dict(source_sha256=sha(src),export_sha256=sha(glb),source_parts_unchanged=True,scope=P['scope']))
else:
 assert stage in ['gray','preview','final'];bpy.ops.wm.open_mainfile(filepath=str(src));settings();s=bpy.context.scene;obs=[o for o in s.objects if o.type=='MESH'];corners=[o.matrix_world@Vector(c)for o in obs for c in o.bound_box];lo=Vector([min(p[i]for p in corners)for i in range(3)]);hi=Vector([max(p[i]for p in corners)for i in range(3)]);center=(lo+hi)/2;size=max(hi-lo);before=sha(src)
 if stage=='gray':
  m=bpy.data.materials.new('Neutral assembly contact review');m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.18,.18,.18,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.32
  for ob in obs:
   ob.data.materials.clear();ob.data.materials.append(m)
   for face in ob.data.polygons:face.material_index=0
 else:assert json.loads((O/'gray-review.json').read_text())['actually_read']
 if stage=='final':assert json.loads((O/'preview-review.json').read_text())['actually_read']
 views=[]
 def view(name,eye,neutral=False):
  s.camera.location=center+Vector(eye)*size;aim(s.camera,center);s.cycles.samples=96 if stage=='final'else 16
  if neutral:
   for l in bpy.data.lights:l.energy=0
   w=bpy.data.worlds.new('Assembly neutral sky');w.use_nodes=True;nt=w.node_tree;tex=nt.nodes.new('ShaderNodeTexEnvironment');tex.image=bpy.data.images.load(str(R/'app/public/materials/kloppenheim_06_puresky_1k.hdr'));nt.links.new(tex.outputs['Color'],nt.nodes['Background'].inputs['Color']);nt.nodes['Background'].inputs['Strength'].default_value=.65;s.world=w
  raw=O/'raw';raw.mkdir(exist_ok=True);s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(raw/(name+'.exr'));bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/(name+'.png')),scene=s);views.append(dict(name=name,samples=s.cycles.samples,PNG_sha256=sha(O/(name+'.png')),actually_saved=True,camera_eye=list(s.camera.location),camera_target=list(center)))
 if stage=='gray':view('gray-rear',(0,3,.35));view('gray-quarter',(1.7,3,1.1))
 elif stage=='preview':view('preview-studio',(1.7,3,1.1));view('preview-neutral',(1.7,3,1.1),True)
 else:view('whole-rear',(0,3,.35));view('whole-quarter',(1.7,3,1.1));view('neutral-rear',(1.7,3,1.1),True)
 assert sha(src)==before;write('render-report.json'if stage=='final'else stage+'-render-report.json',dict(source_sha256=sha(src),export_sha256=sha(glb),views=views,protocol_sha256=sha(Path(__file__)),scope=P['scope'],source_unchanged=True,art_accepted=False))
