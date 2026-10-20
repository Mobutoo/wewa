"""Render immutable, source-hashed candidate only after source/export checks."""
import argparse,json,hashlib,sys
from pathlib import Path
import bpy
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/front-brake-lever-v1'
parser=argparse.ArgumentParser();parser.add_argument('--samples',type=int,default=96);parser.add_argument('--views',default='quarter,front,rear,head-detail');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=HERE/'front-brake-lever-v1.blend';check=json.loads((OUT/'source-geometry-check.json').read_text());gltf=json.loads((OUT/'geometry-check.json').read_text())
assert check['source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
assert check['connected_shells']==1 and not check['non_manifold_edges'] and not gltf['glTF_errors'] and gltf['technical_passed']
assert gltf['sha256']==hashlib.sha256((ROOT/gltf['file']).read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.cycles.samples=args.samples
views={'quarter':((.32,-.12,.14),(0,.002,.060),80),'front':((.33,0,.060),(0,.002,.060),80),'rear':((-.33,0,.060),(0,.002,.060),80),'head-detail':((.13,-.055,.148),(.001,0,.100),100)}
report={'source_sha256':check['source_sha256'],'samples':args.samples,'resolution_px':[1100,1100],'actual_blender_render':True,'art_accepted':False,'views':[]}
for name in args.views.split(','):
 location,target,lens=views[name];scene.camera.location=location;scene.camera.rotation_euler=(Vector(target)-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.lens=lens
 scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True);report['views'].append({'name':name,'location':location,'target':target,'lens_mm':lens})
(OUT/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
