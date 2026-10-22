"""Material-only rear stalk revision; independent unchanged LH/RH geometry; no fitted join."""
import bpy,json,hashlib,sys,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];K='rear-indicator-dark-polymer-v2';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;D=R/'creative/research'/K
for p in [H,O,D]:p.mkdir(exist_ok=True,parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
phase=sys.argv[sys.argv.index('--')+1];F=H/'rear-indicator-dark-polymer-v2.blend'
if phase=='build':
 bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.name='REVIEW';s.unit_settings.system='METRIC';mat=bpy.data.materials.new('Original uncalibrated clean dark polymer proposal');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.012,.014,.012,1);bs.inputs['Metallic'].default_value=0;bs.inputs['Roughness'].default_value=.56;bs.inputs['IOR'].default_value=1.46;rows=[]
 for side in ['left','right']:
  p=R/f'assets-src/moto-components/rear-indicator-{side}-stalk-v1/rear-indicator-{side}-stalk-v1.blend';oldsha=sha(p);name='WEWA_REAR_INDICATOR_'+side.upper()+'_STALK_V1'
  with bpy.data.libraries.load(str(p),link=True)as(a,b):b.collections=[name]
  orig=next(x for x in b.collections[0].all_objects if x.type=='MESH');ob=orig.copy();ob.name='REAR_'+side.upper()+'_STALK_EXACT_GEOMETRY_DARK_MATERIAL';col=bpy.data.collections.new('REAR_INDICATOR_'+side.upper()+'_DARK_POLYMER_V2');col.objects.link(ob)
  for slot in ob.material_slots:slot.link='OBJECT';slot.material=mat
  part=bpy.data.scenes.new(side.upper()+'_EXPORT');part.collection.children.link(col);bpy.context.window.scene=part;bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.export_scene.gltf(filepath=str(H/(side+'-stalk.glb')),export_format='GLB',use_selection=True,export_materials='EXPORT',export_yup=True,export_apply=True,export_tangents=False,export_animations=False,use_active_scene=True)
  bpy.context.window.scene=s;inst=bpy.data.objects.new('Review '+side,None);s.collection.objects.link(inst);inst.instance_type='COLLECTION';inst.instance_collection=col;inst.location=(.032 if side=='left' else-.032,0,0)
  rows.append(dict(side=side,source=str(p.relative_to(R)),source_sha256=oldsha,collection=col.name,object=ob.name,linked_mesh_data=ob.data.name,vertices=len(ob.data.vertices),triangles=sum(len(x.vertices)-2 for x in ob.data.polygons),source_unchanged=sha(p)==oldsha,export=str((H/(side+'-stalk.glb')).relative_to(R))))
 s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=900;s.render.resolution_y=650;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_layers[0].cycles.denoising_store_passes=True
 world=bpy.data.worlds.new('Neutral studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.4,.4,.4,1);world.node_tree.nodes['Background'].inputs[1].default_value=.55;s.world=world;target=Vector((0,0,.028))
 for name,loc,power,size in [('Key',(.18,-.25,.28),14,.2),('Fill',(-.2,.1,.15),8,.15)]:
  ld=bpy.data.lights.new(name,'AREA');ld.energy=power;ld.size=size;lo=bpy.data.objects.new(name,ld);s.collection.objects.link(lo);lo.location=loc;lo.rotation_euler=(target-lo.location).to_track_quat('-Z','Y').to_euler()
 cam=bpy.data.objects.new('Review camera',bpy.data.cameras.new('Review camera'));s.collection.objects.link(cam);cam.data.type='ORTHO';cam.data.ortho_scale=.145;cam.data.clip_start=.001;cam.data.clip_end=10;cam.location=(.16,-.25,.12);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam;s['scope']='Material-only revision of two independently photographed related rear stalks; dimensions and installed joins unreceived';bpy.context.preferences.filepaths.save_version=0
 for lib in bpy.data.libraries:lib.filepath=bpy.path.relpath(lib.filepath,start=str(H))
 bpy.ops.wm.save_as_mainfile(filepath=str(F),compress=True);(O/'source-check.json').write_text(json.dumps(dict(source=str(F.relative_to(R)),source_sha256=sha(F),parents=rows,geometry_unchanged=True,material_estimated=True,art_accepted=False),indent=2)+'\n')
elif phase=='export':
 bpy.ops.wm.open_mainfile(filepath=str(F));before=sha(F)
 for side in ['left','right']:
  bpy.context.window.scene=bpy.data.scenes[side.upper()+'_EXPORT'];bpy.ops.object.select_all(action='DESELECT');ob=next(o for o in bpy.context.scene.objects if o.type=='MESH');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.export_scene.gltf(filepath=str(H/(side+'-stalk.glb')),export_format='GLB',use_selection=True,use_active_scene=True,export_materials='EXPORT',export_yup=True,export_apply=True,export_tangents=False,export_animations=False)
 assert before==sha(F)
else:
 bpy.ops.wm.open_mainfile(filepath=str(F));s=bpy.data.scenes['REVIEW'];bpy.context.window.scene=s;target=Vector((0,0,.028));samples=12 if phase=='preview' else 96;s.cycles.samples=samples;dest=O/phase;dest.mkdir(exist_ok=True);raw=dest/'raw';raw.mkdir(exist_ok=True);views=[]
 for name,eye in ([('quarter',(.16,-.25,.12))]if phase=='preview' else[('quarter',(.16,-.25,.12)),('reverse',(-.18,.22,.10)),('neutral',(0,-.3,.045))]):
  s.camera.location=eye;s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler()
  if name=='neutral':
   nt=s.world.node_tree;tex=nt.nodes.new('ShaderNodeTexEnvironment');tex.image=bpy.data.images.load(str(R/'app/public/materials/kloppenheim_06_puresky_1k.hdr'));nt.links.new(tex.outputs['Color'],nt.nodes['Background'].inputs['Color']);nt.nodes['Background'].inputs[1].default_value=.65
   for ob in s.objects:
    if ob.type=='LIGHT':ob.hide_render=True
  s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(raw/(name+'.exr'));bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(dest/(name+'.png')),scene=s);views.append(dict(name=name,samples=samples,resolution_px=[900,650],PNG_sha256=sha(dest/(name+'.png')),EXR_sha256=sha(raw/(name+'.exr'))))
 (dest/'render-report.json').write_text(json.dumps(dict(source_sha256=sha(F),views=views,art_accepted=False),indent=2)+'\n')
