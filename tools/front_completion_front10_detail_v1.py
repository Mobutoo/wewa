"""Detail cameras in child-specific plan, no geometry mutation; fixed lighting, no depth clipping."""
import bpy,sys,json,runpy,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');key,stem,quality=sys.argv[sys.argv.index('--')+1:][:3];H=R/'assets-src/moto-components'/key;B=R/'creative/reviews'/key;O=B/('gray-detail-96'if quality=='final'else'gray-detail-preview');(O/'raw').mkdir(parents=True,exist_ok=False);source=H/(stem+'-gray.blend');bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;objects=[o for o in bpy.data.objects if o.type=='MESH'];check=runpy.run_path(str(R/'tools/blender_component_camera_preflight.py'))['check_component_camera'];plan=json.loads((B/'detail-plan.json').read_text());s.world=bpy.data.worlds.new('Detail neutral studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.2,.2,.2,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.5
cam=bpy.data.objects.new('Detail review',bpy.data.cameras.new('Detail review'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.clip_start=.00001;cam.data.clip_end=100
s.render.engine='CYCLES';s.cycles.samples=96 if quality=='final'else 24;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';rows=[]
for view in plan['views']:
 for ob in list(bpy.data.objects):
  if ob.type=='LIGHT':bpy.data.objects.remove(ob,do_unlink=True)
 target=Vector(view['target']);scale=view['scale']
 for name,direction,power,ls in [('KEY',(-1,-1,2),500,.9),('FILL',(1,2,1),250,.9),('RIM',(0,-2,.5),150,.6)]:
  d=bpy.data.lights.new(name,'AREA');d.energy=power*scale*scale;d.size=scale*ls;ob=bpy.data.objects.new(name,d);s.collection.objects.link(ob);ob.location=target+scale*Vector(direction);ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
 if view.get('reflection'):
  mat=bpy.data.materials.new('RAM diagnostic reflection');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.3,.3,.3,1);p.inputs['Metallic'].default_value=.8;p.inputs['Roughness'].default_value=.12
  for ob in objects:ob.data.materials.clear();ob.data.materials.append(mat)
 cam.data.ortho_scale=scale;cam.location=target+scale*Vector(view['direction']);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.view_layers[0].update();preflight=check(s,objects,allow_crop=True);name=view['name'];exr=O/'raw'/(name+'.exr');png=O/(name+'.png');s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(exr);bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(png),scene=s);rows.append({**view,'samples':s.cycles.samples,'camera':list(cam.location),'camera_preflight':preflight,'PNG':str(png.relative_to(R)),'EXR':str(exr.relative_to(R))});(O/'render-report.json').write_text(json.dumps({'source':str(source.relative_to(R)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'protocol':'tools/front_completion_front10_detail_v1.py','views':rows,'art_accepted':False},indent=2))
