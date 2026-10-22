import bpy,pathlib,json,hashlib
from mathutils import Vector
R=pathlib.Path('/workspace/wewa');A=R/'assets-src/moto-components/front-mudguard-red-finish-v2';D=R/'creative/reviews/front-mudguard-red-finish-v2'
source=R/'assets-src/moto-components/front-mudguard/front-mudguard-shell-v1.blend';oldglb=source.with_name('front-mudguard-shell-inspection.glb');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
with bpy.data.libraries.load(str(source),link=True)as(src,dst):dst.collections=['WEWA_FRONT_MUDGUARD_SHELL_ISOLATED']
original=dst.collections[0];col=bpy.data.collections.new('WEWA_FRONT_MUDGUARD_RED_FINISH_V2');bpy.context.scene.collection.children.link(col)
mat=bpy.data.materials.new('WEWA plain red gloss paint - estimated finish v2');mat.use_nodes=True
p=mat.node_tree.nodes.get('Principled BSDF');values={'Base Color':(.41788506507873535,.006048833020031452,.012286487966775894,1),'Metallic':0,'Roughness':.22,'Coat Weight':.35,'Coat Roughness':.12,'IOR':1.5}
for key,value in values.items():p.inputs[key].default_value=value
mat.diffuse_color=values['Base Color'];mat.use_backface_culling=False
copies=[]
for old in original.all_objects:
 if old.type!='MESH' or old.hide_render:continue
 o=old.copy();col.objects.link(o)
 for slot in o.material_slots:slot.link='OBJECT';slot.material=mat
 assert o.data is old.data and o.data.library is not None
 assert o.matrix_world==old.matrix_world
 copies.append(o)
assert len(copies)==1
s=bpy.context.scene;s.name='Front mudguard red finish v2 - unchanged linked shell';bpy.ops.object.select_all(action='DESELECT')
for o in copies:o.select_set(True)
bpy.context.view_layer.objects.active=copies[0]
glb=A/'front-mudguard-red-finish-v2.glb'
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,use_active_scene=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=True,export_extras=False)
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=96;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=800;s.render.resolution_y=650;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0;s.view_settings.gamma=1
s.world=bpy.data.worlds.new('Neutral world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.16,.16,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.6
studio=bpy.data.collections.new('STUDIO_NOT_EXPORTED');s.collection.children.link(studio)
def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new('review-camera');camera=bpy.data.objects.new('review-camera',cam);studio.objects.link(camera);s.camera=camera;cam.lens=55;cam.clip_start=.01;cam.clip_end=100
for name,loc,power,size in [('KEY',(.6,-.4,1.2),65,.85),('FILL',(-.8,.4,.6),35,.8),('RAKE',(.7,.8,.3),0,.15)]:
 light=bpy.data.lights.new(name,'AREA');light.energy=power;light.shape='DISK';light.size=size;o=bpy.data.objects.new(name,light);studio.objects.link(o);o.location=loc;aim(o,(0,0,.16))
# Original native frame preserved; only review camera and lamps are authored.
camera.location=(.73,-.83,.67);aim(camera,(0,.06,.18))
bpy.ops.wm.save_as_mainfile(filepath=str(A/'front-mudguard-red-finish-v2.blend'),relative_remap=True)
bpy.ops.file.make_paths_relative()
# save_version=0: persist relative source library path without .blend1.
bpy.ops.wm.save_as_mainfile(filepath=str(A/'front-mudguard-red-finish-v2.blend'))
report={'revision':'front-mudguard-red-finish-v2','source':str((A/'front-mudguard-red-finish-v2.blend').relative_to(R)),'source_sha256':sha(A/'front-mudguard-red-finish-v2.blend'),'glb':str(glb.relative_to(R)),'glb_sha256':sha(glb),'collection':col.name,'selected_objects':[o.name for o in copies],'geometry_library':str(source.relative_to(R)),'geometry_library_sha256':sha(source),'old_glb_sha256':sha(oldglb),'linked_mesh_data':True,'material_slots_link':'OBJECT','geometry_changes':False,'native_transform_changes':False,'material_values_linear':values,'images_copied':False,'art_accepted':False,'G8':'pending','material_only':True}
(D/'main-fragment.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
