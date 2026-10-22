import bpy,json,math,hashlib,sys
from pathlib import Path
from mathutils import Matrix,Vector
R=Path('/workspace/wewa'); D=R/'creative/research/gear-selector-exterior-context-v1'; H=R/'assets-src/moto-components/gear-selector-exterior-context-v1'; O=R/'creative/reviews/gear-selector-exterior-context-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def look(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
names=['gear-selector-'+n+'-v1' for n in ['arm','split-hub','toe-rubber','heel-pad','clamp-ears-visible-head']]
poses=[(Matrix.Identity(3),[0,0,0]),(Matrix.Rotation(math.pi,3,'Z'),[0,0,-.0305]),(Matrix.Identity(3),[-.145,.036,-.0045]),(Matrix(((0,1,0),(0,0,1),(1,0,0))),[.130,.056,.036]),(Matrix.Rotation(math.pi,3,'Z'),[0,0,-.0305])]
if '--build' in sys.argv:
 bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;bpy.context.preferences.filepaths.save_version=0
 kit=bpy.data.collections.new('GEAR_SELECTOR_EXTERIOR_CONTEXT_V1');s.collection.children.link(kit)
 root=bpy.data.objects.new('GEAR_SELECTOR_EXTERIOR_CONTEXT_ROOT',None);kit.objects.link(root);root['physical_ids_created']=0;root['interfaces']='Unqualified review context, not manufactured fit';root['variant']='Marked JZ561415 kit, related variant conditional for RDC125'
 rows=[]
 for name,(rot,pos) in zip(names,poses):
  source=R/'assets-src/moto-components'/name/'child-candidate.blend'
  with bpy.data.libraries.load(str(source),link=True) as (src,dst):dst.objects=[n for n in src.objects if n.startswith(('SELECTOR_','EAR_','VISIBLE_HEX_'))]
  col=bpy.data.collections.new(name+'__EXACT_NATIVE');objs=[o for o in dst.objects if o and o.type=='MESH'];assert objs
  for ob in objs:col.objects.link(ob)
  inst=bpy.data.objects.new(name+'__RIGID_POSE',None);kit.objects.link(inst);inst.instance_type='COLLECTION';inst.instance_collection=col;inst.parent=root;mat=rot.to_4x4();mat.translation=Vector(pos);inst.matrix_basis=mat
  rows.append(dict(parent=name,source=str(source.relative_to(R)),sha256=sha(source),objects=[o.name for o in objs],matrix=[list(r) for r in mat],scale=[1,1,1],geometry_linked=True,materials_linked=True))
 s.unit_settings.system='METRIC';s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.cycles.max_bounces=5;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=1000;s.render.resolution_y=700;s.render.resolution_percentage=100;s.view_layers[0].cycles.denoising_store_passes=True;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
 world=bpy.data.worlds.new('Neutral review world');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.15,.15,.15,1);world.node_tree.nodes['Background'].inputs[1].default_value=.6;s.world=world
 center=Vector((0,.020,.01));size=.33
 for name,di,power in [('Key',(-.6,1,1.5),8),('Fill',(.5,-.8,1),5),('Reverse',(.1,1,-1),6)]:
  l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=.30;o=bpy.data.objects.new(name,l);s.collection.objects.link(o);o.location=center+Vector(di)*size;look(o,center)
 cam=bpy.data.objects.new('Review camera',bpy.data.cameras.new('Review camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.36;cam.data.clip_start=.001;cam.data.clip_end=10;cam.location=center+Vector((.2,1,2))*.33;look(cam,center)
 bpy.ops.wm.save_as_mainfile(filepath=str(H/'gear-selector-exterior-context-v1.blend'),compress=True,relative_remap=True)
 write(D/'native-links-and-transforms.json',dict(parents=rows,collection=kit.name,root=root.name,coordinate_frame='Arm-native X toe negative / heel positive, Y projected up, Z toward rubbers; hub projects -Z',new_physical_ids=0,art_accepted=False))
else:
 mode=sys.argv[-1];bpy.ops.wm.open_mainfile(filepath=str(H/'gear-selector-exterior-context-v1.blend'));s=bpy.context.scene
 if mode=='preview':assert (O/'gray-read.json').exists()
 if mode=='final':assert (O/'preview-read.json').exists()
 if mode=='gray':
  m=bpy.data.materials.new('View-layer-only neutral gray');m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(.18,.18,.18,1);b.inputs['Roughness'].default_value=.32;s.view_layers[0].material_override=m
 views=[('quarter',(.2,1.3,2.2)),('reverse',(-.1,.8,-2.2)),('neutral',(0,0,3))]
 if mode=='preview':views=views[:2]
 rows=[];(O/'raw').mkdir(exist_ok=True)
 for label,di in views:
  s.camera.location=Vector((0,.020,.01))+Vector(di)*.33;look(s.camera,(0,.020,.01));s.cycles.samples=96 if mode=='final' else 16
  if label=='neutral':s.view_settings.look='None'
  stem=mode+'-'+label;s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(O/'raw'/(stem+'.exr'));bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/(stem+'.png')),scene=s)
  rows.append(dict(view=label,samples=s.cycles.samples,png=stem+'.png',raw='raw/'+stem+'.exr',resolution=[1000,700],camera=list(s.camera.location),look=s.view_settings.look,actual_native_render=True,png_sha256=sha(O/(stem+'.png')),raw_sha256=sha(O/'raw'/(stem+'.exr'))))
 write(O/(mode+'-render-report.json'),dict(views=rows,protocol_sha256=sha(Path(__file__)),source_sha256=sha(H/'gear-selector-exterior-context-v1.blend'),original_materials_unmodified=True,gray_override_only=mode=='gray',art_accepted=False))
