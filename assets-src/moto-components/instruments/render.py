"""Render the checked saved candidate and explicit speed/fuel poses."""
import bpy,sys,math,json,hashlib,argparse
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/instruments-v1'
pa=argparse.ArgumentParser();pa.add_argument('--report-name',default='render-report.json');pa.add_argument('--denoise',action='store_true');pa.add_argument('--samples',type=int,default=128);pa.add_argument('--views',default='front,quarter,rear,driver-42');pa.add_argument('--resolution',type=int,default=1400);args=pa.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
check=json.loads((OUT/'source-geometry-check.json').read_text());gltf=json.loads((OUT/'geometry-check.json').read_text());source=HERE/'instruments-v1.blend'
assert check['source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest() and gltf['glTF_errors']==0
assert gltf['sha256']==hashlib.sha256((HERE/'instruments-inspection.glb').read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.cycles.samples=args.samples;scene.cycles.use_denoising=args.denoise
raw=None
if args.denoise:
 scene.cycles.denoiser='OPENIMAGEDENOISE';scene.cycles.denoising_use_gpu=False;scene.view_layers[0].cycles.denoising_store_passes=True
 scene.use_nodes=True;tree=scene.node_tree;tree.nodes.clear();layer=tree.nodes.new('CompositorNodeRLayers');composite=tree.nodes.new('CompositorNodeComposite');tree.links.new(layer.outputs['Image'],composite.inputs['Image'])
 raw=tree.nodes.new('CompositorNodeOutputFile');raw.base_path='/workspace/wewa-assets/render-raw/instruments-v1';raw.format.file_format='OPEN_EXR';raw.format.color_depth='16';raw.format.color_mode='RGBA';raw.format.exr_codec='ZIP';tree.links.new(layer.outputs['Noisy Image'],raw.inputs[0])
 Path(raw.base_path).mkdir(parents=True,exist_ok=True)
scene.render.resolution_x=args.resolution;scene.render.resolution_y=round(args.resolution/1.4);scene.render.image_settings.file_format='PNG'
centre=Vector((0,-.12,.075));normal=Vector((0,math.sin(math.radians(58)),math.cos(math.radians(58))))
views={'front':(centre+normal*.65,centre,70,0),'quarter':(Vector((.25,.30,.37)),centre,70,0),'rear':(Vector((0,-.65,.10)),centre,70,0),'driver':(Vector((0,.36,.36)),Vector((0,-.12,.085)),60,0),'driver-42':(Vector((0,.36,.36)),Vector((0,-.12,.085)),60,42)}
report={'source_sha256':check['source_sha256'],'samples':args.samples,'denoising':args.denoise,'blender_version':bpy.app.version_string,'resolution_px':[scene.render.resolution_x,scene.render.resolution_y],'actual_blender_render':True,'art_accepted':False,'views':[]}
for name in args.views.split(','):
 location,target,lens,speed=views[name];scene.camera.location=location;scene.camera.rotation_euler=(target-location).to_track_quat('-Z','Y').to_euler();scene.camera.data.lens=lens
 bpy.data.objects['SPEED_NEEDLE_PIVOT'].rotation_euler.z=math.radians(225-speed*270/140)
 scene.render.filepath=str(OUT/(name+'.png'));
 if raw:raw.file_slots[0].path=name+'-raw-'
 bpy.ops.render.render(write_still=True)
 report['views'].append({'name':name,'camera_location_m':list(location),'camera_target_m':list(target),'lens_mm':lens,'speed_kmh':speed,'fuel_fraction':.65,'pose_changes_saved_to_source':False})
if raw:
 for row in report['views']:
  hdr=Path(raw.base_path)/(row['name']+'-raw-0001.exr');assert hdr.is_file(),hdr;row['raw_linear_hdr']={'private_path':str(hdr),'sha256':hashlib.sha256(hdr.read_bytes()).hexdigest(),'bytes':hdr.stat().st_size,'in_public_repo':False}
(OUT/args.report_name).write_text(json.dumps(report,indent=2)+'\n')
