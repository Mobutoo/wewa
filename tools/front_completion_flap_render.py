import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa'); package=sys.argv[sys.argv.index('--')+1];H=R/'assets-src/moto-components'/package;O=R/'creative/reviews'/package;O.mkdir(parents=True,exist_ok=True);(O/'raw').mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(H/'flap-gray.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=2;s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.denoising_use_gpu=False;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100
reports=[]
for name,eye,target,scale in [('gray-quarter',(.25,-.15,.4),(0,.12,0),.37),('gray-front',(0,.12,.5),(0,.12,0),.37),('reflection-edge',(.20,.02,.16),(0,.045,.005),.13)]:
 if name.startswith('reflection'):
  m=bpy.data.materials.new('Temporary reflection diagnostic');m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.3,.32,.35,1);p.inputs['Metallic'].default_value=.85;p.inputs['Roughness'].default_value=.08
  for ob in bpy.data.objects:
   if ob.type=='MESH':ob.data.materials.clear();ob.data.materials.append(m)
  key=bpy.data.objects.get('KEY');key.location=(.08,.03,.08);key.data.energy=.6;key.data.shape='RECTANGLE';key.data.size=.08;key.data.size_y=.006;key.rotation_euler=(Vector(target)-key.location).to_track_quat('-Z','Y').to_euler()
 s.camera.location=eye;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale
 s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(O/'raw'/(name+'.exr'));bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/(name+'.png')),scene=s)
 reports.append(dict(view=name,samples=96,resolution=[1400,1000],camera=list(eye),target=list(target),scale=scale,macro_crop=name.startswith('reflection')))
 (O/'render-report.json').write_text(json.dumps(dict(views=reports,material_stage=False,art_accepted=False),indent=2))
