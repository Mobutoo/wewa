import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');key=sys.argv[sys.argv.index('--')+1];H=R/'assets-src/moto-components'/key;O=R/'creative/reviews'/key/'camera-proof-v4';O=O/'preview'if'--preview'in sys.argv else O;(O/'raw').mkdir(parents=True,exist_ok=True);source=next(H.glob('*.blend'));bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
objects=[o for o in bpy.data.objects if o.type=='MESH'];coords=[o.matrix_world@Vector(p)for o in objects for p in o.bound_box];low=Vector([min(p[i]for p in coords)for i in range(3)]);high=Vector([max(p[i]for p in coords)for i in range(3)]);target=(low+high)/2;size=max(high-low)
sys.path.insert(0,str(R/'tools'))
from blender_component_camera_preflight import check_component_camera
for ob in list(bpy.data.objects):
 if ob.type in ('LIGHT','CAMERA'):bpy.data.objects.remove(ob,do_unlink=True)
w=bpy.data.worlds.new('Neutral review');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.2,.2,.2,1);w.node_tree.nodes['Background'].inputs[1].default_value=.5;s.world=w
for name,direction,power,scale in [('KEY',(-1,-1,2),500,.9),('FILL',(1,2,1),250,.9),('RIM',(0,-2,.5),150,.6)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power*size*size;d.size=size*scale;ob=bpy.data.objects.new(name,d);s.collection.objects.link(ob);ob.location=target+size*Vector(direction);ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('Isolated review camera',bpy.data.cameras.new('Isolated review camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=size*1.65;cam.data.clip_start=size*.001;cam.data.clip_end=size*100
s.render.engine='CYCLES';s.cycles.samples=24 if'--preview'in sys.argv else 96;s.cycles.use_denoising=True;s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';report=[]
for name,direction in [('terminal-detail',(2,-2,1.5)),('terminal-tip',(-1.4,1,1.2))]:
 if name=='neutral':
  for light in bpy.data.lights:light.energy=0
  nt=s.world.node_tree;tex=nt.nodes.new('ShaderNodeTexEnvironment');tex.image=bpy.data.images.load(str(R/'app/public/materials/kloppenheim_06_puresky_1k.hdr'));nt.links.new(tex.outputs['Color'],nt.nodes['Background'].inputs[0]);nt.nodes['Background'].inputs[1].default_value=.65
 view_target=Vector((-.08366,.08141,.004))if name in ('terminal-detail','terminal-tip')else target;view_size=max(size*2,.020) if name in ('terminal-detail','terminal-tip')else size;cam.data.ortho_scale=.030 if name in ('terminal-detail','terminal-tip')else size*1.65
 cam.location=view_target+view_size*Vector(direction);cam.rotation_euler=(view_target-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();preflight=check_component_camera(s,objects,allow_crop=True);s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(O/'raw'/(name+'.exr'));bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/(name+'.png')),scene=s);report.append({'view':name,'samples':s.cycles.samples,'resolution':[1200,1000],'camera':list(cam.location),'target':list(view_target),'allow_deliberate_macro_crop':name in ('terminal-detail','terminal-tip'),'ortho_scale':cam.data.ortho_scale,'camera_preflight':preflight});(O/'render-report.json').write_text(json.dumps({'views':report,'material_stage':True,'art_accepted':False},indent=2))
