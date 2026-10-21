"""Hash-bound source renders, checkpoints after every complete view; estimated poses."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/fork-bellows-v1';a=json.loads((OUT/'source-geometry-check.json').read_text());b=json.loads((OUT/'geometry-check.json').read_text());assert a['source_sha256']==hashlib.sha256((HERE/'fork-bellows-v1.blend').read_bytes()).hexdigest();assert a['export_sha256']==b['sha256']==hashlib.sha256((HERE/'fork-bellows-inspection.glb').read_bytes()).hexdigest() and b['technical_passed'];bpy.ops.wm.open_mainfile(filepath=str(HERE/'fork-bellows-v1.blend'));s=bpy.context.scene;o=bpy.data.collections['WEWA_FORK_BELLOWS_ISOLATED'].objects[0];preview='--preview' in sys.argv;s.cycles.samples=24 if preview else 96;s.render.resolution_percentage=50 if preview else 100
views={'quarter':((.14,.22,.14),(0,0,.0625),.18,[0,0]),'lower-opening':((.07,.09,-.075),(0,0,.010),.080,[0,0]),'compression-estimated':((.14,.22,.14),(0,0,.0625),.18,[1,0]),'extension-estimated':((.14,.22,.14),(0,0,.0625),.18,[0,1])};report={'source_sha256':a['source_sha256'],'export_sha256':b['sha256'],'renderer':'Blender4.3.2 Cycles CPU OpenImageDenoise','samples':96,'resolution_px':[1000,1200],'views':[],'manufacturer_travel_verified':False,'art_accepted':False}
for name,(location,target,scale,weights) in views.items():
 if any(a.startswith('--view=') for a in sys.argv) and '--view='+name not in sys.argv:continue
 for i,w in enumerate(weights):o.data.shape_keys.key_blocks[i+1].value=w
 bpy.context.view_layer.update();s.camera.location=location;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=scale;s.render.filepath='/tmp/wewa-bellows-'+name+'.png' if preview else str(OUT/(name+'.png'));view={'name':name,'camera_location_m':list(location),'camera_target_m':list(target),'ortho_scale_m':scale,'morph_weights':weights};config={'source_sha256':report['source_sha256'],'export_sha256':report['export_sha256'],'view':view,'samples':96,'resolution_px':[1000,1200]};config_sha=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest();cp=OUT/('checkpoint-'+name+'.json');png=OUT/(name+'.png');reuse=False
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
