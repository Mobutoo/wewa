"""Finish only the study whole-view after the original camera preflight refused it.

The four existing macro images/checkpoints and their recipe are unchanged.
No final96, no source-save, no geometry/material modification.
"""
from pathlib import Path
import hashlib,json,sys
import bpy
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/front-tyre-v2';sys.path.insert(0,str(H))
from camera_preflight import check_component_camera
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads((O/'comparison-render-report.json').read_text());build=json.loads((O/'material-build-report.json').read_text())
assert len(report['views'])==4 and all(q['samples']==24 for q in report['views'])
source=H/'front-tyre-v2.blend';glb=H/'front-tyre-v2-inspection.glb';assert sha(source)==build['source_sha256']and sha(glb)==build['export_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;o=bpy.data.collections['WEWA_FRONT_TYRE_V2_UNCHANGED_INSPECTION'].objects[0]
s.cycles.samples=24;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
eye=(.7,-.9,.65);target=(0,0,.29);scale=.77
s.camera.location=eye;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale
bpy.context.view_layer.update();pre=check_component_camera(s,[o],allow_crop=False,margin=.005)
png=O/'compare-atlas-whole-quarter.png';s.render.filepath=str(png);bpy.ops.render.render(write_still=True)
q={k:report[k]for k in['source_sha256','export_sha256','samples','resolution_px','exposure_EV','gamma','view_transform','look','world_color_linear','world_strength','lights']}
q.update(render_script_sha256=sha(Path(__file__)),kind='atlas',name='whole-quarter',camera_eye_m=eye,camera_target_m=target,ortho_scale_m=scale,allow_intentional_crop=False,camera_preflight=pre,source_saved=False)
q['config_signature']=hashlib.sha256(json.dumps(q,sort_keys=True).encode()).hexdigest();q['PNG_sha256']=sha(png);q['PNG_bytes']=png.stat().st_size
(O/'compare-atlas-whole-quarter.json').write_text(json.dumps(q,indent=2)+'\n')
report['views'].append(q);report['initial_macro_worker_exit_code']=1;report['initial_worker_failure']='Whole camera at ortho.72 failed preflight with yextent[-.00649,1.00649], before any whole PNG was rendered. Four preceding macro checkpoints remain valid.'
report['corrected_whole_worker_expected_exit_code']=0;report['corrected_whole_render_script_sha256']=sha(Path(__file__))
assert sha(source)==build['source_sha256']and sha(glb)==build['export_sha256']
(O/'comparison-render-report.json').write_text(json.dumps(report,indent=2)+'\n');print('TYRE_TRANSFER_STUDY_WHOLE_ONLY_FINISHED',flush=True)
