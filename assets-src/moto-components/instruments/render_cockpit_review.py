"""Render immutable linked assembly after source hashes and interface preflight."""
import bpy,json,hashlib,sys,argparse
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/cockpit-v1'
pa=argparse.ArgumentParser();pa.add_argument('--denoise',action='store_true');pa.add_argument('--samples',type=int,default=128);pa.add_argument('--views',default='driver,quarter');args=pa.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=HERE.parent/'cockpit-review/cockpit-review-v1.blend';check=json.loads((OUT/'source-geometry-check.json').read_text());assert check['source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
for row in check['linked_components']:assert row['sha256']==hashlib.sha256((ROOT/row['source']).read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.cycles.samples=args.samples;scene.cycles.use_denoising=args.denoise
raw=None
if args.denoise:
 scene.cycles.denoiser='OPENIMAGEDENOISE';scene.cycles.denoising_use_gpu=False;scene.view_layers[0].cycles.denoising_store_passes=True
 scene.use_nodes=True;tree=scene.node_tree;tree.nodes.clear();layer=tree.nodes.new('CompositorNodeRLayers');composite=tree.nodes.new('CompositorNodeComposite');tree.links.new(layer.outputs['Image'],composite.inputs['Image'])
 raw=tree.nodes.new('CompositorNodeOutputFile');raw.base_path='/workspace/wewa-assets/render-raw/cockpit-v1';raw.format.file_format='OPEN_EXR';raw.format.color_depth='16';raw.format.color_mode='RGBA';raw.format.exr_codec='ZIP';tree.links.new(layer.outputs['Noisy Image'],raw.inputs[0])
 Path(raw.base_path).mkdir(parents=True,exist_ok=True)
views={'driver':((0,.67,.49),(0,-.03,.07),28),'quarter':((.75,.85,.65),(0,-.01,.07),45)};report={'source_sha256':check['source_sha256'],'actual_blender_render':True,'samples':args.samples,'denoising':args.denoise,'blender_version':bpy.app.version_string,'resolution_px':[1600,1000],'speed_kmh':42,'art_accepted':False,'views':[]}
for name in args.views.split(','):
 pos,target,lens=views[name];scene.camera.location=pos;scene.camera.rotation_euler=(Vector(target)-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.lens=lens;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/(name+'.png'));
 if raw:raw.file_slots[0].path=name+'-raw-'
 bpy.ops.render.render(write_still=True);report['views'].append({'name':name,'camera_location_m':pos,'camera_target_m':target,'lens_mm':lens})
if raw:
 for row in report['views']:
  hdr=Path(raw.base_path)/(row['name']+'-raw-0001.exr');assert hdr.is_file(),hdr;row['raw_linear_hdr']={'private_path':str(hdr),'sha256':hashlib.sha256(hdr.read_bytes()).hexdigest(),'bytes':hdr.stat().st_size,'in_public_repo':False}
(OUT/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
