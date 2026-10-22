"""Read actual linked geometry bounds under revised context poses; never claim fit."""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
R = Path(__file__).resolve().parents[1]
D = R / 'creative/research/whole-exterior-coverage-v10'
plan = json.loads((D / 'layout-plan-v10.json').read_text())
source = Path(bpy.data.filepath)
source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
keys = ['centre-stand-main-frame-v1', 'side-stand-fork-stem-v1', 'side-stand-curved-foot-v3', 'chaincase-upper', 'chaincase-lower', 'rear-tyre']
rows = {}
for key in keys:
    ob = bpy.data.objects['COVERAGE_PARENT [' + key + ']']
    if key in plan['translations_m']:
        ob.location = plan['translations_m'][key]
bpy.context.view_layer.update()
for key in keys:
    ob = bpy.data.objects['COVERAGE_PARENT [' + key + ']']
    pts = [ob.matrix_world @ child.matrix_world @ Vector(p) for child in ob.instance_collection.all_objects if child.type == 'MESH' and not child.hide_render for p in child.bound_box]
    assert pts, key
    rows[key] = {'min': [min(p[i] for p in pts) for i in range(3)], 'max': [max(p[i] for p in pts) for i in range(3)]}
pairs = []
for stand in keys[:3]:
    for other in keys[3:]:
        a, b = rows[stand], rows[other]
        gaps = [max(b['min'][i] - a['max'][i], a['min'][i] - b['max'][i]) for i in range(3)]
        pairs.append({'a': stand, 'b': other, 'signed_axis_separations_m': gaps, 'aabb_separated': max(gaps) > 0, 'positive_gap_proves_only': 'Separation of these actual authored candidate AABBs; negative values are possible contact/hollow overlap, not proven penetration'})
assert hashlib.sha256(source.read_bytes()).hexdigest() == source_sha
(D / 'folded-stand-context-bounds-v1.json').write_text(json.dumps({'source': str(source.relative_to(R)), 'source_sha256': source_sha, 'source_unchanged': True, 'transient_revised_translations': plan['translations_m'], 'bounds': rows, 'pairs': pairs, 'scope': 'Actual candidate bounds after rigid context shifts, not vehicle tolerance, kinematics or mechanical fit', 'art_accepted': False}, indent=2) + '\n')
print(json.dumps(pairs, indent=2))
