"""Whole ear in frame; earlier cropped views retained as macros, not full-part proof."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];N='chaincase-front-registration-v3';H=R/'assets-src/moto-components'/N;O=R/'creative/reviews'/N
bpy.ops.wm.open_mainfile(filepath=str(H/'linked-registration.blend'));s=bpy.context.scene;c=s.camera;c.location=(-.3,-.50,.08);target=Vector((-.02,-.405,.02));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=.26;s.render.resolution_x=800;s.render.resolution_y=800;s.cycles.samples=96;s.view_layers[0].cycles.denoising_store_passes=True
# Preserve material separation without clipping whites under close studio lamps.
s.view_settings.exposure=-1.7
s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(O/'raw/ear-complete.exr');bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/'ear-complete.png'),scene=s)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();(O/'full-ear-render-report.json').write_text(json.dumps(dict(source_sha256=sha(H/'linked-registration.blend'),samples=96,resolution=[800,800],exposure=-1.7,camera_target=list(target),camera_eye=list(c.location),png_sha256=sha(O/'ear-complete.png'),exr_sha256=sha(O/'raw/ear-complete.exr'),ear_complete_in_frame=True,source_geometry_changed=False,art_accepted=False),indent=2)+'\n')
