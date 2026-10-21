"""Hash-bound component renders; short neutral/reflection diagnostics precede96."""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/frame-front-downmember-v1';sys.path.insert(0,str(ROOT/'tools'))
from blender_component_camera_preflight import check_component_camera
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((OUT/'source-geometry-check.json').read_text());b=json.loads((OUT/'geometry-check.json').read_text());assert a['source_sha256']==sha(HERE/'frame-front-downmember-v1.blend');assert a['export_sha256']==b['sha256']==sha(HERE/'frame-front-downmember-inspection.glb')and b['technical_passed']
bpy.ops.wm.open_mainfile(filepath=str(HERE/'frame-front-downmember-v1.blend'));s=bpy.context.scene;objects=list(bpy.data.collections['WEWA_FRAME_FRONT_DOWNMEMBER_ISOLATED'].objects);preview='--preview'in sys.argv;reflection='--reflection'in sys.argv;assert not reflection or preview
s.cycles.samples=24 if preview else 96;s.render.resolution_percentage=50 if preview else 100
# Component-specific neutral fixture, recorded in every configuration.
# Keep darkcoating intact; a compact key preserves darkareas and speculargrain.
for name,loc,energy,size in [('KEY',(.35,.14,-.42),.7,.08),('FILL',(-.32,.25,-.10),2,.28),('EDGE',(.12,-.16,-.36),2,.30)]:
 light=bpy.data.objects.get(name);light.hide_render=False;light.location=loc;light.rotation_euler=(Vector((0,.15,-.23))-light.location).to_track_quat('-Z','Y').to_euler();light.data.energy=energy;light.data.shape='DISK';light.data.size=size
if reflection:
 s.render.resolution_percentage=100
 m=bpy.data.materials.new('RAM-only diagnostic reflection - not finalfinish');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.30,.32,.35,1);p.inputs['Metallic'].default_value=.85;p.inputs['Roughness'].default_value=.08
 for o in objects:o.data.materials.clear();o.data.materials.append(m)
 s.world.node_tree.nodes['Background'].inputs[1].default_value=.08
 for o in bpy.data.collections['STUDIO_NOT_EXPORTED'].objects:
  if o.type=='LIGHT':o.data.shape='RECTANGLE';o.data.size=.5;o.data.size_y=.035
# RAM-only grazing strip for this inclined member: oldstudio key did not
# reflect into the diagnosticcamera, so a darkplane was not useful evidence.
if reflection:
 for light in bpy.data.collections['STUDIO_NOT_EXPORTED'].objects:
  if light.type=='LIGHT':
   light.hide_render=light.name!='KEY'
   if light.name=='KEY':
    light.location=(.30,.15,-.45);light.rotation_euler=(Vector((.020,.195,-.31))-light.location).to_track_quat('-Z','Y').to_euler();light.data.energy=4;light.data.size=.30;light.data.size_y=.035
fixture={'lights':[{'name':x.name,'location_m':list(x.location),'rotation_euler':list(x.rotation_euler),'power_W':x.data.energy,'shape':x.data.shape,'size_m':x.data.size,'size_y_m':x.data.size_y,'hide_render':x.hide_render}for x in bpy.data.collections['STUDIO_NOT_EXPORTED'].objects if x.type=='LIGHT'],'world_color':list(s.world.node_tree.nodes['Background'].inputs[0].default_value),'world_strength':s.world.node_tree.nodes['Background'].inputs[1].default_value,'source_geometry_or_material_modified':False}
render_script_sha256=sha(Path(__file__))
views={'quarter':((.65,.05,.05),(0,.125,-.20),.70,False),'reverse':((-.65,.30,.04),(0,.125,-.20),.70,False),'side-openings':((.16,.23,-.24),(.020,.195,-.31),.17,True),'lower-opening':((.10,.37,-.44),(0,.248,-.397),.105,True)}
report={'source_sha256':a['source_sha256'],'export_sha256':b['sha256'],'renderer':'Blender4.3.2 CyclesCPU OIDN','samples':96,'resolution_px':[1400,900],'views':[],'art_accepted':False}
for name,(location,target,scale,crop)in views.items():
 if any(v.startswith('--view=')for v in sys.argv)and'--view='+name not in sys.argv:continue
 s.camera.location=location;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;bpy.context.view_layer.update();preflight=check_component_camera(s,objects,allow_crop=crop);preflight['helper_sha256']=sha(ROOT/'tools/blender_component_camera_preflight.py')
 view={'name':name,'camera_location_m':list(location),'camera_target_m':list(target),'ortho_scale_m':scale,'allow_deliberate_macro_crop':crop,'camera_preflight':preflight};config={'studio_fixture':fixture,'render_script_sha256':render_script_sha256,'source_sha256':a['source_sha256'],'export_sha256':b['sha256'],'view':view,'samples':96,'resolution_px':[1400,900]};config_sha=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest();cp=OUT/('checkpoint-'+name+'.json');png=OUT/(name+'.png');reuse=False
 if not preview and cp.exists()and png.exists():
  prior=json.loads(cp.read_text());reuse=prior.get('config_sha256')==config_sha and prior.get('PNG_sha256')==sha(png)
 s.render.filepath='/tmp/wewa-frame-downmember-'+('reflection-'if reflection else'')+name+'.png'if preview else str(png)
 if not reuse:bpy.ops.render.render(write_still=True)
 if preview:
  p=Path(s.render.filepath);p.with_suffix('.json').write_text(json.dumps({'studio_fixture':fixture,'render_script_sha256':render_script_sha256,'source_sha256':a['source_sha256'],'export_sha256':b['sha256'],'samples':s.cycles.samples,'resolution_percentage':s.render.resolution_percentage,'reflection_override':reflection,'view':view,'PNG_sha256':sha(p)},indent=2)+'\n')
 if not preview:
  checkpoint={**config,'config_sha256':config_sha,'PNG_sha256':sha(png),'PNG_bytes':png.stat().st_size,'EXR_saved':False,'art_accepted':False}
  if not reuse:
   temp=cp.with_suffix('.tmp');temp.write_text(json.dumps(checkpoint,indent=2)+'\n');temp.replace(cp)
  view['PNG_sha256']=sha(png);view['checkpoint_file']=cp.name;view['reused_verified_checkpoint']=reuse
 report['views'].append(view)
if not preview:(OUT/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
