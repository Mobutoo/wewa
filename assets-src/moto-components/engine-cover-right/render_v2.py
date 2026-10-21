from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-cover-right-v2';source=H/'engine-cover-right-v2.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();check=json.loads((O/'source-geometry-check.json').read_text());export=json.loads((O/'export-check.json').read_text());assert sha(source)==check['source_sha256'];assert sha(H/'engine-cover-right-v2-inspection.glb')==export['sha256'];assert export['actual_geometry_identical_to_v1'] and not export['glTF_errors']
sys.path.insert(0,str(H));from render_checkpoint_v2 import checkpoint_view
from camera_preflight_v2 import check_component_camera
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.camera.data.clip_start=.001;body=bpy.data.objects['RH clutch cover hollow casting - editable candidate'];old=json.loads((R/'creative/reviews/engine-cover-right-v1/render-report.json').read_text());report={'source_sha256':sha(source),'export_sha256':export['sha256'],'samples':96,'denoising':'OpenImageDenoise','resolution_px':[1100,850],'actual_blender_render':True,'base_cameras_identical_to_v1':True,'guides_visible':False,'all_dimensions_estimated':True,'views':[],'art_accepted':False}
for view in old['views']:
 target=Vector(view['target_m']);s.camera.location=view['camera_m'];s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=view['lens_mm'];bpy.context.view_layer.update();frame=check_component_camera(s,[body],allow_crop=False);cp=checkpoint_view(s,O,source,view['name']);report['views'].append({'name':view['name'],'camera_m':list(s.camera.location),'target_m':list(target),'camera_preflight':frame,'checkpoint':view['name']+'.checkpoint.json','outputs':cp['outputs']})
(O/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
