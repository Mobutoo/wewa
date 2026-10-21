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
# Reuse the actual preflight exposure card; no second card, no white balance or asset edits.
sun.hide_render = True
preview_report_path = ROOT / spec['preview_report']
assert digest(preview_report_path) == spec['preview_report_sha256']
preview = json.loads(preview_report_path.read_text())
assert preview['source_sha256'] == spec['source_sha256'] and preview['export_sha256'] == spec['export_sha256']
assert preview['camera_spec'] == view and preview['HDR_sha256'] == spec['HDR_sha256']
reference = preview['exposure_reference']
assert digest(reference['raw_private_path']) == reference['raw_sha256']
scene.view_settings.exposure = reference['exposure_EV']
background.inputs['Strength'].default_value = reference['camera_backdrop_strength_compensation']
scene.cycles.denoising_use_gpu = False
bpy.context.view_layer.use_pass_normal = True
bpy.context.view_layer.use_pass_diffuse_color = True
bpy.context.view_layer.cycles.denoising_store_passes = True
config = {'source_sha256':spec['source_sha256'],'export_sha256':spec['export_sha256'],
 'protocol_sha256':digest(Path(__file__)),'spec_sha256':digest(spec_path),'HDR_sha256':spec['HDR_sha256'],
 'preview_report_sha256':spec['preview_report_sha256'],'camera_spec':view,
 'actual_camera_matrix':[list(a)for a in camera.matrix_world], 'near_far_m':[camera.data.clip_start,camera.data.clip_end],
 'renderer':'Blender4.3.2 Cycles96/OIDN CPU','samples':96,'resolution_px':spec['resolution_px'],
 'color_management':{'view_transform':'AgX','look':'AgX - Medium High Contrast','gamma':1,'exposure_EV':reference['exposure_EV']},
 'lighting':'Neutral HDR only; warm sun hidden','exposure_reference_reused':reference,'source_saved':False}
config_sha=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()
checkpoint=output/'neutral-final-checkpoint.json'
png=output/'neutral-outdoor.png'
exr=Path('/workspace/wewa-assets/renders/rear-sns/outer-spring-v1/neutral-outdoor.exr')
exr.parent.mkdir(parents=True,exist_ok=True)
old=json.loads(checkpoint.read_text())if checkpoint.exists()else None
if not(old and old['config_sha256']==config_sha and png.exists()and exr.exists()and digest(png)==old['PNG_sha256']and digest(exr)==old['EXR_sha256']):
 scene.render.image_settings.file_format='OPEN_EXR_MULTILAYER';scene.render.image_settings.color_depth='32';scene.render.filepath=str(exr)
 bpy.ops.render.render(write_still=True)
 scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(png),scene=scene)
 checkpoint.write_text(json.dumps({'name':'neutral-outdoor','configuration':config,'config_sha256':config_sha,'PNG_path':str(png),'PNG_sha256':digest(png),'EXR_private_path':str(exr),'EXR_sha256':digest(exr),'frame_check':preflight,'actually_saved':True},indent=2)+'\n')
assert digest(source)==spec['source_sha256'] and digest(export)==spec['export_sha256']
print('SAVED neutral-outdoor96')
