"""Four frozen-source96 views, checkpoint each PNG and linear EXR; never save source."""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/front-tyre-v3';sys.path.insert(0,str(H));from camera_preflight import check_component_camera
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();freeze=json.loads((O/'source-freeze.json').read_text());assert all(sha(R/q['path'])==q['sha256']for q in freeze['files'])
b=json.loads((O/'material-build-report.json').read_text());read=json.loads((O/'material-preview-review.json').read_text());assert read['ready_for_final96']and read['source_sha256']==b['source_sha256'];source=H/'front-tyre-v3.blend';assert sha(source)==b['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;o=bpy.data.collections[b['collection']].objects[0]
s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';s.render.image_settings.color_mode='RGBA'
views=[('quarter',(.7,-.9,.65),(0,0,.29),.77,False),('reverse-quarter',(-.7,.9,.65),(0,0,.29),.77,False),('tread-detail',(.075,-.17,.69),(.012,-.1,.562),.05,True),('sidewall-detail',(.15,-.17,.52),(.035,-.12,.49),.04,True)]
fixture={'source_sha256':sha(source),'export_sha256':b['export_sha256'],'render_script_sha256':sha(Path(__file__)),'samples':96,'resolution_px':[1400,1100],'exposure_EV':s.view_settings.exposure,'gamma':s.view_settings.gamma,'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,'denoiser':'OPENIMAGEDENOISE','world_strength':s.world.node_tree.nodes['Background'].inputs['Strength'].default_value,'world_color_linear':list(s.world.node_tree.nodes['Background'].inputs['Color'].default_value),'lights':[{'name':x.name,'location_m':list(x.location),'rotation_rad':list(x.rotation_euler),'shape':x.data.shape,'power_W':x.data.energy,'size_m':x.data.size}for x in s.objects if x.type=='LIGHT']}
report={**fixture,'views':[],'status':'rendering','source_saved':False,'art_accepted':False}
for name,eye,target,scale,crop in views:
 assert sha(source)==b['source_sha256'];s.camera.location=eye;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;bpy.context.view_layer.update();pre=check_component_camera(s,[o],allow_crop=crop,margin=.005)
 config={**fixture,'name':name,'camera_eye_m':eye,'camera_target_m':target,'ortho_scale_m':scale,'allow_intentional_crop':crop,'camera_preflight':pre};signature=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest();png=O/(name+'.png');exr=O/(name+'.exr');cp=O/('checkpoint-'+name+'.json')
 if cp.exists():
  q=json.loads(cp.read_text());assert q['config_signature']==signature and sha(png)==q['PNG_sha256']and sha(exr)==q['EXR_sha256'];print('REUSED_VERIFIED_FINAL_VIEW',name,flush=True)
 else:
  s.render.filepath=str(png);bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.image_settings.exr_codec='ZIP';bpy.data.images['Render Result'].save_render(filepath=str(exr),scene=s);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8'
  q={**config,'config_signature':signature,'PNG_sha256':sha(png),'PNG_bytes':png.stat().st_size,'EXR_sha256':sha(exr),'EXR_bytes':exr.stat().st_size,'EXR_scope':'Linear32bit render result, PNG has stated AgX display transform','source_saved':False};cp.write_text(json.dumps(q,indent=2)+'\n')
 report['views'].append(q);(O/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
assert sha(source)==b['source_sha256'];report['status']='completed';(O/'render-report.json').write_text(json.dumps(report,indent=2)+'\n');print('FRONT_TYRE_V3_FOUR_FINALS_COMPLETE',flush=True)
