"""V2: link exact component meshes and explicitly pose a selected current needle.
No source library is edited. Placements and pointer calibration remain estimates.
The historical v1 builder is preserved; no instrument catalogue key is hardcoded.
"""
import bpy,json,hashlib,argparse,sys,math
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
ROOT=Path(__file__).resolve().parents[1]
pa=argparse.ArgumentParser();pa.add_argument('assets',nargs='+');pa.add_argument('--revision',required=True);pa.add_argument('--bindings',type=Path);pa.add_argument('--output-root',type=Path);pa.add_argument('--needle-asset');pa.add_argument('--needle-relative-degrees',type=float,default=-81);pa.add_argument('--inspection-export',action='store_true');a=pa.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
catalog=json.loads((ROOT/'tools/motorcycle-lab/catalog.json').read_text())['assets'];bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
collection=bpy.data.collections.new('MOTORCYCLE18_LINKED_REVIEW_COPIES');scene.collection.children.link(collection);linked=[];copies_by_original={}
for key in a.assets:
 c=catalog[key];path=ROOT/'assets-src/moto-components'/c['source'];before=hashlib.sha256(path.read_bytes()).hexdigest()
 if c.get('source_frame')=='isolated_local':assert c.get('assembly_placement'),(key,'Local part requires an explicit estimated placement before assembly review')
 with bpy.data.libraries.load(str(path),link=True) as (available,loaded):
  assert c['collection'] in available.collections,(key,c['collection']);loaded.collections=[c['collection']]
 # Linked objects outside a scene can retain stale serialized world matrices.
 # Evaluate their actual parent hierarchy before reading or copying transforms.
 scene.collection.children.link(loaded.collections[0]);bpy.context.view_layer.update()
 originals=list(loaded.collections[0].all_objects);copies={}
 for original in originals:
  copy=original.copy();copy.name='M18 ['+key+'] '+original.name;collection.objects.link(copy);copy.animation_data_clear();copy.hide_set(False);copy.hide_render=original.hide_render;copies[original]=copy;copies_by_original[(key,original.name)]=copy
 for original,copy in copies.items():
  copy.parent=copies.get(original.parent);copy.matrix_parent_inverse=original.matrix_parent_inverse.copy();copy.matrix_basis=original.matrix_basis.copy()
 bpy.context.view_layer.update()
 for original,copy in copies.items():
  if original.parent not in copies:copy.matrix_world=original.matrix_world.copy()
 bpy.context.view_layer.update()
 max_copy_delta=0
 for original,copy in copies.items():
  delta=max(abs(copy.matrix_world[i][j]-original.matrix_world[i][j])for i in range(4)for j in range(4));assert delta<1e-6,(key,original.name,'Copied hierarchy changed source transform',delta)
  max_copy_delta=max(max_copy_delta,delta)
 scene.collection.children.unlink(loaded.collections[0]);bpy.context.view_layer.update()
 placement=c.get('assembly_placement',{});q=placement.get('quaternion_source',[0,0,0,1]);transform=Matrix.LocRotScale(Vector(placement.get('position_source',[0,0,0])),Quaternion((q[3],q[0],q[1],q[2])),Vector(placement.get('scale_source',[1,1,1])))
 for original,copy in copies.items():
  if original.parent not in copies:copy.matrix_world=transform@copy.matrix_world
 bpy.context.view_layer.update();assert before==hashlib.sha256(path.read_bytes()).hexdigest()
 linked.append({'asset':key,'source':str(path.relative_to(ROOT)),'sha256':before,'source_collection':c['collection'],'objects':len(copies),'copied_hierarchy_max_world_matrix_delta':max_copy_delta,'placement':placement,'art_accepted':False})
bindings=[]
for binding in json.loads(a.bindings.read_text()) if a.bindings else []:
 child=copies_by_original[tuple(binding['child'])];parent=copies_by_original[tuple(binding['parent'])]
 before=child.matrix_world.copy();child.parent=parent;bpy.context.view_layer.update();child.matrix_world=before;bpy.context.view_layer.update()
 delta=max(abs(child.matrix_world[i][j]-before[i][j])for i in range(4)for j in range(4));assert delta<1e-6,('Rest transform changed',binding,delta)
 fixed={tuple(key):copies_by_original[tuple(key)].matrix_world.copy()for key in binding.get('fixed',[])}
 mode=parent.rotation_mode;rotation=parent.rotation_quaternion.copy()if mode=='QUATERNION'else parent.rotation_euler.to_quaternion();parent.rotation_mode='QUATERNION';parent.rotation_quaternion=rotation@Quaternion(Vector(binding['axis_source']),math.radians(binding['test_degrees']));bpy.context.view_layer.update()
 v=child.data.vertices[len(child.data.vertices)//2].co;travel=(child.matrix_world@v-before@v).length;assert travel>1e-5,('No actual attached mesh movement',binding)
 fixed_delta=max([max(abs(copies_by_original[key].matrix_world[i][j]-matrix[i][j])for i in range(4)for j in range(4))for key,matrix in fixed.items()]or[0]);assert fixed_delta<1e-7,('Fixed part moved',binding)
 parent.rotation_quaternion=rotation;bpy.context.view_layer.update()
 bindings.append({**binding,'rest_world_matrix_delta':delta,'actual_attached_vertex_travel_m':travel,'fixed_world_matrix_delta':fixed_delta,'mechanical_fit_certified':False})
# Pose only the explicitly selected copied pointer, using its declared local axis.
# Catalogue axes are glTF (x,z,-y); source axes are Blender (x,y,z).
needle_pose=None
if a.needle_asset:
 assert a.needle_asset in a.assets,'Needle source must be among linked assets'
 config=catalog[a.needle_asset];rig=next(r for r in config['rigs'] if r['id']=='speed_angle')
 assert rig['min']<=a.needle_relative_degrees<=rig['max']
 pointer=copies_by_original[(a.needle_asset,rig['node'])]
 axis=Vector((rig['axis'][0],-rig['axis'][2],rig['axis'][1])).normalized()
 rest=pointer.rotation_quaternion.copy() if pointer.rotation_mode=='QUATERNION' else pointer.rotation_euler.to_quaternion()
 children=[o for o in pointer.children_recursive if o.type=='MESH' and not o.hide_render]
 assert children,'No real visible needle mesh to verify'
 witness=max(((o,v.index)for o in children for v in o.data.vertices),key=lambda item:(item[0].matrix_world@item[0].data.vertices[item[1]].co-pointer.matrix_world.translation).length)
 o,i=witness;before=o.matrix_world@o.data.vertices[i].co
 pointer.rotation_mode='QUATERNION';pointer.rotation_quaternion=rest@Quaternion(axis,math.radians(a.needle_relative_degrees));bpy.context.view_layer.update()
 travel=(o.matrix_world@o.data.vertices[i].co-before).length
 assert abs(a.needle_relative_degrees)<1e-12 or travel>1e-5, 'Actual needle did not move'
 needle_pose={'asset':a.needle_asset,'control':rig['id'],'relative_degrees':a.needle_relative_degrees,'source_axis':list(axis),'rest_quaternion_wxyz':list(rest),'posed_quaternion_wxyz':list(pointer.rotation_quaternion),'witness_mesh':o.name,'witness_vertex':i,'actual_vertex_travel_m':travel,'manufacturer_calibration_certified':False}
scene['review_only_not_gameplay']=True;scene['all_installed_interfaces_unverified']=True;scene['rider_created']=False
world=bpy.data.worlds.new('Review studio CC0 HDR');world.use_nodes=True;n=world.node_tree.nodes;l=world.node_tree.links;env=n.new('ShaderNodeTexEnvironment');env.image=bpy.data.images.load(str(ROOT/'app/public/materials/kloppenheim_06_puresky_1k.hdr'));env.image.pack();l.new(env.outputs['Color'],n['Background'].inputs['Color']);n['Background'].inputs['Strength'].default_value=.3;scene.world=world
stage=bpy.data.collections.new('STUDIO_NOT_COMPONENTS');scene.collection.children.link(stage)
def move(o):
 for old in list(o.users_collection):old.objects.unlink(o)
 stage.objects.link(o);return o
def area(name,position,power,size):
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;o=bpy.data.objects.new(name,data);stage.objects.link(o);o.location=position;o.rotation_euler=(Vector((0,.01,.04))-o.location).to_track_quat('-Z','Y').to_euler()
area('Neutral key',(-.7,-.5,1.2),55,.65);area('Neutral fill',(.8,-.2,.9),30,.55);area('Soft rim',(0,.8,1),24,.5)
camera=bpy.data.objects.new('REVIEW_CAMERA',bpy.data.cameras.new('REVIEW_CAMERA'));stage.objects.link(camera);scene.camera=camera;camera.location=(0,.67,.49);camera.rotation_euler=(Vector((0,-.03,.07))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=28;camera.data.clip_start=.002
scene.render.engine='CYCLES';scene.cycles.samples=128;scene.cycles.use_denoising=True;scene.cycles.denoiser='OPENIMAGEDENOISE';scene.cycles.denoising_use_gpu=False;scene.view_layers[0].cycles.denoising_store_passes=True;scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
folder=(a.output_root/'source'if a.output_root else ROOT/'assets-src/moto-components'/a.revision);review=(a.output_root/'review'if a.output_root else ROOT/'creative/reviews'/a.revision);folder.mkdir(parents=True,exist_ok=True);review.mkdir(parents=True,exist_ok=True)
for library in bpy.data.libraries:library.filepath=bpy.path.relpath(library.filepath,start=str(folder))
source=folder/(a.revision+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(source))
export_record=None
if a.inspection_export:
 bpy.ops.object.select_all(action='DESELECT')
 for obj in collection.all_objects:
  if not obj.hide_render:obj.select_set(True)
 export_path=folder/(a.revision+'-inspection.glb')
 bpy.ops.export_scene.gltf(filepath=str(export_path),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_tangents=True,export_animations=False)
 export_record={'path':str(export_path.relative_to(ROOT)) if export_path.is_relative_to(ROOT) else str(export_path),'sha256':hashlib.sha256(export_path.read_bytes()).hexdigest(),'bytes':export_path.stat().st_size,'purpose':'Detailed linked review export, not mobile LOD or accepted game asset'}
for row in linked:assert row['sha256']==hashlib.sha256((ROOT/row['source']).read_bytes()).hexdigest()
(review/'source-geometry-check.json').write_text(json.dumps({'kind':'linked_review_assembly_not_gameplay_or_installed_certification','builder':'tools/build_motorcycle18_assembly_v2.py','builder_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'linked_sources':linked,'bindings':bindings,'needle_pose':needle_pose,'inspection_export':export_record,'physical_iphone_tested':False,'art_accepted':False,'driver_added':False},indent=2)+'\n');print('WEWA_M18_REVIEW_SOURCE',a.revision,len(linked))
