"""Additional actual sides of the existing frozen native review; source is not saved."""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
K='whole-exterior-opposite-side-v1'
O=R/'creative/reviews'/K
O.mkdir(exist_ok=True)
raw=O/'raw'
raw.mkdir(exist_ok=True)
source=R/'assets-src/moto-components/whole-exterior-coverage-v11/whole-exterior-coverage-v11.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source_sha=sha(source)
bpy.ops.wm.open_mainfile(filepath=str(source))
s=bpy.context.scene
center=Vector((0,.35,-.35))
rows=[]
for name,eye in [('coverage-right',(-3.5,.35,-.15)),('coverage-front',(0,-3.5,-.15)),('coverage-back',(0,4,-.15))]:
 s.camera.location=eye
 s.camera.rotation_euler=(center-s.camera.location).to_track_quat('-Z','Y').to_euler()
 s.render.image_settings.file_format='OPEN_EXR_MULTILAYER'
 s.render.image_settings.color_depth='32'
 s.render.filepath=str(raw/(name+'.exr'))
 bpy.ops.render.render(write_still=True)
 s.render.image_settings.file_format='PNG'
 s.render.image_settings.color_depth='8'
 bpy.data.images['Render Result'].save_render(str(O/(name+'.png')),scene=s)
 rows.append(dict(name=name,camera_eye=list(eye),camera_target=list(center),resolution_px=[1280,900],samples=16,PNG_sha256=sha(O/(name+'.png')),EXR_sha256=sha(raw/(name+'.exr'))))
 (O/'render-report.json').write_text(json.dumps(dict(source=str(source.relative_to(R)),source_sha256=source_sha,source_unchanged=sha(source)==source_sha,views=rows,scope='Additional actual sides, unchanged88parent native gray scene; no art or fit acceptance',protocol_sha256=sha(Path(__file__)),art_accepted=False),indent=2)+'\n')
assert sha(source)==source_sha
print('OPPOSITE_SIDES_RENDERED')
