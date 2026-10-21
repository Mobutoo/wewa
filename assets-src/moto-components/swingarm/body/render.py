"""Actual component cameras, real-vertex preflight and per-view hash checkpoints.
Gray, reflection, no-shadow and material previews are RAM-only diagnostics.
"""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/swingarm-body-v1';sys.path.insert(0,str(R/'tools'))
from blender_component_camera_preflight import check_component_camera
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();base='--base'in sys.argv;reflection='--reflection'in sys.argv;no_shadow='--no-shadow'in sys.argv;final='--final'in sys.argv;material_preview='--material-preview'in sys.argv;assert not final or not(reflection or no_shadow or material_preview or base)
src=H/('swingarm-body-base-study.blend'if base else'swingarm-body-v1.blend');glb=H/('swingarm-body-base-study.glb'if base else'swingarm-body-v1-inspection.glb');proof=json.loads((O/('base-study-geometry-check.json'if base else'source-geometry-check.json')).read_text());buffers=json.loads((O/('base-study-buffer-check.json'if base else'geometry-check.json')).read_text());assert sha(src)==proof['source_sha256']and sha(glb)==proof['export_sha256']==buffers['sha256']and buffers['technical_passed'];bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;obs=[o for o in bpy.data.collections['WEWA_SWINGARM_BODY_ISOLATED'].objects if o.type=='MESH'];s.cycles.samples=96 if final else 24;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100 if final or'--native'in sys.argv else 65;s.view_settings.exposure=-.8
if no_shadow:
 for ob in obs:ob.visible_shadow=False
if reflection:
 s.view_settings.exposure=-1.6
 for o in obs:
  m=bpy.data.materials.new('RAM only reflection not final paint');m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(.30,.32,.35,1);b.inputs['Metallic'].default_value=.8;b.inputs['Roughness'].default_value=.09;o.data.materials.clear();o.data.materials.append(m)
 for ob in bpy.data.collections['LOCAL_NEUTRAL_STUDIO_NOT_EXPORT'].objects:
  if ob.type=='LIGHT':ob.data.shape='RECTANGLE';ob.data.size=.65;ob.data.size_y=.03
views={'quarter':((.65,.82,.68),(0,.27,0),.72,False),'reverse-quarter':((-.65,.82,-.55),(0,.27,0),.72,False),'upper':((0,.275,1),(0,.275,0),.88,False),'lower':((0,.275,-1),(0,.275,0),.88,False),'side':((1,.275,.015),(0,.275,.015),.65,False),'pivot-detail':((.26,-.16,.16),(.07,.035,0),.25,True),'slot-detail':((.30,.63,.15),(.11,.51,0),.15,True),'weld-detail':((-.222,.065,.524),(.094,.245,.012),.100,True),'return-detail':((-.180,.630,.293),(.045,.180,.008),.100,True)}
def fixture():
 return{'render_script_sha256':sha(Path(__file__)),'lights':[{'name':ob.name,'location_m':list(ob.location),'rotation_rad':list(ob.rotation_euler),'energy_W':ob.data.energy,'shape':ob.data.shape,'size_m':ob.data.size,'size_y_m':ob.data.size_y}for ob in bpy.data.collections['LOCAL_NEUTRAL_STUDIO_NOT_EXPORT'].objects if ob.type=='LIGHT'],'world_color_linear':list(s.world.node_tree.nodes['Background'].inputs[0].default_value),'world_strength':s.world.node_tree.nodes['Background'].inputs[1].default_value,'exposure_EV':s.view_settings.exposure,'gamma':s.view_settings.gamma,'view_transform':s.view_settings.view_transform,'look':s.view_settings.look}
report={'source_sha256':sha(src),'export_sha256':sha(glb),'renderer':'Blender4.3.2 CyclesCPU96 OIDN','samples':96,'resolution_px':[1400,1000],'views':[],'art_accepted':False}
for name,(loc,target,scale,crop)in views.items():
 if '--view='+name not in sys.argv:continue
 s.camera.location=loc;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;bpy.context.view_layer.update();pre=check_component_camera(s,obs,allow_crop=crop);pre['helper_sha256']=sha(R/'tools/blender_component_camera_preflight.py');v={'name':name,'camera_location_m':loc,'target_m':target,'ortho_scale_m':scale,'allow_deliberate_macro_crop':crop,'preflight':pre};prefix=''if final else'preview-'if material_preview else'reflection-'if reflection else'gray-no-shadow-'if no_shadow else'gray-';png=O/(('base-'if base else'')+prefix+name+'.png');s.render.filepath=str(png);config={'source_sha256':sha(src),'export_sha256':sha(glb),'view':v,'samples':s.cycles.samples,'resolution_px':[int(s.render.resolution_x*s.render.resolution_percentage/100),int(s.render.resolution_y*s.render.resolution_percentage/100)],'fixture':fixture()};cs=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest();cp=O/('checkpoint-'+name+'.json');reuse=False
 if final and cp.exists()and png.exists():
  old=json.loads(cp.read_text());reuse=old.get('config_sha256')==cs and old.get('PNG_sha256')==sha(png)
 if not reuse:bpy.ops.render.render(write_still=True)
 if final:
  if not reuse:
   checkpoint={**config,'config_sha256':cs,'PNG_sha256':sha(png),'PNG_bytes':png.stat().st_size,'EXR_saved':False,'art_accepted':False};tmp=cp.with_suffix('.tmp');tmp.write_text(json.dumps(checkpoint,indent=2)+'\n');tmp.replace(cp)
  report['views'].append({**v,'PNG_sha256':sha(png),'checkpoint_file':cp.name,'reused_verified_checkpoint':reuse})
 else:png.with_suffix('.json').write_text(json.dumps({**config,'partial_base_study':base,'name':name,'camera_location_m':loc,'target_m':target,'ortho_scale_m':scale,'PNG_sha256':sha(png),'samples':s.cycles.samples,'resolution_percentage':s.render.resolution_percentage,'source_shadow_rays_disabled_in_RAM_only':no_shadow,'exposure_EV':s.view_settings.exposure,'reflection_override':reflection,'material_preview':material_preview,'art_accepted':False},indent=2)+'\n')
if final:(O/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
