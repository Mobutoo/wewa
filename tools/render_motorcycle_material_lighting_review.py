"""Read-only, reproducible material comparison of a frozen motorcycle component.

Run in Blender with --python ... -- --spec SPEC. This changes only the loaded
scene in memory and writes new review images. It never saves the asset.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from blender_component_camera_preflight import check_component_camera


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


parser = argparse.ArgumentParser()
parser.add_argument('--spec', required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
spec_path = Path(args.spec).resolve()
spec = json.loads(spec_path.read_text())
source = ROOT / spec['source']
export = ROOT / spec['export']
hdr = ROOT / spec['HDR']
for name, path in [('source', source), ('export', export), ('HDR', hdr)]:
    assert digest(path) == spec[name + '_sha256'], 'Unfrozen ' + name
output = ROOT / spec['output']
output.mkdir(parents=True, exist_ok=True)
assert not list(output.glob('*.png')), 'Use a new review directory'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene = bpy.context.scene
collection = bpy.data.collections[spec['collection']]
objects = list(collection.all_objects)
assert any(o.type == 'MESH' for o in objects)
# Hide the source studio locally. Do not change asset geometry or materials.
for obj in scene.objects:
    if obj not in objects:
        obj.hide_render = True
camera_data = bpy.data.cameras.new('Read-only material review camera')
camera = bpy.data.objects.new(camera_data.name, camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
view = spec['camera']
camera.location = view['location_m']
camera.rotation_euler = (Vector(view['target_m']) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera_data.type = 'ORTHO'
camera_data.ortho_scale = view['ortho_scale_m']
camera_data.clip_start = .001
camera_data.clip_end = 100
scene.render.engine = 'CYCLES'
scene.cycles.samples = spec['samples']
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'
scene.render.resolution_x, scene.render.resolution_y = spec['resolution_px']
scene.render.resolution_percentage = 100
scene.render.threads_mode = 'FIXED'
scene.render.threads = 1
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Medium High Contrast'
scene.view_settings.exposure = 0
scene.view_settings.gamma = 1
preflight = check_component_camera(scene, [o for o in objects if o.type == 'MESH'])
world = bpy.data.worlds.new('Read-only common outdoor lighting')
world.use_nodes = True
nodes, links = world.node_tree.nodes, world.node_tree.links
nodes.clear()
env = nodes.new('ShaderNodeTexEnvironment')
env.image = bpy.data.images.load(str(hdr), check_existing=True)
environment = nodes.new('ShaderNodeBackground')
environment.inputs['Strength'].default_value = .3
links.new(env.outputs['Color'], environment.inputs['Color'])
background = nodes.new('ShaderNodeBackground')
background.inputs['Color'].default_value = (.12, .12, .12, 1)
background.inputs['Strength'].default_value = 1
path = nodes.new('ShaderNodeLightPath')
mix = nodes.new('ShaderNodeMixShader')
links.new(path.outputs['Is Camera Ray'], mix.inputs[0])
links.new(environment.outputs[0], mix.inputs[1])
links.new(background.outputs[0], mix.inputs[2])
out = nodes.new('ShaderNodeOutputWorld')
links.new(mix.outputs[0], out.inputs['Surface'])
scene.world = world
sun_data = bpy.data.lights.new('Read-only warm late-day comparison', 'SUN')
sun_data.energy = 1.5
sun_data.color = (1, .72, .48)
sun_data.angle = math.radians(2)
sun = bpy.data.objects.new(sun_data.name, sun_data)
scene.collection.objects.link(sun)
sun.rotation_euler = tuple(math.radians(v) for v in (65, -20, -35))
records = []
for name, warm in [('neutral-outdoor', False), ('warm-late-day', True)]:
    sun.hide_render = not warm
    scene.render.filepath = str(output / (name + '.png'))
    bpy.ops.render.render(write_still=True)
    assert digest(source) == spec['source_sha256']
    record = {'name': name, 'PNG_sha256': digest(scene.render.filepath),
              'source_sha256': spec['source_sha256'], 'export_sha256': spec['export_sha256'],
              'samples': spec['samples'], 'camera_preflight': preflight,
              'source_saved': False, 'asset_geometry_or_materials_changed': False,
              'actual_Blender_render': True, 'art_accepted': False}
    (output / (name + '-checkpoint.json')).write_text(json.dumps(record, indent=2) + '\n')
    records.append(record)
report = {'schema': 'wewa.component-material-lighting-review.v1',
          'spec_sha256': digest(spec_path), 'tool_sha256': digest(Path(__file__)),
          'source_sha256': spec['source_sha256'], 'export_sha256': spec['export_sha256'],
          'HDR_sha256': spec['HDR_sha256'], 'views': records,
          'scope': 'Same unchanged asset under common neutral HDR then warm sun addition. Orthographic isolated material study; no city scene or photographic/OEM qualification.',
          'lighting_is_radiometrically_calibrated': False,
          'preview_only': spec['samples'] < 96, 'art_accepted': False,
          'physical_iphone_tested': False}
(output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'material_lighting_review': str(output.relative_to(ROOT)), 'views': len(records)}))
