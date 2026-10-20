# Generated explicit working cameras only; no model mutation or saving.
import bpy
from mathutils import Quaternion
CAMERAS = [{'name': 'WEWA_STUDY_R00', 'kind': 'ORTHO', 'role': 'selected_working_camera_not_calibrated', 'location_m': [-4.0, 0.3041840607210626, -0.3888804554079697], 'rotation_matrix_local_to_world': [[0.0, -0.0, -1.0], [-1.0, 0.0, -0.0], [0.0, 1.0, -0.0]], 'rotation_quaternion_wxyz': [0.5, 0.5, -0.5, -0.5], 'forward_world': [1.0, 0.0, 0.0], 'up_world': [-0.0, 0.0, 1.0], 'target_m': [0.0, 0.3041840607210626, -0.3888804554079697], 'ortho_scale_m': 2.4383301707779883, 'ortho_scale_convention': 'Blender horizontal frame width, sensor_fit HORIZONTAL', 'pixels_per_candidate_working_m': 410.1167315175098, 'distance_m': 4.0, 'distance_status': 'Arbitrary: orthographic distance is unobservable.', 'fit': {'projected_uv_px': {'front_axle': [797.0, 494.0], 'rear_axle': [269.99999999999994, 494.0], 'bar_clamp': [624.7509727626459, 190.51361867704276]}, 'observed_uv_px': {'front_axle': [797.0, 494.0], 'rear_axle': [270.0, 494.0], 'bar_clamp': [625.0, 190.0]}, 'signed_residual_uv_px': {'front_axle': [0.0, 0.0], 'rear_axle': [-5.684341886080802e-14, 0.0], 'bar_clamp': [-0.24902723735408472, 0.5136186770427571]}, 'euclidean_residual_px': {'front_axle': 0.0, 'rear_axle': 5.684341886080802e-14, 'bar_clamp': 0.5708053173818195}, 'unweighted_rms_coordinate_px': 0.23303029500881056, 'max_absolute_normalised_reading_residual': 0.04280155642022976, 'normalisation_is': 'Manual image-reading intervals only; not a probabilistic camera-error or physical tolerance.'}}, {'name': 'WEWA_STUDY_R04', 'kind': 'ORTHO', 'role': 'selected_working_camera_not_calibrated', 'location_m': [4.0, 0.2699639639639639, -0.4065945945945947], 'rotation_matrix_local_to_world': [[0.0, 0.0, 1.0], [1.0, 0.0, -0.0], [0.0, 1.0, -0.0]], 'rotation_quaternion_wxyz': [0.5, 0.5, 0.5, 0.5], 'forward_world': [-1.0, 0.0, 0.0], 'up_world': [0.0, 0.0, 1.0], 'target_m': [0.0, 0.2699639639639639, -0.4065945945945947], 'ortho_scale_m': 2.315315315315315, 'ortho_scale_convention': 'Blender horizontal frame width, sensor_fit HORIZONTAL', 'pixels_per_candidate_working_m': 431.90661478599225, 'distance_m': 4.0, 'distance_status': 'Arbitrary: orthographic distance is unobservable.', 'fit': {'projected_uv_px': {'front_axle': [202.00000000000003, 494.0], 'rear_axle': [757.0, 494.0], 'bar_clamp': [383.40077821011675, 174.38910505836571]}, 'observed_uv_px': {'front_axle': [202.0, 494.0], 'rear_axle': [757.0, 494.0], 'bar_clamp': [364.0, 188.0]}, 'signed_residual_uv_px': {'front_axle': [2.842170943040401e-14, 0.0], 'rear_axle': [0.0, 0.0], 'bar_clamp': [19.400778210116755, -13.610894941634285]}, 'euclidean_residual_px': {'front_axle': 2.842170943040401e-14, 'rear_axle': 0.0, 'bar_clamp': 23.699085557682324}, 'unweighted_rms_coordinate_px': 9.675111164480633, 'max_absolute_normalised_reading_residual': 1.6167315175097297, 'normalisation_is': 'Manual image-reading intervals only; not a probabilistic camera-error or physical tolerance.'}}]
scene = bpy.context.scene
scene.render.resolution_x = 1000
scene.render.resolution_y = 700
scene.render.resolution_percentage = 100
scene.render.pixel_aspect_x = scene.render.pixel_aspect_y = 1
for spec in CAMERAS:
 data = bpy.data.cameras.new(spec['name'])
 data.type = 'ORTHO'
 data.sensor_fit = 'HORIZONTAL'
 data.ortho_scale = spec['ortho_scale_m']
 data.clip_start = .01
 data.clip_end = 100
 ob = bpy.data.objects.new(spec['name'], data)
 scene.collection.objects.link(ob)
 ob.location = spec['location_m']
 ob.rotation_mode = 'QUATERNION'
 ob.rotation_quaternion = Quaternion(spec['rotation_quaternion_wxyz'])
 if scene.camera is None:
  scene.camera = ob
