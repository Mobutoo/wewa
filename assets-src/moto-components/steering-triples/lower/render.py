import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/steering-lower-v1';s=json.loads((OUT/'source-geometry-check.json').read_text());g=json.loads((OUT/'geometry-check.json').read_text());assert s['source_sha256']==hashlib.sha256((HERE/'steering-lower-v1.blend').read_bytes()).hexdigest() and g['technical_passed'];assert g['sha256']==hashlib.sha256((HERE/'steering-lower-inspection.glb').read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(HERE/'steering-lower-v1.blend'));scene=bpy.context.scene;preview='--preview' in sys.argv;scene.cycles.samples=24 if preview else 96;scene.render.resolution_percentage=50 if preview else 100
views={'upper-quarter':((.13,-.21,.23),(0,.025,0),.28),'underside-ribs':((-.13,-.18,-.24),(0,.025,0),.28)};report={'source_sha256':s['source_sha256'],'export_sha256':s['export_sha256'],'actual_blender_render':True,'samples':96,'denoiser':'OpenImageDenoise official Blender4.3.2 CPU','resolution_px':[1200,1000],'art_accepted':False,'views':[]}
for name,(location,target,scale) in views.items():
 scene.camera.location=location;scene.camera.rotation_euler=(Vector(target)-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.type='ORTHO';scene.camera.data.ortho_scale=scale;scene.render.filepath='/tmp/wewa-lower-'+name+'.png' if preview else str(OUT/(name+'.png'));view={'name':name,'camera_location_m':list(location),'camera_target_m':list(target),'ortho_scale_m':scale};config={'source_sha256':report['source_sha256'],'export_sha256':report['export_sha256'],'view':view,'samples':96,'resolution_px':[1200,1000]};config_sha=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest();cp=OUT/('checkpoint-'+name+'.json');png=OUT/(name+'.png');reuse=False
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
