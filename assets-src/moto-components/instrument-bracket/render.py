import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/instrument-bracket-v1';s=json.loads((OUT/'source-geometry-check.json').read_text());g=json.loads((OUT/'geometry-check.json').read_text());assert s['source_sha256']==hashlib.sha256((HERE/'instrument-bracket-v1.blend').read_bytes()).hexdigest() and g['technical_passed'];assert g['sha256']==hashlib.sha256((HERE/'instrument-bracket-inspection.glb').read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(HERE/'instrument-bracket-v1.blend'));scene=bpy.context.scene;preview='--preview' in sys.argv;scene.cycles.samples=24 if preview else 96
views={'front-quarter':((.10,-.16,.30),(0,-.05,0),50),'reverse-quarter':((-.13,-.16,-.30),(0,-.05,0),50)};report={'source_sha256':s['source_sha256'],'export_sha256':s['export_sha256'],'actual_blender_render':True,'samples':96,'denoiser':'OpenImageDenoise official Blender4.3.2 CPU','resolution_px':[1200,1000],'art_accepted':False,'views':[]}
for name,(location,target,lens) in views.items():
 if preview and name!='front-quarter':continue
 scene.camera.location=location;scene.camera.rotation_euler=(Vector(target)-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.lens=lens;scene.render.filepath='/tmp/wewa-bracket-preview.png' if preview else str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True);report['views'].append({'name':name,'camera_location_m':location,'camera_target_m':target,'lens_mm':lens})
if not preview:(OUT/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
