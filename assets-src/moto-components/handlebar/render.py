"""Actual source-hashed Blender views; no compositing with a generated target."""
import hashlib,json,argparse,sys
from pathlib import Path
import bpy
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/handlebar-v1'
parser=argparse.ArgumentParser();parser.add_argument('--samples',type=int,default=96);parser.add_argument('--views',default='quarter,cockpit,clamp-detail');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=HERE/'handlebar-v1.blend';check=json.loads((OUT/'source-geometry-check.json').read_text());gltf=json.loads((OUT/'geometry-check.json').read_text());assert check['source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest();assert gltf['technical_passed'] and gltf['sha256']==hashlib.sha256((HERE/'handlebar-inspection.glb').read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.cycles.samples=args.samples
views={'quarter':((.82,.92,.68),(0,.02,.05),60),'cockpit':((0,.54,.45),(0,.020,.04),32),'clamp-detail':((.16,.22,.24),(0,0,0),80),'front':((0,-1.45,.32),(0,0,.045),60),'top':((0,.045,1.4),(0,.045,0),55)}
report={'component_id':'MOTO-HANDLEBAR-001','source_sha256':check['source_sha256'],'export_sha256':gltf['sha256'],'actual_blender_source_render':True,'samples':args.samples,'resolution_px':[1400,900],'denoising':False,'scope':'Bare handlebar only; cockpit view is component inspection, not gameplay or complete driving controls','art_accepted':False,'views':[]}
for name in args.views.split(','):
 location,target,lens=views[name];scene.camera.location=location;scene.camera.rotation_euler=(Vector(target)-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.lens=lens;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True);report['views'].append({'name':name,'camera_location_m':location,'camera_target_m':target,'lens_mm':lens,'documentary_camera_calibrated':False})
(OUT/'render-report.json').write_text(json.dumps(report,indent=2)+'\n');print('WEWA_HANDLEBAR_RENDERS',len(report['views']))
