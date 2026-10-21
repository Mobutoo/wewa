import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');key=sys.argv[sys.argv.index('--')+1];H=R/'assets-src/moto-components'/key;O=R/'creative/reviews'/key;(O/'raw').mkdir(parents=True,exist_ok=True);source=next(H.glob('*.blend'));bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
objects=[o for o in bpy.data.objects if o.type=='MESH'];coords=[o.matrix_world@Vector(p)for o in objects for p in o.bound_box];low=Vector([min(p[i]for p in coords)for i in range(3)]);high=Vector([max(p[i]for p in coords)for i in range(3)]);target=(low+high)/2;size=max(high-low)
for ob in list(bpy.data.objects):
 if ob.type in ('LIGHT','CAMERA'):bpy.data.objects.remove(ob,do_unlink=True)
w=bpy.data.worlds.new('Neutral review');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.2,.2,.2,1);w.node_tree.nodes['Background'].inputs[1].default_value=.5;s.world=w
for name,direction,power,scale in [('KEY',(-1,-1,2),500,.9),('FILL',(1,2,1),250,.9),('RIM',(0,-2,.5),150,.6)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power*size*size;d.size=size*scale;ob=bpy.data.objects.new(name,d);s.collection.objects.link(ob);ob.location=target+size*Vector(direction);ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('Isolated review camera',bpy.data.cameras.new('Isolated review camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=size*1.65;cam.data.clip_start=size*.001;cam.data.clip_end=size*100
s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';report=[]
for name,direction in [('gray-quarter',(2,-2,1.5)),('gray-reverse',(-2,1,1)),('reflection',(2,-1,1))]:
 if name=='reflection':
  mat=bpy.data.materials.new('RAM reflection diagnostic only');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.3,.3,.3,1);p.inputs['Metallic'].default_value=.8;p.inputs['Roughness'].default_value=.12
  for o in objects:o.data.materials.clear();o.data.materials.append(mat)
 cam.location=target+size*Vector(direction);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(O/'raw'/(name+'.exr'));bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/(name+'.png')),scene=s);report.append({'view':name,'samples':96,'resolution':[1200,1000],'camera':list(cam.location),'target':list(target),'ortho_scale':cam.data.ortho_scale});(O/'render-report.json').write_text(json.dumps({'views':report,'material_stage':False,'art_accepted':False},indent=2))
