"""Read-only extraction of the exact native preview camera, not photo calibration."""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--spec', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
a.spec = a.spec.resolve()
a.output = a.output.resolve()
spec = json.loads(a.spec.read_text())
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
assert not a.output.exists(), 'Use a new camera extraction'
for key in ['source', 'export', 'HDR']:
    assert sha(ROOT / spec[key]) == spec[key + '_sha256'], key
native = json.loads((ROOT / spec['output'] / 'report.json').read_text())
assert native['spec_sha256'] == sha(a.spec)
assert native['camera_type'] == 'PERSP' and spec['camera']['type'] == 'PERSP'
bpy.ops.wm.open_mainfile(filepath=str(ROOT / spec['source']))
scene = bpy.context.scene
view = spec['camera']
camera = bpy.data.objects.new('Read-only exact comparison camera', bpy.data.cameras.new('Exact comparison camera'))
scene.collection.objects.link(camera)
camera.location = view['location_m']
camera.rotation_euler = (Vector(view['target_m']) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'PERSP'
camera.data.lens = view['lens_mm']
camera.data.clip_start, camera.data.clip_end = .001, 100
scene.camera = camera
scene.render.resolution_x, scene.render.resolution_y = spec['resolution_px']
scene.render.resolution_percentage = 100
bpy.context.view_layer.update()
projection = camera.calc_matrix_camera(bpy.context.evaluated_depsgraph_get(), x=scene.render.resolution_x, y=scene.render.resolution_y,
                                       scale_x=scene.render.pixel_aspect_x, scale_y=scene.render.pixel_aspect_y)
def gltf(v):
    return [float(v[0]), float(v[2]), -float(v[1])]
objects = [o for o in bpy.data.collections[spec['collection']].all_objects if o.type == 'MESH' and not o.hide_render]
points = []
for obj in objects:
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    points.extend(evaluated.matrix_world @ vertex.co for vertex in mesh.vertices)
    evaluated.to_mesh_clear()
low = [min(p[i] for p in points) for i in range(3)]
high = [max(p[i] for p in points) for i in range(3)]
witnesses = []
for x in [low[0], high[0]]:
    for y in [low[1], high[1]]:
        for z in [low[2], high[2]]:
            point = Vector((x, y, z))
            projected = world_to_camera_view(scene, camera, point)
            witnesses.append({'gltf_world_m': gltf(point), 'native_pixel_xy': [projected.x * scene.render.resolution_x, (1 - projected.y) * scene.render.resolution_y]})
for key in ['source', 'export', 'HDR']:
    assert sha(ROOT / spec[key]) == spec[key + '_sha256'], key
record = {'schema': 'wewa.material-camera-comparison.v1', 'source': spec['source'], 'source_sha256': spec['source_sha256'],
          'export': spec['export'], 'export_sha256': spec['export_sha256'], 'HDR': spec['HDR'], 'HDR_sha256': spec['HDR_sha256'],
          'native_spec': str(a.spec.relative_to(ROOT)), 'native_spec_sha256': sha(a.spec), 'native_report': spec['output'] + '/report.json',
          'native_report_sha256': sha(ROOT / spec['output'] / 'report.json'), 'native_neutral_PNG': spec['output'] + '/neutral-outdoor.png',
          'native_neutral_PNG_sha256': sha(ROOT / spec['output'] / 'neutral-outdoor.png'), 'resolution_px': spec['resolution_px'],
          'camera_gltf': {'position_m': gltf(camera.location), 'target_m': gltf(view['target_m']),
                          'up_vector': gltf(camera.matrix_world.to_3x3().col[1]),
                          'vertical_fov_radians': 2 * math.atan(1 / projection[1][1]),
                          'near_m': camera.data.clip_start, 'far_m': camera.data.clip_end},
          'native_projection_matrix_rows': [list(row) for row in projection], 'software_projection_witnesses': witnesses,
          'environment_intensity': .3, 'exposure_EV': native['exposure_reference']['exposure_EV'],
          'processing_difference': 'Native AgX Medium High Contrast versus Babylon ACES. Same camera and HDR file/intensity/exposure factor; HDR orientation/prefilter/BRDF and display responses are not calibrated or asserted equal.',
          'tool': 'tools/prepare_material_camera_comparison_v1.py', 'tool_sha256': sha(Path(__file__)),
          'scope': 'Exact preview-camera extraction and numeric projection witnesses only. Not a photograph fit, optical parity, mobile benchmark or art reception.',
          'source_saved': False, 'art_accepted': False, 'physical_iphone_tested': False}
a.output.parent.mkdir(parents=True, exist_ok=True)
a.output.write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'camera_output': str(a.output), 'witnesses': len(witnesses), 'source_saved': False}))
