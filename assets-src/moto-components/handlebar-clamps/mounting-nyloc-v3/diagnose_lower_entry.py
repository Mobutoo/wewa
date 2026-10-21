"""Read-only native-resolution crop: compare lower thread entry with/without OIDN."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/handlebar-mount-nyloc-v3/lower-entry-diagnostic';OUT.mkdir(exist_ok=True);source=HERE/'handlebar-mount-nyloc-v3.blend';export=HERE/'handlebar-mount-nyloc-v3-inspection.glb'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ss,es=sha(source),sha(export);expected=json.loads((ROOT/'creative/reviews/handlebar-mount-nyloc-v3/source-geometry-check.json').read_text());assert ss==expected['source_sha256']and es==expected['export_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.camera.location=(.030,.033,-.026);s.camera.rotation_euler=(Vector((0,0,.004))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=.029;s.render.resolution_percentage=100;s.cycles.samples=96;s.cycles.seed=0;bpy.context.view_layer.update();sys.path.insert(0,str(ROOT/'tools'));from blender_component_camera_preflight import check_component_camera
preflight=check_component_camera(s,list(bpy.data.collections['WEWA_HANDLEBAR_MOUNT_NYLOC_ISOLATED'].objects),allow_crop=True);s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=380/1200;s.render.border_max_x=830/1200;s.render.border_min_y=1-835/1000;s.render.border_max_y=1-620/1000
r={'source_sha256':ss,'export_sha256':es,'source_or_GLB_modified':False,'native_frame_px':[1200,1000],'requested_crop_top_left_box_px':[380,620,830,835],'camera':'Same underside-thread view as final; only border and denoising flag changed in RAM','samples':96,'seed':0,'material_light_exposure_gamma_unchanged':True,'camera_preflight':preflight,'views':[],'art_accepted':False}
for label,denoise in[('without-oidn',False),('with-oidn',True)]:
 s.cycles.use_denoising=denoise;p=OUT/(label+'.png');s.render.filepath=str(p);bpy.ops.render.render(write_still=True);r['views'].append({'name':label,'denoising':denoise,'PNG_sha256':sha(p),'PNG_bytes':p.stat().st_size});(OUT/'render-report.json').write_text(json.dumps(r,indent=2)+'\n')
assert sha(source)==ss and sha(export)==es;print('WEWA_LOWER_ENTRY_READ_ONLY',json.dumps(r))
