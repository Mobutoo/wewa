"""Read a frozen Blender source and evaluate a real edge vertex under ordered rotations.

Run with Blender --background --threads 1 --python-exit-code 1 --python THIS --
--spec SPEC.json --out NEW.json. Does not export, render, or save the .blend.
Axes in SPEC are source-frame data, independent of the browser/catalog matrices.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Quaternion, Vector


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    root = Path(__file__).resolve().parents[1]
    spec_path = Path(args.spec).resolve()
    spec = json.loads(spec_path.read_text())
    source = root / spec['source']
    export = root / spec['export']
    output = Path(args.out).resolve()
    assert not output.exists(), 'Refuse to overwrite an existing witness'
    assert digest(source) == spec['source_sha256'], 'Unfrozen source'
    assert digest(export) == spec['export_sha256'], 'Unfrozen export'
    parameters = root / spec['source_parameters']
    assert digest(parameters) == spec['source_parameters_sha256']
    source_parameters = json.loads(parameters.read_text())
    rotations = spec['source_rotation_order']
    assert len(rotations) == 2 and len({r['control_id'] for r in rotations}) == 2
    axes = []
    for rotation in rotations:
        value = (source_parameters[rotation['parameter_property']]
                 if 'parameter_property' in rotation else rotation['axis_source'])
        axis = Vector(value)
        assert abs(axis.length - 1) < 1e-5, 'Source axis must be normalized'
        axes.append(axis.normalized())
    assert axes[0].cross(axes[1]).length > .1, 'Axes must be nonparallel'
    bpy.ops.wm.open_mainfile(filepath=str(source))
    pivot = bpy.data.objects[spec['pivot']]
    obj = bpy.data.objects[spec['witness_mesh']]
    assert obj.type == 'MESH'
    assert obj.name in bpy.data.collections[spec['collection']].all_objects
    ancestors = []
    parent = obj.parent
    while parent is not None:
        ancestors.append(parent)
        parent = parent.parent
    assert pivot in ancestors, 'Witness must actually belong to the moving head'
    assert not pivot.constraints and pivot.animation_data is None
    original_basis = pivot.matrix_basis.copy()
    original_mode = pivot.rotation_mode
    rest = original_basis.to_quaternion()
    # This source contract uses axes independently observed in source world space.
    # Reject a rotated/scaled pivot rather than silently treating them as local axes.
    basis = pivot.matrix_world.to_3x3()
    assert max(abs(basis[i][j] - (1 if i == j else 0))
               for i in range(3) for j in range(3)) < 1e-6
    pivot.rotation_mode = 'QUATERNION'
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()

    def evaluated_vertices():
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            return [v.co.copy() for v in mesh.vertices], evaluated.matrix_world.copy()
        finally:
            evaluated.to_mesh_clear()

    local_rest, matrix_rest = evaluated_vertices()
    # The specified mesh is the actual head edge seal, not an invented marker.
    # Choose its farthest real vertex for a strong lever arm under both rotations.
    centre = pivot.matrix_world.translation
    index = max(range(len(local_rest)),
                key=lambda i: ((matrix_rest @ local_rest[i]) - centre).length_squared)
    witness_local = local_rest[index]
    vertex_count = len(local_rest)

    def point_at(pose, reversed_order=False):
        pivot.matrix_basis = original_basis.copy()
        values = [Quaternion(axis, math.radians(float(pose[r['control_id']])))
                  for axis, r in zip(axes, rotations)]
        if reversed_order:
            values.reverse()
        pivot.rotation_quaternion = rest @ values[0] @ values[1]
        bpy.context.view_layer.update()
        coords, world = evaluated_vertices()
        assert len(coords) == vertex_count
        assert (coords[index] - witness_local).length < 1e-12
        return list(world @ coords[index])

    states = []
    try:
        for item in spec['poses']:
            pose = item['controls']
            assert set(pose) == {r['control_id'] for r in rotations}
            actual = point_at(pose)
            reverse = point_at(pose, True)
            states.append({'name': item['name'], 'controls': pose,
                           'evaluated_Blender_world_m': actual,
                           'reverse_order_Blender_world_m': reverse,
                           'order_separation_m': math.dist(actual, reverse)})
    finally:
        pivot.matrix_basis = original_basis
        pivot.rotation_mode = original_mode
        bpy.context.view_layer.update()
    assert digest(source) == spec['source_sha256']
    assert digest(export) == spec['export_sha256']
    report = {
        'schema': 'wewa.blender-rotation-witness.v1',
        'spec_sha256': digest(spec_path), 'source_sha256': digest(source),
        'export_sha256': digest(export),
        'source_parameters_sha256': digest(parameters),
        'extractor_sha256': digest(__file__),
        'Blender_version': bpy.app.version_string,
        'pivot': pivot.name, 'witness_mesh': obj.name,
        'source_evaluated_vertex_index': index,
        'source_evaluated_vertex_count': vertex_count,
        'source_vertex_local_m': list(witness_local),
        'selection': 'Farthest actual evaluated vertex of the explicitly named head edge seal',
        'source_axes': [{'control_id': r['control_id'], 'axis_Blender': list(a)}
                        for r, a in zip(rotations, axes)],
        'composition': 'restQuaternion @ sourceRotation[0] @ sourceRotation[1]',
        'states': states,
        'independent_of_browser_matrices': True,
        'rendered_or_exported_or_saved_source': False,
        'art_accepted': False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n')
    print('WEWA_SOURCE_ROTATION_WITNESS', json.dumps({
        'states': len(states), 'actual_source_vertex': index,
        'max_order_separation_m': max(s['order_separation_m'] for s in states)}))


if __name__ == '__main__':
    main()
