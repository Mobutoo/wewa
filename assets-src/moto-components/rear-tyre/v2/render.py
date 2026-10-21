"""Checked source views with real geometry camera preflight and hash checkpoints."""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/rear-tyre-v2';sys.path.insert(0,str(R/'tools'))
from blender_component_camera_preflight import check_component_camera
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();a=json.loads((O/'source-geometry-check.json').read_text());b=json.loads((O/'geometry-check.json').read_text());assert a['source_sha256']==sha(H/'rear-tyre-v2.blend') and a['export_sha256']==b['sha256']==sha(H/'rear-tyre-v2-inspection.glb') and b['technical_passed'];bpy.ops.wm.open_mainfile(filepath=str(H/'rear-tyre-v2.blend'));s=bpy.context.scene;objects=list(bpy.data.collections['WEWA_REAR_TYRE_ISOLATED'].objects);o=objects[0];preview='--preview'in sys.argv;reflection='--reflection'in sys.argv;assert not reflection or preview;s.cycles.samples=24 if preview else 96;s.render.resolution_percentage=100 if reflection or'--native-preview'in sys.argv else 50 if preview else 100
if '--gray'in sys.argv:
 assert preview
 m=bpy.data.materials.new('RAM neutral gray diagnostic');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.20,.21,.23,1);p.inputs['Roughness'].default_value=.3;o.data.materials.clear();o.data.materials.append(m)
if reflection:
 m=bpy.data.materials.new('RAM-only reflection diagnostic not final alloy finish');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.30,.32,.35,1);p.inputs['Metallic'].default_value=.85;p.inputs['Roughness'].default_value=.08;o.data.materials.clear();o.data.materials.append(m);s.world.node_tree.nodes['Background'].inputs[1].default_value=.08
 for x in bpy.data.collections['STUDIO_NOT_EXPORTED'].objects:
  if x.type=='LIGHT':x.data.shape='RECTANGLE';x.data.size=.50;x.data.size_y=.025
views={'quarter':((.65,.65,.30),(0,0,0),.70,False),'side':((.85,0,0),(0,0,0),.68,False),'rear-tread':((0,.85,.06),(0,0,0),.68,False),'tread-detail':((.14,.44,.30),(0,.23,.15),.12,True),'bead-opening':((.45,.30,.10),(0,0,0),.47,True)}
def fixture():return {'render_script_sha256':sha(Path(__file__)),'lights':[{'name':x.name,'location_m':list(x.location),'rotation_euler_rad':list(x.rotation_euler),'energy_W':x.data.energy,'shape':x.data.shape,'size_m':x.data.size,'size_y_m':x.data.size_y}for x in bpy.data.collections['STUDIO_NOT_EXPORTED'].objects if x.type=='LIGHT'],'world_color_linear':list(s.world.node_tree.nodes['Background'].inputs[0].default_value),'world_strength':s.world.node_tree.nodes['Background'].inputs[1].default_value,'exposure_EV':s.view_settings.exposure,'gamma':s.view_settings.gamma,'view_transform':s.view_settings.view_transform,'look':s.view_settings.look}
report={'source_sha256':a['source_sha256'],'export_sha256':b['sha256'],'renderer':'Blender4.3.2 CyclesCPU OIDN','samples':96,'resolution_px':[1200,1100],'views':[],'art_accepted':False}
for name,(loc,target,scale,crop)in views.items():
 if any(q.startswith('--view=')for q in sys.argv)and'--view='+name not in sys.argv:continue
 if preview and '--native-macros'in sys.argv:s.render.resolution_percentage=100 if crop else 50
 s.camera.location=loc;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;bpy.context.view_layer.update();pre=check_component_camera(s,objects,allow_crop=crop);pre['helper_sha256']=sha(R/'tools/blender_component_camera_preflight.py');v={'name':name,'camera_location_m':list(loc),'camera_target_m':list(target),'ortho_scale_m':scale,'allow_deliberate_macro_crop':crop,'camera_preflight':pre};config={'source_sha256':a['source_sha256'],'export_sha256':b['sha256'],'view':v,'samples':s.cycles.samples,'resolution_px':[int(1200*s.render.resolution_percentage/100),int(1100*s.render.resolution_percentage/100)],'fixture':fixture()};cs=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest();cp=O/('checkpoint-'+name+'.json');png=O/(name+'.png');reuse=False
 if not preview and cp.exists()and png.exists():
  old=json.loads(cp.read_text());reuse=old.get('config_sha256')==cs and old.get('PNG_sha256')==sha(png)
 s.render.filepath=str(O/(('gray-reflection-'if reflection else'gray-'if'--gray'in sys.argv else'preview-')+name+'.png'))if preview else str(png)
 if not reuse:bpy.ops.render.render(write_still=True)
 if preview:
  p=Path(s.render.filepath);p.with_suffix('.json').write_text(json.dumps({**config,'actual_samples':24,'actual_resolution_percentage':s.render.resolution_percentage,'reflection_override':reflection,'PNG_sha256':sha(p)},indent=2)+'\n')
 else:
  if not reuse:
   d={**config,'config_sha256':cs,'PNG_sha256':sha(png),'PNG_bytes':png.stat().st_size,'EXR_saved':False,'art_accepted':False};tmp=cp.with_suffix('.tmp');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(cp)
  v.update(PNG_sha256=sha(png),checkpoint_file=cp.name,reused_verified_checkpoint=reuse)
 report['views'].append(v)
if not preview:(O/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
