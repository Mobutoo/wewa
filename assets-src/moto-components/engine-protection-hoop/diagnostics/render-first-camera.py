"""Actual source isolated gray/reflection views, preflight and checkpointed finals."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-protection-hoop-v1';sys.path.insert(0,str(R/'tools'));from blender_component_camera_preflight import check_component_camera
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();src=H/'engine-protection-hoop-v1.blend';glb=H/'engine-protection-hoop-inspection.glb';a=json.loads((O/'source-geometry-check.json').read_text());b=json.loads((O/'geometry-check.json').read_text());assert a['source_sha256']==b['source_sha256']==sha(src)and a['export_sha256']==b['export_sha256']==sha(glb)and b['technical_passed'];bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;obs=list(bpy.data.collections['WEWA_ENGINE_PROTECTION_HOOP_TUBE_ISOLATED'].objects);final='--final'in sys.argv;reflection='--reflection'in sys.argv;material='--material-preview'in sys.argv;assert not final or not(reflection or material);s.cycles.samples=96 if final else 24;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100 if final or reflection or'--native'in sys.argv else 65
if reflection:
 s.view_settings.exposure=-1.3
 for ob in obs:
  m=bpy.data.materials.new('RAM reflection diagnostic only');m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.30,.32,.35,1);p.inputs['Metallic'].default_value=.8;p.inputs['Roughness'].default_value=.07;ob.data.materials.clear();ob.data.materials.append(m)
 for ob in bpy.data.collections['LOCAL_NEUTRAL_STUDIO_NOT_EXPORT'].objects:
  if ob.type=='LIGHT':ob.data.shape='RECTANGLE';ob.data.size=.65;ob.data.size_y=.025
views={'quarter':((.55,-.85,.4),(0,0,-.12),.65,False),'front':((0,-1,-.12),(0,0,-.12),.65,False),'reverse-quarter':((-.55,.85,.25),(0,0,-.12),.65,False),'bend-detail':((.42,-.16,.12),(.235,0,-.045),.13,True),'mouth-detail':((.10,-.07,-.20),(.07,-.008,-.255),.065,True),'terminal-lumen-detail':((.015,-.05,-.215),(.045,0,-.255),.065,True)}
def fixture():return{'render_script_sha256':sha(Path(__file__)),'exposure_EV':s.view_settings.exposure,'gamma':s.view_settings.gamma,'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,'world_color_linear':list(s.world.node_tree.nodes['Background'].inputs[0].default_value),'world_strength':s.world.node_tree.nodes['Background'].inputs[1].default_value,'lights':[{'name':ob.name,'location_m':list(ob.location),'rotation_rad':list(ob.rotation_euler),'power_W':ob.data.energy,'shape':ob.data.shape,'size_m':ob.data.size,'size_y_m':ob.data.size_y}for ob in bpy.data.collections['LOCAL_NEUTRAL_STUDIO_NOT_EXPORT'].objects if ob.type=='LIGHT']}
r={'source_sha256':sha(src),'export_sha256':sha(glb),'samples':96,'resolution_px':[1400,1000],'views':[],'art_accepted':False}
for name,(loc,target,scale,crop)in views.items():
 if any(x.startswith('--view=')for x in sys.argv)and'--view='+name not in sys.argv:continue
 s.camera.location=loc;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;bpy.context.view_layer.update();pre=check_component_camera(s,obs,allow_crop=crop);pre['helper_sha256']=sha(R/'tools/blender_component_camera_preflight.py');v={'name':name,'camera_location_m':loc,'target_m':target,'ortho_scale_m':scale,'allow_deliberate_macro_crop':crop,'camera_preflight':pre};config={'source_sha256':sha(src),'export_sha256':sha(glb),'view':v,'samples':s.cycles.samples,'resolution_px':[round(1400*s.render.resolution_percentage/100),round(1000*s.render.resolution_percentage/100)],'fixture':fixture()};digest=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest();prefix=''if final else'preview-'if material else'reflection-'if reflection else'gray-';png=O/(prefix+name+'.png');cp=O/('checkpoint-'+name+'.json');reuse=False
 if final and cp.exists()and png.exists():
  q=json.loads(cp.read_text());reuse=q.get('config_sha256')==digest and q.get('PNG_sha256')==sha(png)
 s.render.filepath=str(png)
 if not reuse:bpy.ops.render.render(write_still=True)
 if final:
  if not reuse:
   q={**config,'config_sha256':digest,'PNG_sha256':sha(png),'PNG_bytes':png.stat().st_size,'EXR_saved':False,'art_accepted':False};tmp=cp.with_suffix('.tmp');tmp.write_text(json.dumps(q,indent=2)+'\n');tmp.replace(cp)
  r['views'].append({**v,'PNG_sha256':sha(png),'checkpoint_file':cp.name,'reused_verified_checkpoint':reuse})
 else:png.with_suffix('.json').write_text(json.dumps({**config,'PNG_sha256':sha(png),'reflection_override':reflection,'material_preview':material,'art_accepted':False},indent=2)+'\n')
if final:(O/'render-report.json').write_text(json.dumps(r,indent=2)+'\n')
