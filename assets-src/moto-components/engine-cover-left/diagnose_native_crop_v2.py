"""Read-only numerical source diagnosis: native-view border, OIDN/no OIDN.
The border and denoising state are recorded per crop. No image resizing or repair.
"""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Matrix
H=Path(__file__).resolve().parent;R=H.parents[2];source=H/'engine-cover-left-v2.blend';glb=H/'engine-cover-left-v2-inspection.glb';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();ss=sha(source);es=sha(glb);base=Path('/workspace/wewa-assets/work-in-progress/engine-cover-left-v2')/ss[:12];parent=base/'preview/front-fixation-transition.checkpoint.json';cp=json.loads(parent.read_text());assert cp['source_sha256']==ss;O=base/'native-border-diagnostic';O.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.camera.matrix_world=Matrix(cp['configuration']['camera_world_matrix']);s.camera.data.lens=cp['configuration']['lens_mm'];s.camera.data.clip_start=.001;s.render.resolution_x=850;s.render.resolution_y=700;s.render.resolution_percentage=100;s.cycles.samples=32;s.cycles.seed=0;s.render.use_border=True;s.render.use_crop_to_border=True;bpy.context.view_layer.update();report={'source_sha256':ss,'export_sha256':es,'source_not_modified':True,'native_frame_px':[850,700],'parent_view_checkpoint_sha256':sha(parent),'driver_sha256':sha(__file__),'camera_and_lights_unchanged_from_parent_checkpoint':True,'samples':32,'views':[],'art_accepted':False}
for name,box in [('upper-mark',[350,180,520,300]),('lower-groove',[250,410,380,650])]:
 s.render.border_min_x=box[0]/850;s.render.border_max_x=box[2]/850;s.render.border_min_y=1-box[3]/700;s.render.border_max_y=1-box[1]/700
 for denoise in [False,True]:
  label=name+('-oidn'if denoise else'-raw');s.cycles.use_denoising=denoise;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;bpy.ops.render.render(write_still=False);image=bpy.data.images['Render Result'];outputs=[]
  for fmt,ext,depth in [('OPEN_EXR','exr','16'),('PNG','png','8')]:
   s.render.image_settings.file_format=fmt;s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth=depth
   if fmt=='OPEN_EXR':s.render.image_settings.exr_codec='ZIP'
   p=O/(label+'.'+ext);image.save_render(str(p),scene=s);outputs.append({'file':p.name,'sha256':sha(p),'bytes':p.stat().st_size,'linear_scene_data':fmt=='OPEN_EXR'})
  entry={'view':label,'source_sha256':ss,'export_sha256':es,'configuration':dict(report,parent_configuration=cp['configuration'],border_top_left_box_px=box,denoising=denoise,seed=0),'outputs':outputs,'complete':True};entry['configuration'].pop('views');(O/(label+'.checkpoint.json')).write_text(json.dumps(entry,indent=2)+'\n');report['views'].append({'name':label,'border_top_left_box_px':box,'denoising':denoise,'outputs':outputs});(O/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
assert sha(source)==ss and sha(glb)==es
