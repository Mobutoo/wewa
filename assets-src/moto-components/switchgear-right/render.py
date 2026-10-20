"""Render only the exact checked candidate; no source saved after rendering."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/switchgear-right-v1'
check=json.loads((OUT/'source-geometry-check.json').read_text());export=json.loads((OUT/'geometry-check.json').read_text())
source=HERE/'switchgear-right-v1.blend';assert check['source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest();assert not export['glTF_errors'];assert export['sha256']==hashlib.sha256((ROOT/export['file']).read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.view_layers[0].cycles.denoising_store_passes=True
I=Vector(check['datum']['inward_axis']);T=Vector(check['datum']['thumb_side_radial']);E=Vector(check['datum']['endpoint_m']);Z=Vector((0,0,1));target=E+I*.143+T*.002-Z*.008
views={'front':(target+T*.26,target,80),'quarter':(target+T*.21+Z*.10+I*.08,target,80),'underside':(target+T*.18-Z*.11-I*.08,target,80),'material-grazing':(target+T*.10+I*.05+Z*.015,target,80)}
report={'source_sha256':check['source_sha256'],'resolution_px':[1100,1000],'samples':96,'renderer_version':bpy.app.version_string,'renderer_build_hash':bpy.app.build_hash.decode(),'denoiser':'OPENIMAGEDENOISE CPU','noisy_and_denoising_passes_enabled':True,'actual_blender_renders':True,'views':[],'art_accepted':False}
# Floor does not occlude the underside inspection; lift/reposition only studio,
# never the source component used by the hash-bound geometric proof.
floor=next(o for o in bpy.data.collections['RH_SWITCH_STUDIO'].objects if o.type=='MESH')
for name,(location,look,lens) in views.items():
 floor.hide_render=name=='underside'
 key=bpy.data.objects['RH_KEY'];key.location=target+(I*.17+T*.025+Z*.01 if name=='material-grazing' else T*.18+Z*.26+I*.04);key.rotation_euler=(target-key.location).to_track_quat('-Z','Y').to_euler()
 s.camera.location=location;s.camera.rotation_euler=(look-location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=lens;s.render.image_settings.file_format='PNG';s.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True);report['views'].append({'name':name,'camera_location_m':list(location),'camera_target_m':list(look),'lens_mm':lens,'key_light_location_m':list(key.location)})
(OUT/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
