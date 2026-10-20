# Run in an empty Blender process; no rendering or saving.
import bpy, json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
BASE = Path('/workspace/wewa-github/creative/research/reference-camera-studies')
exec((BASE/'create-working-cameras.blender.py').read_text())
report = json.loads((BASE/'camera-studies.json').read_text())
bpy.context.view_layer.update()
rows = []
for view in report['views']:
 cam = bpy.data.objects['WEWA_STUDY_'+view['id']]
 actual = {}
 differences = {}
 for name, point in report['guides_world_m_unchanged'].items():
  uv = world_to_camera_view(bpy.context.scene, cam, Vector(point))
  actual[name] = [float(uv.x*1000), float((1-uv.y)*700)]
  expected = view['selected_working_camera']['fit']['projected_uv_px'][name]
  differences[name] = [actual[name][i]-expected[i] for i in range(2)]
 assert max(abs(d) for pair in differences.values() for d in pair) < .001, differences
 rows.append({'id': view['id'], 'actual_blender_projection_px': actual, 'blender_minus_numpy_uv_px': differences})
result = {'blender': bpy.app.version_string, 'threads': 1, 'render_executed': False, 'existing_source_opened_or_modified': False, 'camera_calibrated': False, 'scope': 'Independent Blender projection matches explicit working-camera equations within0.001px; no photograph/metric calibration implied.', 'views': rows}
(BASE/'blender-projection-check.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result))
