"""Actual native whole-bike composition checks, without changing the linked model."""
import hashlib
import json
from pathlib import Path
import bpy
from mathutils import Vector

R=Path(__file__).resolve().parents[1]
O=R/'creative/reviews/motorcycle-exterior-v5';(O/'raw').mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=R/'assets-src/moto-components/motorcycle-exterior-v5/motorcycle-exterior-v5.blend'
before=sha(source);bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=24;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=960;s.render.resolution_y=675;s.render.resolution_percentage=100
s.camera.data.type='ORTHO';s.camera.data.ortho_scale=2.9;s.camera.data.clip_start=.01;s.camera.data.clip_end=100
target=Vector((0,.35,-.35));views=[]
for name,eye in [('native-left-quarter',(2.9,-3,1)),('native-right-quarter',(-2.9,-3,1))]:
    s.camera.location=eye;s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler()
    s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(O/'raw'/f'{name}.exr');bpy.ops.render.render(write_still=True)
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/f'{name}.png'),scene=s)
    views.append({'view':name,'camera_eye_blender_m':list(eye),'camera_target_blender_m':list(target),'orthographic_width_m':2.9,'samples':24,'denoised':False,'purpose':'Whole composition; new child material closeups separately rendered at 96 samples','png_sha256':sha(O/f'{name}.png'),'exr_sha256':sha(O/'raw'/f'{name}.exr')})
assert before==sha(source)
(O/'native-render-report.json').write_text(json.dumps({'source':str(source.relative_to(R)),'source_sha256':before,'tool_sha256':sha(Path(__file__)),'views':views,'art_accepted':False},indent=2)+'\n')
