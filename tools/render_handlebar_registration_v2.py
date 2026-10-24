"""Native comparison views of the registration, with identical camera and lighting."""
import hashlib
import json
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'creative/reviews/handlebar-registration-v2'
SOURCE = ROOT / 'assets-src/moto-components/handlebar-registration-v2/registration-context.blend'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


before = sha(SOURCE)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene = bpy.context.scene
objects = [o for o in scene.objects if o.name.startswith('Handlebar clamp ')]
assert len(objects) == 8
positions = {o.name: o.location.copy() for o in objects}
target = Vector((0, -.0975, -.025))
views = []
(OUT / 'raw').mkdir(exist_ok=True)
for angle, position in [('underside', (.17, .17, -.15)), ('top', (.12, -.32, .36))]:
    scene.camera.location = position
    scene.camera.rotation_euler = (target - scene.camera.location).to_track_quat('-Z', 'Y').to_euler()
    scene.camera.data.ortho_scale = .28
    for state in ['before', 'candidate']:
        for obj in objects:
            obj.location = positions[obj.name]
            if state == 'before':
                obj.location.x += .0065 if ' clamp L ' in obj.name else -.0065
        bpy.context.view_layer.update()
        name = 'native-' + angle + '-' + state
        exr = OUT / 'raw' / (name + '.exr')
        png = OUT / (name + '.png')
        scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
        scene.render.image_settings.color_depth = '32'
        scene.render.filepath = str(exr)
        bpy.ops.render.render(write_still=True)
        scene.render.image_settings.file_format = 'PNG'
        scene.render.image_settings.color_depth = '8'
        bpy.data.images['Render Result'].save_render(str(png), scene=scene)
        views.append({'name': name, 'camera_eye_blender_m': list(position),
                      'camera_target_blender_m': list(target), 'ortho_width_m': .28,
                      'samples': scene.cycles.samples, 'denoised': False,
                      'png_sha256': sha(png), 'exr_sha256': sha(exr)})
assert sha(SOURCE) == before
(OUT / 'native-render-check.json').write_text(json.dumps({
    'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': before,
    'tool_sha256': sha(Path(__file__)), 'views': views, 'art_accepted': False,
    'scope': 'Same-camera native geometry/reflection comparison. Handlebar ends outside close framing; all eight clamp parts and plate are the review subject.'
}, indent=2) + '\n')
print('REGISTRATION_NATIVE_VIEWS', len(views), flush=True)
