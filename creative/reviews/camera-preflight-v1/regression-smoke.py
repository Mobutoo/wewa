import sys,json
sys.path.insert(0,'/workspace/wewa-github/tools')
import bpy
from mathutils import Vector
from blender_component_camera_preflight import check_component_camera
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add(size=.01)
obj=bpy.context.object
bpy.ops.object.camera_add(location=(0,0,.085))
cam=bpy.context.object;cam.rotation_euler=(0,0,0);bpy.context.scene.camera=cam;scene=bpy.context.scene;scene.render.resolution_x=scene.render.resolution_y=500
# Reproduce the real 100mm near plane slicing an 85mm macro.
try:
 check_component_camera(scene,[obj]);raise AssertionError('Missed actual near-clip regression')
except ValueError as e:
 assert json.loads(str(e))['actual_vertices_outside_depth_range']
cam.data.clip_start=.001
assert check_component_camera(scene,[obj])['technical_preflight_passed']
cam.data.type='ORTHO';cam.data.ortho_scale=.005
try:
 check_component_camera(scene,[obj]);raise AssertionError('Missed cropped whole-piece view')
except ValueError as e:
 assert json.loads(str(e))['projected_extent_outside_margin']
assert check_component_camera(scene,[obj],allow_crop=True)['technical_preflight_passed']
# Active shape keys extend the actual object beyond the camera frame.
cam.data.ortho_scale=.03;obj.shape_key_add(name='Basis');key=obj.shape_key_add(name='Extended')
for v in key.data:v.co.x*=5
key.value=1
try:
 check_component_camera(scene,[obj]);raise AssertionError('Ignored actual shape-key extent')
except ValueError as e:
 assert json.loads(str(e))['projected_extent_outside_margin']
print('Camera preflight: near-clip regression, corrected camera, deliberate crop and active morph extent verified')
