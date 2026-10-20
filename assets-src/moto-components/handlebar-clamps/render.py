import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/handlebar-clamps-v1';s=json.loads((OUT/'source-geometry-check.json').read_text());g=json.loads((OUT/'geometry-check.json').read_text());assert s['source_sha256']==hashlib.sha256((HERE/'handlebar-clamps-v1.blend').read_bytes()).hexdigest() and g['technical_passed'];assert g['sha256']==hashlib.sha256((HERE/'handlebar-clamps-inspection.glb').read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(HERE/'handlebar-clamps-v1.blend'));scene=bpy.context.scene;preview='--preview' in sys.argv or '--preview-detail' in sys.argv;scene.cycles.samples=24 if preview else 96;scene.render.resolution_percentage=50 if preview else 100;scene.render.image_settings.file_format='PNG';objects=list(bpy.data.collections['WEWA_HANDLEBAR_CLAMPS_SEPARATE_PARTS'].objects);original={o.name:o.location.copy() for o in objects}
views={'quarter':((.30,.32,.23),(0,0,-.015),70),'exploded':((.22,.25,.20),(.045,0,.012),70),'material-close':((.135,.13,.095),(.045,0,.003),90)};report={'export_sha256':s['export_sha256'],'source_sha256':s['source_sha256'],'samples':96,'denoiser':'OpenImageDenoise, official Blender4.3.2 CPU','resolution_px':[1200,900],'actual_blender_render':True,'art_accepted':False,'views':[]}
for name,(location,target,lens) in views.items():
 if not preview and name=='exploded':continue
 if preview and name!=('material-close' if '--preview-detail' in sys.argv else 'quarter'):continue
 for o in objects:
  o.hide_render=name in ['exploded','material-close'] and ' R ' in o.name;o.location=original[o.name].copy()
  if name=='exploded':
   if 'upper' in o.name:o.location.z+=.030
   elif 'bolt' in o.name:o.location.z+=.055
 scene.camera.location=location;scene.camera.rotation_euler=(Vector(target)-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.lens=lens;scene.render.filepath=('/tmp/wewa-clamps-preview-detail.png' if '--preview-detail' in sys.argv else '/tmp/wewa-clamps-preview.png') if preview else str(OUT/(name+'.png'));view={'name':name,'camera_location_m':list(location),'camera_target_m':list(target),'lens_mm':lens,'exploded_offsets_m':{'upper_z':.030,'bolt_z':.055} if name=='exploded' else None}
 config={'source_sha256':report['source_sha256'],'export_sha256':report['export_sha256'],'view':view,'samples':96,'resolution_px':[1200,900]};config_sha=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest();cp=OUT/('checkpoint-'+name+'.json');png=OUT/(name+'.png');reuse=False
 if not preview and cp.exists() and png.exists():
  prior=json.loads(cp.read_text());reuse=prior.get('config_sha256')==config_sha and prior.get('PNG_sha256')==hashlib.sha256(png.read_bytes()).hexdigest()
 if not reuse:bpy.ops.render.render(write_still=True)
 if not preview:
  checkpoint={**config,'config_sha256':config_sha,'PNG_sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'PNG_bytes':png.stat().st_size,'EXR_saved':False,'art_accepted':False}
  if not reuse:
   tmp=cp.with_suffix('.tmp');tmp.write_text(json.dumps(checkpoint,indent=2)+'\n');tmp.replace(cp)
  view['checkpoint_file']=cp.name;view['PNG_sha256']=checkpoint['PNG_sha256'];view['reused_verified_checkpoint']=reuse
 report['views'].append(view)
if not preview:(OUT/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
