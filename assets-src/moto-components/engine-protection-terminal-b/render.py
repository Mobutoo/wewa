"""Actual separate B plate, checkpointed preview/final views; never saves source."""
from pathlib import Path
import bpy,json,hashlib,sys,numpy as np
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-protection-terminal-b-v1';sys.path.insert(0,str(H));from camera_preflight import check_component_camera
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();src=H/'engine-protection-terminal-b-v1.blend';glb=H/'engine-protection-terminal-b-inspection.glb';a=json.loads((O/'source-geometry-check.json').read_text());b=json.loads((O/'geometry-check.json').read_text());assert b['technical_passed']and a['source_sha256']==b['source_sha256']==sha(src)and a['export_sha256']==b['export_sha256']==sha(glb)
final='--final'in sys.argv
if final:
 frozen=json.loads((O/'source-freeze.json').read_text());assert all(sha(R/q['path'])==q['sha256']for q in frozen['files'])
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;obs=list(bpy.data.collections['WEWA_ENGINE_PROTECTION_TERMINAL_B_ISOLATED'].objects);centre=np.mean(np.array(a['bounds_m']),axis=0);shift=np.array(a['origin_shift_from_developed_mapping_m']);fold=np.array([0.,.0055,.025])-shift;lower=np.array([0.,0.,0.])-shift;s.cycles.samples=96 if final else 24;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100
views=[('quarter',centre+(.12,-.22,.10),centre,.14,False),('reverse-quarter',centre+(-.12,.22,.10),centre,.14,False),('doublebend-detail',fold+(.07,-.15,.07),fold,.045,True),('upper-bore-detail',np.array([.045,-.16,.035]),np.array([0.,0.,0.]),.035,True),('lower-envelope-detail',lower+(.045,-.16,.04),lower,.045,True)]
r={'source_sha256':sha(src),'export_sha256':sha(glb),'samples':s.cycles.samples,'views':[],'art_accepted':False}
for name,eye,target,scale,crop in views:
 if not final and name in ['reverse-quarter','lower-envelope-detail']:continue
 s.camera.location=eye;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;bpy.context.view_layer.update();pre=check_component_camera(s,obs,allow_crop=crop,margin=.005)
 config={'source_sha256':sha(src),'export_sha256':sha(glb),'render_script_sha256':sha(Path(__file__)),'name':name,'samples':s.cycles.samples,'resolution_px':[1400,1000],'camera_eye_m':list(eye),'camera_target_m':list(target),'ortho_scale_m':scale,'camera_preflight':pre,'exposure_EV':s.view_settings.exposure,'gamma':s.view_settings.gamma,'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,'world_color_linear':list(s.world.node_tree.nodes['Background'].inputs[0].default_value),'world_strength':s.world.node_tree.nodes['Background'].inputs[1].default_value,'lights':[{'name':o.name,'location_m':list(o.location),'rotation_rad':list(o.rotation_euler),'shape':o.data.shape,'power_W':o.data.energy,'size_m':o.data.size}for o in s.objects if o.type=='LIGHT']}
 digest=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest();png=O/((''if final else'preview-')+name+'.png');exr=O/(name+'.exr');cp=O/('checkpoint-'+name+'.json');reuse=False
 if final and png.exists()and exr.exists()and cp.exists():
  q=json.loads(cp.read_text());reuse=q.get('config_signature')==digest and q.get('PNG_sha256')==sha(png)and q.get('EXR_sha256')==sha(exr)
 if not reuse:
  s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.filepath=str(png);bpy.ops.render.render(write_still=True)
  if final:
   s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.image_settings.exr_codec='ZIP';bpy.data.images['Render Result'].save_render(str(exr),scene=s)
  q={**config,'config_signature':digest,'PNG_sha256':sha(png),'PNG_bytes':png.stat().st_size,'source_saved':False,'art_accepted':False}
  if final:q.update(EXR_sha256=sha(exr),EXR_bytes=exr.stat().st_size,EXR_scope='Linear32bit render result, PNG uses stated AgX')
  targetcp=cp if final else png.with_suffix('.json');tmp=targetcp.with_suffix('.tmp');tmp.write_text(json.dumps(q,indent=2)+'\n');tmp.replace(targetcp)
 r['views'].append({'name':name,'PNG_sha256':sha(png),'reused_verified_checkpoint':reuse});(O/('render-report.json'if final else'material-preview-report.json')).write_text(json.dumps(r,indent=2)+'\n')
assert sha(src)==a['source_sha256'];r['status']='completed';(O/('render-report.json'if final else'material-preview-report.json')).write_text(json.dumps(r,indent=2)+'\n');print('TERMINAL_B_VIEWS_EXIT0',flush=True)
