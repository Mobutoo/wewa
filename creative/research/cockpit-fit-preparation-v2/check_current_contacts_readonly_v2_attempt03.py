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
    if row['asset'] != 'cockpit-cables':
        assert row['sha256'] == expected[row['asset']]['source_sha256']
bpy.ops.wm.open_mainfile(filepath=str(assembly))
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
objects = list(bpy.data.collections['MOTORCYCLE18_LINKED_REVIEW_COPIES'].all_objects)
old_pigtail = next(o for o in objects if o.type == 'MESH' and o.name.startswith('M18 [cockpit-cables] Visible ignition pigtail'))
# Append the actual frozen v2 collection plus its external parent/interface guides.
# These are disposable in-memory instances; no source save or placement transform.
cable_source = ROOT / expected['cockpit-cables']['source']
assert sha(cable_source) == expected['cockpit-cables']['source_sha256']
with bpy.data.libraries.load(str(cable_source), link=False) as (available, loaded):
    loaded.collections = ['WEWA_COCKPIT_CABLES_PARTIAL', 'CABLES_IMMUTABLE_INTERFACE_GUIDES']
for col in loaded.collections:
    bpy.context.scene.collection.children.link(col)
    col.hide_viewport = False
# Matrices of the external contact parent must actually be evaluated.
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
cable_objects = list(loaded.collections[0].all_objects)
assert len([o for o in cable_objects if o.type == 'MESH']) == 3
objects = [o for o in objects if not o.name.startswith('M18 [cockpit-cables] ')] + cable_objects
loaded_cable_matrices = {o.name: [list(row) for row in o.evaluated_get(depsgraph).matrix_world] for o in cable_objects if o.type == 'MESH'}


def find(asset, prefix):
    matches = [o for o in objects if o.type == 'MESH' and ((asset == 'cockpit-cables' and o in cable_objects and o.name.startswith(prefix)) or (asset != 'cockpit-cables' and o.name.startswith('M18 [' + asset + '] ' + prefix)))]
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
out = HERE / 'current-contact-checks-attempt03.json'
assert not out.exists()
nonzero = [x for x in checks if x['actual_triangle_surface_crossings']]
out.write_text(json.dumps({'schema': 'wewa.cockpit-current-contact-preparation.v2',
                          'assembly_source_sha256': sha(assembly),
                          'assembly_report_sha256': sha(assembly_report),
                          'checker_sha256': sha(__file__),
                          'source_hashes': {x['key']: x['source_sha256'] for x in snapshot['entries']},
                          'input_snapshot_sha256': sha(HERE / 'input-snapshot.json'),
                          'cable_world_matrices': loaded_cable_matrices,
                          'v2_guides_reactivated_in_memory': True,
                          'checks': checks, 'nonzero_checks': nonzero,
                          'scope': 'Selected actual triangle-surface crossings at rest and partial controls. Not solid containment, minimum clearance, all cockpit pairs, OEM tolerances or full steering.',
                          'new_geometry_or_source_saved': False,
                          'art_accepted': False}, indent=2) + '\n')
print('CURRENT_CONTACT_CHECKS', len(checks), 'NONZERO', len(nonzero), flush=True)

# Independently recheck explicit edge segments and solid membership, not only overlap().
from mathutils.geometry import intersect_ray_tri

def world_data(ob):
    ev = ob.evaluated_get(depsgraph)
    me = ev.to_mesh()
    try:
        me.calc_loop_triangles()
        verts = [ev.matrix_world @ v.co for v in me.vertices]
        tris = [tuple(t.vertices) for t in me.loop_triangles]
    finally:
        ev.to_mesh_clear()
    return {'name': ob.name, 'vertices': verts, 'triangles': tris,
            'tree': BVHTree.FromPolygons(verts, tris, all_triangles=True)}

def edge_segment_tests(A, B):
    edges = {tuple(sorted((t[k], t[(k+1)%3]))) for t in A['triangles'] for k in range(3)}
    hits = []
    valid = 0
    for i, j in edges:
        start, end = A['vertices'][i], A['vertices'][j]
        delta = end - start
        if delta.length < 1e-12:
            continue
        valid += 1
        direction = delta.normalized()
        location, normal, index, distance = B['tree'].ray_cast(start, direction, delta.length + 1e-9)
        if location is None or distance < -1e-9 or distance > delta.length + 1e-9:
            continue
        target = [B['vertices'][k] for k in B['triangles'][index]]
        exact = intersect_ray_tri(*target, direction, start, True)
        assert exact is not None, ('Ray/triangle disagreement', i, j, index)
        projection = (exact - start).dot(direction)
        assert -1e-8 <= projection <= delta.length + 1e-8
        hits.append({'edge_vertex_indices': [i,j], 'target_triangle': index, 'point_world_m': list(exact)})
    return {'from': A['name'], 'to': B['name'], 'unique_valid_segments_tested': valid,
            'method': 'Every unique actual triangle edge ray-cast against target real triangles; returned hits independently confirmed with intersect_ray_tri and finite segment bounds. No overlap-pair filtering.',
            'intersection_count': len(hits), 'intersections': hits}

def contained_points(A, B):
    directions = [Vector(v).normalized() for v in [(.8123,.3937,.4301),(-.2713,.8917,.3629),(.4721,-.2189,.8541)]]
    samples = [('vertex',i,p)for i,p in enumerate(A['vertices'])]
    samples += [('triangle_centroid',i,sum((A['vertices'][k]for k in t),Vector())/3)for i,t in enumerate(A['triangles'])]
    inside, ambiguous, boundary = [], [], []
    for kind, index, p in samples:
        nearest = B['tree'].find_nearest(p)
        if nearest[0] is not None and nearest[3] <= 1e-8:
            boundary.append([kind,index]);continue
        parities = []
        for direction in directions:
            origin = p.copy(); hits = 0
            for _ in range(200):
                location, normal, face, distance = B['tree'].ray_cast(origin,direction,5.0)
                if location is None:break
                hits += 1; origin = location + direction * 1e-7
            else:raise AssertionError('Containment ray failed to terminate')
            parities.append(hits % 2)
        if len(set(parities)) > 1: ambiguous.append([kind,index,parities])
        elif parities[0]:inside.append([kind,index])
    return {'from':A['name'],'solid':B['name'],'vertices_tested':len(A['vertices']),
            'triangle_centroids_tested':len(A['triangles']),'inside_count':len(inside),'inside':inside,
            'ambiguous_direction_count':len(ambiguous),'ambiguous':ambiguous,
            'boundary_within_1e_8_m_count':len(boundary),'boundary':boundary,
            'directions_world':[list(d)for d in directions],
            'ray_restart_step_m':1e-7,
            'method':'Odd/even actual triangle ray crossings, 3 non-axis directions; boundary classified separately at1e-8m. Restart advancement1e-7m avoids repeat hits of the same floating triangle; separately diagnosed at1e-8/1e-7/1e-6. This samples vertices/centroids and is not an exact volume boolean.'}

cover = find('instruments-v3', 'Shaped central cluster cover')
A, B, OLD = world_data(pigtail), world_data(cover), world_data(old_pigtail)
old_pairs = OLD['tree'].overlap(B['tree'])
assert len(old_pairs) == 32, ('Historical context no longer reproduced', len(old_pairs))
new_pairs = A['tree'].overlap(B['tree'])
segments = [edge_segment_tests(A,B),edge_segment_tests(B,A)]
containment = [contained_points(A,B),contained_points(B,A)]
selfpairs = [(i,j)for i,j in A['tree'].overlap(A['tree'])if i<j and not set(A['triangles'][i]).intersection(A['triangles'][j])]
nearest = min(B['tree'].find_nearest(p)[3]for p in A['vertices'])
spatial = {'schema':'wewa.cockpit-current-independent-spatial.v2',
           'source_hashes':{x['key']:x['source_sha256']for x in snapshot['entries']},
           'input_snapshot_sha256':sha(HERE/'input-snapshot.json'),'checker_sha256':sha(__file__),
           'old_v1_pigtail_crossing_triangle_pairs':len(old_pairs),'old_v1_pair_indices':[list(t)for t in old_pairs],
           'new_v2_pigtail_crossing_triangle_pairs':len(new_pairs),
           'segment_triangle_checks':segments,'contained_point_checks':containment,
           'pigtail_nonadjacent_triangle_self_crossings':len(selfpairs),
           'minimum_sampled_pigtail_vertex_to_cover_surface_distance_m':nearest,
           'distance_is_not_exact_surface_clearance':True,
           'source_modified_or_saved':False,'model_rendered':False,
           'complete_upper_cables_or_harness_created':False,'art_accepted':False}
(HERE/'spatial-attempt03-before-assertions.json').write_text(json.dumps(spatial,indent=2)+'\n')
print('CONTAINMENT_DIAGNOSTIC',[(x['inside_count'],x['ambiguous_direction_count'],x['boundary_within_1e_8_m_count'])for x in containment],flush=True)
assert not nonzero and len(checks)==177
assert not new_pairs and not selfpairs
assert all(x['intersection_count']==0 for x in segments)
assert all(x['inside_count']==0 and x['ambiguous_direction_count']==0 and x['boundary_within_1e_8_m_count']==0 for x in containment)
for e in snapshot['entries']:
    assert sha(ROOT/e['source'])==e['source_sha256']
    for export in e['exports']:assert sha(ROOT/export['path'])==export['sha256']
assert sha(assembly)==contract['source_sha256']
(HERE/'independent-spatial-checks.json').write_text(json.dumps(spatial,indent=2)+'\n')
print('INDEPENDENT_SPATIAL_CHECKS',len(old_pairs),len(new_pairs),[x['unique_valid_segments_tested']for x in segments],nearest,flush=True)
