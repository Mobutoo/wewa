"""Bounded gray exterior studies. Never alters or receives the original SNS parts."""
import argparse
import bmesh
import bpy
import hashlib
import json
import math
import sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REVIEW = ROOT / 'creative/reviews/rear-sns-end-closures-study-v1'
PLAN = ROOT / 'creative/research/rear-sns-end-closures-study-v1/preparation.json'
INPUT = HERE.parent / 'rest-assembly/rear-sns-rest-assembly-v1.glb'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
pa = argparse.ArgumentParser()
pa.add_argument('--render', action='store_true')
args = pa.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
REVIEW.mkdir(parents=True, exist_ok=True)
plan = json.loads(PLAN.read_text())
expected = json.loads((ROOT / 'creative/reviews/rear-sns-rest-assembly-v1/visual-reading.json').read_text())['export_sha256']
assert sha(INPUT) == expected
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.import_scene.gltf(filepath=str(INPUT))
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
# Import converts glTF coordinates back to the original Blender SNS frame.
originals = [o for o in scene.objects if o.type == 'MESH']
assert originals

def signature(ob):
    h = hashlib.sha256()
    h.update(repr([tuple(v.co) for v in ob.data.vertices]).encode())
    h.update(repr([tuple(p.vertices) for p in ob.data.polygons]).encode())
    h.update(repr([list(row) for row in ob.matrix_world]).encode())
    return h.hexdigest()

before = {ob.name: signature(ob) for ob in originals}
gray = bpy.data.materials.new('Gray form study only - no finish claim')
gray.use_nodes = True
bs = gray.node_tree.nodes.get('Principled BSDF')
bs.inputs['Base Color'].default_value = (.22, .22, .22, 1)
bs.inputs['Roughness'].default_value = .45
scene.view_layers[0].material_override = gray
studies = bpy.data.collections.new('WEWA_SNS_END_CLOSURE_STUDIES_NOT_RECEIVED')
scene.collection.children.link(studies)
new = []

def lathe(unit):
    corners = [Vector(p) for p in unit['profile_r_z_m']]
    profile = []
    # Round in the source section rather than a 3D bevel: short thin lips can
    # produce collapsed bevel triangles even when the resulting volume is closed.
    for i, p in enumerate(corners):
        previous, following = corners[i - 1], corners[(i + 1) % len(corners)]
        trim = min(.00004, (previous - p).length * .18, (following - p).length * .18)
        a = p + (previous - p).normalized() * trim
        b = p + (following - p).normalized() * trim
        for sample in range(7):
            t = sample / 6
            q = (1 - t) ** 2 * a + 2 * (1 - t) * t * p + t ** 2 * b
            profile.append(tuple(q))
    segments = 256
    vertices = [(r * math.cos(a * 2 * math.pi / segments),
                 r * math.sin(a * 2 * math.pi / segments), z)
                for r, z in profile for a in range(segments)]
    faces = []
    for j in range(len(profile)):
        for a in range(segments):
            b = (a + 1) % segments
            k = (j + 1) % len(profile)
            faces.append((j * segments + a, j * segments + b,
                          k * segments + b, k * segments + a))
    mesh = bpy.data.meshes.new(unit['id'] + ' original lathed section')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    if bm.calc_volume(signed=True) < 0:
        bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    # Each profile segment has a separate UV strip, with a real angular seam.
    uv = mesh.uv_layers.new(name='AuthoredProfileUV')
    for poly in mesh.polygons:
        ring = poly.index // segments
        angular = poly.index % segments
        for loop_idx, (u, v) in zip(poly.loop_indices, [
            (angular / segments, ring / len(profile)),
            ((angular + 1) / segments, ring / len(profile)),
            ((angular + 1) / segments, (ring + 1) / len(profile)),
            (angular / segments, (ring + 1) / len(profile)),
        ]):
            uv.data[loop_idx].uv = (u, v)
        poly.use_smooth = True
    ob = bpy.data.objects.new(unit['id'], mesh)
    studies.objects.link(ob)
    ob.data.materials.append(gray)
    ob['scope'] = unit['scope']
    ob['dimensions_status'] = 'estimated, not OEM'
    ob['art_accepted'] = False
    return ob

new = [lathe(u) for u in plan['units']]
bpy.context.view_layer.update()

def evaluated(ob):
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    me = ev.to_mesh()
    me.calc_loop_triangles()
    vs = [ob.matrix_world @ v.co for v in me.vertices]
    ts = [tuple(t.vertices) for t in me.loop_triangles]
    bm = bmesh.new()
    bm.from_mesh(me)
    volume = bm.calc_volume(signed=True)
    bad_edges = sum(not e.is_manifold for e in bm.edges)
    bm.free()
    areas = [((vs[t[1]] - vs[t[0]]).cross(vs[t[2]] - vs[t[0]])).length / 2 for t in ts]
    ev.to_mesh_clear()
    return vs, ts, {'vertices': len(vs), 'triangles': len(ts),
                    'signed_volume_m3': volume, 'non_manifold_edges': bad_edges,
                    'zero_area_triangles': sum(x <= 1e-16 for x in areas),
                    'minimum_triangle_area_m2': min(areas),
                    'bbox_m': [[min(v[k] for v in vs), max(v[k] for v in vs)] for k in range(3)]}

trees = {}
for ob in originals + new:
    vs, ts, stats = evaluated(ob)
    trees[ob.name] = BVHTree.FromPolygons(vs, ts, all_triangles=True, epsilon=0)
checks = []
for ob in new:
    _, _, stats = evaluated(ob)
    assert stats['non_manifold_edges'] == 0, (ob.name, stats)
    assert stats['zero_area_triangles'] == 0, (ob.name, stats)
    assert stats['signed_volume_m3'] > 0, (ob.name, stats)
    contacts = []
    for other in originals + new:
        if other == ob:
            continue
        overlap = trees[ob.name].overlap(trees[other.name])
        if overlap:
            contacts.append({'other': other.name, 'intersecting_triangle_pairs': len(overlap)})
    checks.append({'component': ob.name, **stats, 'surface_intersections': contacts})
assert before == {ob.name: signature(ob) for ob in originals}
world = bpy.data.worlds.new('Neutral gray study world')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (.16, .16, .16, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = .4
scene.world = world
for name, eye, energy, size in [('Key', (.35, -.4, .4), 18, .4),
                                 ('Fill', (-.3, -.2, .2), 8, .3),
                                 ('Rim', (0, .3, .2), 12, .25)]:
    light = bpy.data.objects.new(name, bpy.data.lights.new(name, 'AREA'))
    scene.collection.objects.link(light)
    light.location = eye
    light.data.energy = energy
    light.data.shape = 'DISK'
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, .055)) - light.location).to_track_quat('-Z', 'Y').to_euler()
camera = bpy.data.objects.new('Gray study camera', bpy.data.cameras.new('Gray study camera'))
scene.collection.objects.link(camera)
scene.camera = camera
camera.data.clip_start = .0001
camera.data.clip_end = 10
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
# This executor's Debian Blender has Cycles CPU but no OIDN enum. Do not claim
# parity with the historical OIDN finals or silently substitute a filter.
scene.cycles.use_denoising = False
scene.render.threads_mode = 'FIXED'
scene.render.threads = 2
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Medium High Contrast'
scene.view_settings.exposure = -2
scene.render.resolution_x = 1100
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
scene['scope'] = 'Gray external closure studies, not completed SNS or whole motorcycle'
source = HERE / 'sns-end-closures-gray-study-v1.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(source), compress=True)
exports = []
for ob in new:
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    path = HERE / (ob.name.lower() + '-study-v1.glb')
    bpy.ops.export_scene.gltf(filepath=str(path), export_format='GLB', use_selection=True,
                              export_apply=True, export_yup=True, export_animations=False)
    exports.append({'path': str(path.relative_to(ROOT)), 'sha256': sha(path)})
report = {'schema': 1, 'source': str(source.relative_to(ROOT)), 'source_sha256': sha(source),
          'input_glb': str(INPUT.relative_to(ROOT)), 'input_sha256': sha(INPUT),
          'preparation_sha256': sha(PLAN), 'builder_sha256': sha(Path(__file__)),
          'imported_input_geometry_and_transforms_unchanged': before == {ob.name: signature(ob) for ob in originals},
          'comparison_scope': 'Blender imported vertex/topology/matrix signatures; not original glTF buffer parity',
          'components': checks, 'exports': exports, 'views': [],
          'status': 'gray_study_not_received', 'art_accepted': False,
          'full_motorcycle_finished': False}
(REVIEW / 'build-report.json').write_text(json.dumps(report, indent=2) + '\n')
if args.render:
    sys.path.insert(0, str(ROOT / 'tools'))
    from blender_component_camera_preflight import check_component_camera
    views = [
        ('whole-quarter-gray', (.35, -.90, .24), (0, 0, .055), .56, False, None),
        ('whole-opposite-gray', (-.25, -.90, -.03), (0, 0, .055), .56, False, None),
        ('opposite-interface-gray', (.10, -.18, .25), (0, 0, .195), .09, True, None),
        ('body-interface-gray', (.10, -.18, .065), (0, 0, -.003), .09, True, None),
        ('opposite-closure-isolated-gray', (.1, -.2, .29), (0, 0, .193), .065, False, new[0]),
        ('body-closure-isolated-gray', (.1, -.2, .09), (0, 0, -.001), .065, False, new[1]),
    ]
    for name, eye, target, scale, crop, isolated in views:
        for ob in originals + new:
            ob.hide_render = isolated is not None and ob != isolated
        camera.location = eye
        camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
        camera.data.type = 'ORTHO'
        camera.data.ortho_scale = scale
        bpy.context.view_layer.update()
        visible = [ob for ob in originals + new if not ob.hide_render]
        frame = check_component_camera(scene, visible, allow_crop=crop, margin=.005)
        png = REVIEW / (name + '.png')
        scene.render.image_settings.file_format = 'PNG'
        scene.render.filepath = str(png)
        bpy.ops.render.render(write_still=True)
        report['views'].append({'name': name, 'path': str(png.relative_to(ROOT)),
                                'sha256': sha(png), 'camera_matrix': [list(row) for row in camera.matrix_world],
                                'ortho_scale': scale, 'samples': scene.cycles.samples,
                                'renderer': 'Blender 4.3.2 Cycles CPU, no denoising',
                                'source_sha256': report['source_sha256'],
                                'protocol_sha256': report['builder_sha256'],
                                'color_management': {'view': scene.view_settings.view_transform,
                                                     'look': scene.view_settings.look,
                                                     'exposure_EV': scene.view_settings.exposure,
                                                     'gamma': scene.view_settings.gamma},
                                'frame_check': frame, 'actually_opened': False})
        (REVIEW / 'build-report.json').write_text(json.dumps(report, indent=2) + '\n')
assert sha(INPUT) == expected
assert before == {ob.name: signature(ob) for ob in originals}
print('SNS_GRAY_STUDY_COMPLETE', json.dumps(checks), flush=True)
