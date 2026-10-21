"""V4: explicit actual camera metadata and verified linked sources for gray-card material reviews.

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

ROOT = Path(__file__).resolve().parents[4]
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
linked_check = None
if spec.get('linked_source_check'):
    linked_check = ROOT / spec['linked_source_check']
    assert digest(linked_check) == spec['linked_source_check_sha256']
    linked_report = json.loads(linked_check.read_text())
    assert linked_report['source_sha256'] == spec['source_sha256']
    assert linked_report['inspection_export']['sha256'] == spec['export_sha256']
    for row in linked_report['linked_sources']:
        assert digest(ROOT / row['source']) == row['sha256'], row['asset']
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
camera_data.type = view.get('type', 'ORTHO')
assert camera_data.type in {'ORTHO', 'PERSP'}
if camera_data.type == 'ORTHO':
    camera_data.ortho_scale = view['ortho_scale_m']
else:
    camera_data.lens = view['lens_mm']
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
scene.render.use_compositing = False
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
# Numerically expose an actual diffuse18% card, without changing asset shaders.
# This is an exposure reference, not a radiometrically calibrated HDR/camera.
sun.hide_render = True
asset_hidden = {obj: obj.hide_render for obj in objects}
for obj in objects:
    obj.hide_render = True
card_mesh = bpy.data.meshes.new('Exposure reference card mesh')
half = camera_data.ortho_scale * .25 if camera_data.type == 'ORTHO' else (camera.location-Vector(view['target_m'])).length * math.tan(max(camera_data.angle_x,camera_data.angle_y)*.5) * .4
card_mesh.from_pydata([(-half,-half,0),(half,-half,0),(half,half,0),(-half,half,0)], [], [(0,1,2,3)])
card = bpy.data.objects.new('Exposure reference diffuse18 percent', card_mesh)
scene.collection.objects.link(card)
card.location = view['target_m']
card.rotation_euler = camera.rotation_euler
card_material = bpy.data.materials.new('Pure diffuse18 percent exposure reference')
card_material.use_nodes = True
cn, cl = card_material.node_tree.nodes, card_material.node_tree.links
cn.clear()
diffuse = cn.new('ShaderNodeBsdfDiffuse')
diffuse.inputs['Color'].default_value = (.18,.18,.18,1)
diffuse.inputs['Roughness'].default_value = 0
co = cn.new('ShaderNodeOutputMaterial')
cl.new(diffuse.outputs[0], co.inputs['Surface'])
card_mesh.materials.append(card_material)
scene.render.resolution_x = scene.render.resolution_y = 128
scene.cycles.samples = 32
scene.cycles.use_denoising = False
scene.render.image_settings.file_format = 'OPEN_EXR'
scene.render.image_settings.color_depth = '32'
raw = Path('/workspace/wewa-assets/render-raw/material-lighting-review')
raw.mkdir(parents=True, exist_ok=True)
raw_path = raw / (output.name + '-graycard.exr')
scene.render.filepath = str(raw_path)
bpy.ops.render.render(write_still=True)
linear = bpy.data.images.load(str(raw_path), check_existing=False)
assert linear.is_float and tuple(linear.size) == (128,128)
pixels = list(linear.pixels[:])
samples = [pixels[4*(y*128+x):4*(y*128+x)+3] for y in range(56,72) for x in range(56,72)]
mean_rgb = [sum(p[c] for p in samples)/len(samples) for c in range(3)]
mean_luminance = sum(v*w for v,w in zip(mean_rgb,(.2126,.7152,.0722)))
assert math.isfinite(mean_luminance) and mean_luminance > 1e-8
factor = .18 / mean_luminance
exposure_ev = math.log2(factor)
assert abs(exposure_ev) < 20, 'Unexpected reference exposure; inspect the linear render'
card.hide_render = True
for obj, hidden in asset_hidden.items():
    obj.hide_render = hidden
scene.render.resolution_x, scene.render.resolution_y = spec['resolution_px']
scene.cycles.samples = spec['samples']
scene.cycles.use_denoising = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_depth = '8'
scene.view_settings.exposure = exposure_ev
reference_png = output / 'exposure-reference.png'
bpy.data.images['Render Result'].save_render(str(reference_png), scene=scene)
# Camera background is an independent inspection backdrop, not illumination.
background.inputs['Strength'].default_value = 1 / factor
exposure_reference = {'method':'Neutral HDR illuminating a real pure-diffuse18% camera-facing card at target, asset hidden for reference pass; mean of256 center linearEXR pixels',
 'actual_Blender_render':True,'linear_mean_RGB':mean_rgb,'linear_mean_luminance':mean_luminance,
 'target_linear_luminance':.18,'exposure_EV':exposure_ev,'reference_samples':32,'reference_resolution_px':[128,128],
 'raw_private_path':str(raw_path),'raw_sha256':digest(raw_path),'raw_public':False,
 'white_balance_changed':False,'asset_materials_changed':False,'HDR_radiometrically_calibrated':False,
 'reference_card_removed_from_final_views':True,'reference_PNG':str(reference_png.relative_to(ROOT)),'reference_PNG_sha256':digest(reference_png),'camera_backdrop_strength_compensation':1/factor}
records = []
for name, warm in [('neutral-outdoor', False)]:
    sun.hide_render = not warm
    scene.render.filepath = str(output / (name + '.png'))
    bpy.ops.render.render(write_still=True)
    assert digest(source) == spec['source_sha256']
    if linked_check:
        for row in linked_report['linked_sources']:
            assert digest(ROOT / row['source']) == row['sha256']
    record = {'name': name, 'PNG_sha256': digest(scene.render.filepath),
              'source_sha256': spec['source_sha256'], 'export_sha256': spec['export_sha256'],
              'samples': spec['samples'], 'camera_preflight': preflight, 'exposure_reference': exposure_reference,
              'source_saved': False, 'asset_geometry_or_materials_changed': False,
              'actual_Blender_render': True, 'art_accepted': False}
    (output / (name + '-checkpoint.json')).write_text(json.dumps(record, indent=2) + '\n')
    records.append(record)
report = {'schema': 'wewa.component-material-lighting-review.v3',
          'spec_sha256': digest(spec_path), 'tool_sha256': digest(Path(__file__)),
          'source_sha256': spec['source_sha256'], 'export_sha256': spec['export_sha256'],
          'HDR_sha256': spec['HDR_sha256'], 'views': records, 'exposure_reference': exposure_reference,
          'camera_type': camera_data.type, 'camera_spec': view,
          'scope': f'Same unchanged asset under common neutral HDR only, warm sun hidden. Actual {camera_data.type} camera; no city scene or photographic/OEM qualification.',
          'lighting_is_radiometrically_calibrated': False,
          'preview_only': spec['samples'] < 96, 'art_accepted': False,
          'physical_iphone_tested': False}
(output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'material_lighting_review': str(output.relative_to(ROOT)), 'views': len(records)}))
