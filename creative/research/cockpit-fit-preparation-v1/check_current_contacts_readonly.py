"""Renew selected cockpit contact checks on the coordinator's existing review copy.

No placements, new geometry, source saves, exports, or renders. Pose changes stay in memory.
"""
import bpy
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector, Quaternion
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assembly_report = ROOT / 'creative/reviews/cockpit-current-review-v1/source-geometry-check.json'
assembly = ROOT / 'assets-src/moto-components/cockpit-current-review-v1/cockpit-current-review-v1.blend'
contract = json.loads(assembly_report.read_text())
assert sha(assembly) == contract['source_sha256']
snapshot = json.loads((HERE / 'input-snapshot.json').read_text())
expected = {e['key']: e for e in snapshot['entries']}
for row in contract['linked_sources']:
    assert row['sha256'] == expected[row['asset']]['source_sha256']
bpy.ops.wm.open_mainfile(filepath=str(assembly))
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
objects = list(bpy.data.collections['MOTORCYCLE18_LINKED_REVIEW_COPIES'].all_objects)


def find(asset, prefix):
    matches = [o for o in objects if o.type == 'MESH' and o.name.startswith('M18 [' + asset + '] ' + prefix)]
    assert len(matches) == 1, (asset, prefix, [o.name for o in matches])
    return matches[0]


def tree(obj):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles()
        return BVHTree.FromPolygons([evaluated.matrix_world @ v.co for v in mesh.vertices],
                                    [tuple(t.vertices) for t in mesh.loop_triangles], all_triangles=True)
    finally:
        evaluated.to_mesh_clear()


trees = {}


def fixed_tree(obj):
    if obj.name not in trees:
        trees[obj.name] = tree(obj)
    return trees[obj.name]


checks = []


def check(a, b, group, pose=None, moving_a=False):
    count = len((tree(a) if moving_a else fixed_tree(a)).overlap(fixed_tree(b)))
    checks.append({'group': group, 'a': a.name, 'b': b.name,
                   'pose': pose or 'rest', 'actual_triangle_surface_crossings': count})


left_switch = [find('switchgear-left-v3', p) for p in
               ['LH switch upper shell', 'LH switch lower shell', 'LH dipper rocker - high low',
                'LH turn selector - centre push', 'LH horn push tongue']]
right_switch = [find('switchgear-right', p) for p in
                ['RH switch upper shell', 'RH switch lower shell',
                 'RH observed red top control - function', 'RH estimated black actuator collar']]
lever_sets = []
for key, side, sign, switch in [('clutch-control', 'Clutch', 1, left_switch),
                               ('front-brake-control', 'Front cable brake', -1, right_switch)]:
    lever = find(key, side + ' lever - moving')
    parts = [o for o in objects if o.type == 'MESH' and o.name.startswith('M18 [' + key + '] ')]
    for obj in parts:
        for other in switch:
            check(obj, other, key + '_current_switch_rest')
    lever_sets.append((parts, switch))
    basis, mode = lever.matrix_basis.copy(), lever.rotation_mode
    rest = basis.to_quaternion()
    try:
        lever.rotation_mode = 'QUATERNION'
        for angle in [3, 6, 9, 12]:
            lever.rotation_quaternion = rest @ Quaternion(Vector((0, 0, sign)), math.radians(angle))
            bpy.context.view_layer.update()
            for other in switch:
                check(lever, other, key + '_current_switch_motion', {'pull_degrees': angle}, True)
    finally:
        lever.matrix_basis = basis
        lever.rotation_mode = mode
        bpy.context.view_layer.update()

left_grip = find('grips-v3', 'Left rubber grip')
right_grip = find('grips-v3', 'Right rubber grip')
for part in left_switch + lever_sets[0][0]:
    check(left_grip, part, 'left_grip_v3_controls_rest')
rotor = find('throttle', 'Throttle sleeve and cable spool')
assert right_grip.parent == rotor, 'Use the actual review binding, do not invent one here'
guide = find('throttle', 'Throttle fixed hollow cable guide')
basis, mode = rotor.matrix_basis.copy(), rotor.rotation_mode
rest = basis.to_quaternion()
try:
    rotor.rotation_mode = 'QUATERNION'
    for angle in [0, 10, 20, 30, 40, 50]:
        rotor.rotation_quaternion = rest @ Quaternion(Vector((-1, 0, 0)), math.radians(angle))
        bpy.context.view_layer.update()
        for other in right_switch + lever_sets[1][0] + [guide]:
            check(right_grip, other, 'right_grip_v3_controls_motion', {'throttle_degrees': angle}, True)
finally:
    rotor.matrix_basis = basis
    rotor.rotation_mode = mode
    bpy.context.view_layer.update()

pigtail = find('cockpit-cables', 'Visible ignition pigtail')
visor_parts = [o for o in objects if o.type == 'MESH' and o.name.startswith('M18 [instrument-visor] ')]
instrument_physical = [o for o in objects if o.type == 'MESH'
                       and o.name.startswith('M18 [instruments-v3] ')
                       and any(s in o.name for s in ['hollow rear pod', 'stepped bezel', 'clear closed lens',
                                                    'rear mounting boss', 'Shaped central cluster cover'])]
for other in visor_parts + instrument_physical:
    check(pigtail, other, 'pigtail_current_instruments_visor_rest')
assert sha(assembly) == contract['source_sha256']
for row in contract['linked_sources']:
    assert sha(ROOT / row['source']) == row['sha256']
out = HERE / 'current-contact-checks.json'
assert not out.exists()
nonzero = [x for x in checks if x['actual_triangle_surface_crossings']]
out.write_text(json.dumps({'schema': 'wewa.cockpit-current-contact-preparation.v1',
                          'assembly_source_sha256': sha(assembly),
                          'assembly_report_sha256': sha(assembly_report),
                          'checker_sha256': sha(__file__),
                          'source_hashes': {x['asset']: x['sha256'] for x in contract['linked_sources']},
                          'checks': checks, 'nonzero_checks': nonzero,
                          'scope': 'Selected actual triangle-surface crossings at rest and partial controls. Not solid containment, minimum clearance, all cockpit pairs, OEM tolerances or full steering.',
                          'new_geometry_or_source_saved': False,
                          'art_accepted': False}, indent=2) + '\n')
print('CURRENT_CONTACT_CHECKS', len(checks), 'NONZERO', len(nonzero), flush=True)
