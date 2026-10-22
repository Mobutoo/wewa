# Template SHA256 0178181c57ecb82d7f608dadbf284dc57f216a66d09b3e5886a638aa6ded2fb8; recovered guide pose revision.
# Template SHA256 4ef2f1a97dbed54645ea53434107c4f413c4f3047c28e11c5c31c845428c3c47; four guard parents namespace and cameras.
"""Render-only gray override; existing linked geometry/materials are never saved or edited."""
import bpy,json,sys,hashlib,runpy
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');K='engine-protection-exterior-context-v2';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;mode=sys.argv[sys.argv.index('--')+1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=H/'integration-wrapper.blend'
if mode=='preview':assert (O/'gray-read.json').exists()
if mode=='final':assert (O/'preview-read.json').exists()
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;objects=[o for o in s.objects if o.type=='MESH'];assert len(objects)==4;coords=[o.matrix_world@Vector(p)for o in objects for p in o.bound_box];low=Vector([min(p[i]for p in coords)for i in range(3)]);high=Vector([max(p[i]for p in coords)for i in range(3)]);target=(low+high)/2;size=max(high-low);check=runpy.run_path(str(R/'tools/blender_component_camera_preflight.py'))['check_component_camera']
folder={'gray':'gray-preview-v2','preview':'material-preview-v2','final':'material-96'}[mode];out=O/folder;(out/'raw').mkdir(parents=True,exist_ok=False)
w=bpy.data.worlds.new('Uncalibrated studio');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.2,.2,.2,1);w.node_tree.nodes['Background'].inputs[1].default_value=.5;s.world=w
for name,di,power in [('Key',(-2,-1,2),500),('Fill',(2,1,1),300),('Rim',(0,-2,-.3),200)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power*size*size;d.size=size*.9;ob=bpy.data.objects.new(name,d);s.collection.objects.link(ob);ob.location=target+size*Vector(di);ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('Context inspection camera',bpy.data.cameras.new('Context inspection camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=size*1.45;cam.data.clip_start=size*.001;cam.data.clip_end=size*100
s.render.engine='CYCLES';s.cycles.samples=96 if mode=='final' else 16;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.render.use_stamp=False
if mode=='gray':
 m=bpy.data.materials.new('Render-only gray override');m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.20,.20,.20,1);p.inputs['Roughness'].default_value=.35;s.view_layers[0].material_override=m
views=[('quarter',(-2,-1,.7)),('reverse',(2,.6,.7)),('profile',(0,-3,0))]if mode=='gray'else[('quarter',(-2,-1,.7)),('reverse',(2,.6,.7))]
if mode=='final':views.append(('neutral',(-2,-.5,.8)))
rows=[]
for name,di in views:
 if name=='neutral':
  for l in bpy.data.lights:l.energy=0
  nt=w.node_tree;tex=nt.nodes.new('ShaderNodeTexEnvironment');tex.image=bpy.data.images.load(str(R/'app/public/materials/kloppenheim_06_puresky_1k.hdr'));nt.links.new(tex.outputs['Color'],nt.nodes['Background'].inputs[0]);nt.nodes['Background'].inputs[1].default_value=.65
 cam.location=target+size*Vector(di);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.view_layers[0].update();pf=check(s,objects);png=out/(name+'.png');exr=out/'raw'/(name+'.exr');s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(exr);bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(png),scene=s);rows.append({'view':name,'samples':s.cycles.samples,'resolution':[1000,800],'PNG':str(png.relative_to(R)),'EXR':str(exr.relative_to(R)),'PNG_sha256':sha(png),'EXR_sha256':sha(exr),'camera':list(cam.location),'target':list(target),'camera_preflight':pf});(out/'render-report.json').write_text(json.dumps({'source':str(source.relative_to(R)),'source_sha256':sha(source),'protocol':'creative/research/'+K+'/render.py','protocol_sha256':sha(Path(__file__)),'views':rows,'mode':mode,'denoising':False,'gray_override_only':mode=='gray','source_materials_unmodified':True,'new_geometry':False,'art_accepted':False},indent=2))
