"""Preserve the frozen clamp geometry; derive a separate lateral registration study.

blender --background --threads 2 --python-exit-code 1 --python tools/build_handlebar_registration_v2.py
"""
import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets-src/moto-components/handlebar-registration-v2'
REVIEW = ROOT / 'creative/reviews/handlebar-registration-v2'
PLAN = ROOT / 'creative/research/handlebar-registration-v2/plan.json'
COLLECTION = 'WEWA_HANDLEBAR_CLAMPS_SEPARATE_PARTS'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def geometry(obj):
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    mesh.calc_loop_triangles()
    vertices = [obj.matrix_world @ v.co for v in mesh.vertices]
    faces = [tuple(t.vertices) for t in mesh.loop_triangles]
    evaluated.to_mesh_clear()
    return vertices, faces


def tree(obj):
    vertices, faces = geometry(obj)
    return BVHTree.FromPolygons(vertices, faces, all_triangles=True, epsilon=0)


def main():
    plan = json.loads(PLAN.read_text())
    parents = {p['key']: p for p in json.loads((ROOT / 'creative/research/motorcycle-exterior-v5/parents.json').read_text())['parents']}
    inputs = {str(PLAN.relative_to(ROOT)): sha(PLAN)}
    for key in ['clamps', 'handlebar', 'steering-upper']:
        row = parents[key]
        assert sha(ROOT / row['source']) == row['sha256'], row['source']
        inputs[row['source']] = row['sha256']
    assert inputs[plan['source_component']] == plan['source_sha256']
    OUT.mkdir(parents=True, exist_ok=True)
    REVIEW.mkdir(parents=True, exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / plan['source_component']))
    objects = list(bpy.data.collections[COLLECTION].all_objects)
    assert len(objects) == 8 and all(o.type == 'MESH' for o in objects)
    changes = []
    for obj in objects:
        old = obj.location.copy()
        side = 1 if ' clamp L ' in obj.name else -1 if ' clamp R ' in obj.name else 0
        assert side and abs(old.x - side * .045) < 1e-7, obj.name
        obj.location.x -= side * plan['translation_per_side_m']
        obj['registration_status'] = plan['dimension_status']
        changes.append({'name': obj.name, 'before_m': list(old), 'after_m': list(obj.location)})
    bpy.context.scene['registration_plan'] = str(PLAN.relative_to(ROOT))
    bpy.context.scene['art_accepted'] = False
    bpy.ops.file.pack_all()
    candidate = OUT / 'handlebar-registration-v2.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(candidate), compress=True)

    # Independent context built from the actual editable collections, without
    # rerunning historical generators or modifying their source geometry.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1
    context_objects = {}
    for key in ['clamps', 'handlebar', 'steering-upper']:
        row = parents[key]
        source = candidate if key == 'clamps' else ROOT / row['source']
        with bpy.data.libraries.load(str(source), link=False) as (available, loaded):
            assert row['collection'] in available.collections
            loaded.collections = [row['collection']]
        collection = loaded.collections[0]
        scene.collection.children.link(collection)
        parent = bpy.data.objects.new('PARENT [' + key + ']', None)
        scene.collection.objects.link(parent)
        parent.location = row['translation_m']
        parent.rotation_euler = [math.radians(v) for v in row['rotation_degrees']]
        parent.scale = row['scale']
        for obj in collection.all_objects:
            if obj.parent is None:
                obj.parent = parent
        context_objects[key] = [o for o in collection.all_objects if o.type == 'MESH']
    bpy.context.view_layer.update()
    assert len(context_objects['steering-upper']) == 1
    plate = tree(context_objects['steering-upper'][0])
    collisions = []
    for obj in context_objects['clamps']:
        if ' lower' not in obj.name:
            continue
        corrected = len(plate.overlap(tree(obj)))
        original = obj.location.copy()
        side = 1 if ' clamp L ' in obj.name else -1
        obj.location.x += side * plan['translation_per_side_m']
        bpy.context.view_layer.update()
        previous = len(plate.overlap(tree(obj)))
        obj.location = original
        bpy.context.view_layer.update()
        collisions.append({'name': obj.name, 'old_intersecting_triangle_pairs': previous,
                           'candidate_intersecting_triangle_pairs': corrected})
    assert len(collisions) == 2
    assert all(r['old_intersecting_triangle_pairs'] > 0 for r in collisions), collisions
    assert all(r['candidate_intersecting_triangle_pairs'] == 0 for r in collisions), collisions

    # A compact native context, with packed textures and explicitly bounded scope.
    scene['scope'] = 'P28 lateral registration only; no fitted lower hardware stack or measured OEM fit'
    scene['art_accepted'] = False
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 24
    scene.cycles.use_denoising = False
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = 2
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 760
    scene.render.resolution_percentage = 100
    scene.world = bpy.data.worlds.new('Neutral review world')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.18, .22, .28, 1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value = .5
    target = Vector((0, -.0975, -.025))
    for name, position, power, size in [('Key', (.2, -.3, .4), 12, .3), ('Fill', (-.3, .1, .2), 8, .3)]:
        data = bpy.data.lights.new(name, 'AREA')
        data.energy = power
        data.shape = 'DISK'
        data.size = size
        obj = bpy.data.objects.new(name, data)
        scene.collection.objects.link(obj)
        obj.location = position
        obj.rotation_euler = (target - obj.location).to_track_quat('-Z', 'Y').to_euler()
    camera = bpy.data.objects.new('Review camera', bpy.data.cameras.new('Review camera'))
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = .24
    camera.data.clip_start = .001
    camera.data.clip_end = 10
    camera.location = (.17, .17, -.15)
    camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.ops.file.pack_all()
    context = OUT / 'registration-context.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(context), compress=True)
    report = {'schema': 1, 'input_sha256': inputs, 'tool_sha256': sha(Path(__file__)),
              'source': str(candidate.relative_to(ROOT)), 'source_sha256': sha(candidate),
              'context': str(context.relative_to(ROOT)), 'context_sha256': sha(context),
              'changes': changes, 'native_triangle_intersections': collisions,
              'art_accepted': False, 'complete_fastener_stack': False,
              'scope': 'Triangle surface intersection of the native lower saddles/studs and plate; no solid containment, preload or dimensional certification.'}
    (REVIEW / 'native-check.json').write_text(json.dumps(report, indent=2) + '\n')
    for relative, expected in inputs.items():
        assert sha(ROOT / relative) == expected, relative
    print('REGISTRATION_NATIVE_CHECK', json.dumps(collisions), flush=True)


if __name__ == '__main__':
    main()
