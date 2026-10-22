from pathlib import Path
import bpy,json,hashlib,runpy,sys
from mathutils import Vector
R=Path('/workspace/wewa');K='headlamp-interior-completion-v3';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K
source=H/'visible-optics-v3.blend';bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
preview='--preview' in sys.argv
if preview:O=O/'preview';O.mkdir(exist_ok=True)
denoised='--denoised' in sys.argv
if denoised:O=O/'denoised-96';O.mkdir(exist_ok=True)
objects=[o for o in bpy.data.objects if o.type=='MESH'];s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.use_denoising=False;s.cycles.max_bounces=12;s.cycles.transmission_bounces=8;s.render.threads_mode='FIXED';s.render.threads=2
s.render.resolution_x=800;s.render.resolution_y=600;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
if preview:s.cycles.samples=8;s.render.resolution_percentage=50
if denoised:s.cycles.use_denoising=True
w=bpy.data.worlds.new('Neutral sky optics review');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.45,.48,.52,1);w.node_tree.nodes['Background'].inputs[1].default_value=.8;s.world=w
for n,loc,power,size in [('Key',(-.12,-.12,.25),9,.16),('Fill',(.16,.10,.18),5,.14)]:
 l=bpy.data.lights.new(n,'AREA');l.energy=power;l.size=size;o=bpy.data.objects.new(n,l);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
c=bpy.data.objects.new('Visible optics review camera',bpy.data.cameras.new('Visible optics review camera'));s.collection.objects.link(c);s.camera=c;c.data.type='ORTHO';c.data.ortho_scale=.28;c.data.clip_start=.001;c.data.clip_end=10
pre=runpy.run_path(str(R/'tools/blender_component_camera_preflight.py'))['check_component_camera'];rows=[];(O/'raw').mkdir(exist_ok=True)
for name,pos in [('front',(0,0,.35)),('oblique',(.14,-.10,.32)),('raking',(-.16,.02,.25))]:
 if preview and name!='oblique':continue
 if denoised and name!='front':continue
 c.location=pos;c.rotation_euler=(Vector((0,0,0))-c.location).to_track_quat('-Z','Y').to_euler();s.view_layers[0].update();check=pre(s,objects)
 exr=O/'raw'/(name+'.exr');png=O/(name+'.png');s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.filepath=str(exr);bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(png),scene=s)
 rows.append({'view':name,'camera':pos,'samples':s.cycles.samples,'resolution':[400,300] if preview else [800,600],'camera_preflight':check,'PNG':str(png.relative_to(R)),'EXR':str(exr.relative_to(R))})
 (O/'render-report.json').write_text(json.dumps({'source':str(source.relative_to(R)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'views':rows,'denoising':denoised,'denoising_scope':'Separate Cycles denoised presentation, original undenoised raw retained' if denoised else 'None','emission':False,'art_accepted':False},indent=2))
