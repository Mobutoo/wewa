"""One rendered view is attributable independently of an interrupted later view.
Checkpoints bind immutable source, effective scene configuration, linear EXR and PNG.
"""
from pathlib import Path
import json,hashlib,os
import bpy

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def atomic_json(p,data):
 p=Path(p);tmp=p.with_name(p.name+'.partial');tmp.write_text(json.dumps(data,indent=2)+'\n');os.replace(tmp,p)
def checkpoint_view(scene,out,source,name):
 out=Path(out);out.mkdir(exist_ok=True,parents=True);source=Path(source);bpy.context.view_layer.update()
 config={'frame':scene.frame_current,'renderer':scene.render.engine,'samples':scene.cycles.samples,'denoising':scene.cycles.use_denoising,'denoiser':scene.cycles.denoiser,'resolution':[scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage],'camera_world_matrix':[list(r) for r in scene.camera.matrix_world],'lens_mm':scene.camera.data.lens,'sensor_width_mm':scene.camera.data.sensor_width,'view':{'transform':scene.view_settings.view_transform,'look':scene.view_settings.look,'exposure':scene.view_settings.exposure,'gamma':scene.view_settings.gamma},'lights':[{'name':o.name,'energy':o.data.energy,'size':o.data.size,'matrix':[list(r) for r in o.matrix_world]} for o in scene.objects if o.type=='LIGHT'],'hidden_render_objects':sorted(o.name for o in scene.objects if o.hide_render),'hidden_render_collections':sorted(c.name for c in bpy.data.collections if c.hide_render),'protocol_sha256':sha(__file__)}
 signature=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest();checkpoint=out/(name+'.checkpoint.json');source_sha=sha(source)
 if checkpoint.exists():
  previous=json.loads(checkpoint.read_text())
  if previous['source_sha256']==source_sha and previous['configuration_sha256']==signature and all((out/f['file']).exists() and sha(out/f['file'])==f['sha256'] for f in previous['outputs']):
   print('WEWA_VIEW_RESUME_SKIP',name,flush=True);return previous
 scene.cycles.use_denoising=True;scene.cycles.denoiser='OPENIMAGEDENOISE';scene.cycles.denoising_use_gpu=False
 bpy.ops.render.render(write_still=False);image=bpy.data.images['Render Result'];outputs=[]
 for fmt,ext,depth in [('OPEN_EXR','exr','16'),('PNG','png','8')]:
  scene.render.image_settings.file_format=fmt;scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth=depth
  if fmt=='OPEN_EXR':scene.render.image_settings.exr_codec='ZIP'
  destination=out/(name+'.'+ext);tmp=out/(name+'.partial.'+ext);image.save_render(str(tmp),scene=scene);os.replace(tmp,destination)
  outputs.append({'file':destination.name,'format':fmt,'bytes':destination.stat().st_size,'sha256':sha(destination),'linear_scene_data':fmt=='OPEN_EXR'})
 result={'schema':'wewa.single-view-checkpoint.v1','view':name,'source_file':str(source),'source_sha256':source_sha,'configuration_sha256':signature,'configuration':config,'outputs':outputs,'complete':True,'art_accepted':False};atomic_json(checkpoint,result);print('WEWA_VIEW_CHECKPOINT',name,source_sha,flush=True);return result
