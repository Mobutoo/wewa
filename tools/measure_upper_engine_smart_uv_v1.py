"""Bounded diagnostic only: rejected atlas -> Smart Project only -> OBJECT stats.

Run by root in Blender4.3.2. Does not save BLEND, bake, render, export or pack twice.
Default writes only small JSON/progress into a new private output directory.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys
import time

import bpy
import bmesh
import numpy as np

R = Path(__file__).resolve().parents[1]
PRIVATE = Path('/workspace/wewa-assets').resolve()
CASE = PRIVATE / 'work-in-progress/upper-engine-local-ao-diagnostic-v1/run-005'
EXPECTED_INPUT = '7017d79d4fb8d8279ba544173e0d9b3586346af90da2d59267d5ecf3c3ea0e25'
UV = 'UV_AO'


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for data in iter(lambda: stream.read(1 << 20), b''):
            h.update(data)
    return h.hexdigest()


def array(collection, prop, width, dtype=np.float32):
    out = np.empty(len(collection) * width, dtype=dtype)
    collection.foreach_get(prop, out)
    return out.reshape((-1, width)) if width > 1 else out


def ahash(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def emit(event, **fields):
    print(json.dumps({'event': event, **fields}), flush=True)


def atomic_json(path, value):
    tmp = path.with_suffix('.partial')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    tmp.replace(path)


def witness(obj):
    m = obj.data
    m.calc_loop_triangles()
    return {
        'mesh': m.name, 'world': [list(x) for x in obj.matrix_world],
        'basis': [list(x) for x in obj.matrix_basis],
        'parent': obj.parent.name if obj.parent else None,
        'positions': ahash(array(m.vertices, 'co', 3)),
        'edges': ahash(array(m.edges, 'vertices', 2, np.int32)),
        'loop_vertices': ahash(array(m.loops, 'vertex_index', 1, np.int32)),
        'polygon_starts': ahash(array(m.polygons, 'loop_start', 1, np.int32)),
        'polygon_totals': ahash(array(m.polygons, 'loop_total', 1, np.int32)),
        'triangle_loops': ahash(array(m.loop_triangles, 'loops', 3, np.int32)),
        'corner_normals': ahash(array(m.corner_normals, 'vector', 3)),
        'protected_UVs': {u.name: ahash(array(u.data, 'uv', 2)) for u in m.uv_layers if u.name != UV},
        'UV_names': [u.name for u in m.uv_layers],
        'render_UVs': [u.name for u in m.uv_layers if u.active_render],
    }


def quantiles(a):
    a = a[np.isfinite(a)]
    if not len(a):
        return None
    return dict(zip(['min', 'p01', 'p50', 'p99', 'max'],
                    [float(x) for x in np.quantile(a, [0, .01, .5, .99, 1])]))


def island_counts(mesh, uv):
    """Exact shared-mesh-edge UV continuity; no geometric UV coincidence merge.

    Also return count with flagged mesh seams cut, matching SmartProject's
    use_seams=True partition policy. No per-face output or tolerance welding.
    """
    nf = len(mesh.polygons)
    if nf == 0:
        return {'exact_UV_continuity': 0, 'exact_UV_continuity_and_mesh_seams': 0}
    starts = array(mesh.polygons, 'loop_start', 1, np.int32)
    totals = array(mesh.polygons, 'loop_total', 1, np.int32)
    assert np.array_equal(starts, np.r_[0, np.cumsum(totals[:-1])])
    nxt = np.arange(len(mesh.loops), dtype=np.int32) + 1
    nxt[starts + totals - 1] = starts
    lv = array(mesh.loops, 'vertex_index', 1, np.int32)
    le = array(mesh.loops, 'edge_index', 1, np.int32)
    faces = np.repeat(np.arange(nf, dtype=np.int32), totals)
    u = np.array(uv, dtype=np.float32, copy=True)
    u[u == 0] = 0  # Treat -0 and +0 as equal, like numeric UV equality.
    bits = u.view(np.uint32)
    forward = lv < lv[nxt]
    lo = np.where(forward[:, None], bits, bits[nxt])
    hi = np.where(forward[:, None], bits[nxt], bits)
    order = np.lexsort((hi[:, 1], hi[:, 0], lo[:, 1], lo[:, 0], le))
    keys = np.column_stack([le.astype(np.uint32), lo, hi])[order]
    finite = np.isfinite(u).all(axis=1) & np.isfinite(u[nxt]).all(axis=1)
    equal = np.all(keys[1:] == keys[:-1], axis=1)
    equal &= finite[order[1:]] & finite[order[:-1]]
    pairs = np.flatnonzero(equal)
    seams = array(mesh.edges, 'use_seam', 1, np.bool_)
    result = {}
    for cut, key in [(False, 'exact_UV_continuity'), (True, 'exact_UV_continuity_and_mesh_seams')]:
        parent = np.arange(nf, dtype=np.int32)
        size = np.ones(nf, dtype=np.int32)
        count = nf
        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = int(parent[a])
            return a
        for j in pairs:
            l, r = int(order[j]), int(order[j + 1])
            if cut and seams[le[l]]:
                continue
            a, b = find(int(faces[l])), find(int(faces[r]))
            if a != b:
                if size[a] < size[b]:
                    a, b = b, a
                parent[b] = a
                size[a] += size[b]
                count -= 1
        result[key] = int(count)
    result['definition'] = 'Same mesh edge and exactly equal endpoint UV values; no epsilon, no overlap merge.'
    return result


def stats(obj, with_islands):
    m = obj.data
    m.calc_loop_triangles()
    uv = array(m.uv_layers[UV].data, 'uv', 2)
    loops = array(m.loop_triangles, 'loops', 3, np.int32)
    p = uv[loops].astype(np.float64)
    ab, ac = p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]
    det = ab[:, 0] * ac[:, 1] - ab[:, 1] * ac[:, 0]
    finite = np.isfinite(p).all(axis=(1, 2)) & np.isfinite(det)
    absolute = np.abs(det)
    areas = absolute * .5
    bm = bmesh.new()
    try:
        bm.from_mesh(m)
        face_areas = np.asarray([f.calc_area() for f in bm.faces], dtype=np.float64)
    finally:
        bm.free()
    tri_faces = array(m.loop_triangles, 'polygon_index', 1, np.int32)
    small_faces = face_areas[tri_faces] <= 1e-12
    outside = finite & ((p < 0) | (p > 1)).any(axis=(1, 2))
    valid_uv = uv[np.isfinite(uv).all(axis=1)]
    row = {
        'object': obj.name, 'mesh': m.name,
        'UV_names': [u.name for u in m.uv_layers], 'active_UV_index': m.uv_layers.active_index,
        'active_UV_name': m.uv_layers.active.name if m.uv_layers.active else None,
        'render_UVs': [u.name for u in m.uv_layers if u.active_render],
        'object_scale': list(obj.scale), 'faces': len(m.polygons), 'triangles': len(loops),
        'local_BMesh_faces_le_1e_minus12': int(np.count_nonzero(face_areas <= 1e-12)),
        'local_BMesh_face_area_quantiles': quantiles(face_areas),
        'UV_exact_zero_triangles': int(np.count_nonzero(finite & (absolute == 0))),
        'UV_area_le_1e_minus18_triangles': int(np.count_nonzero(finite & (areas <= 1e-18))),
        'UV_abs_determinant_le_1e_minus18_triangles': int(np.count_nonzero(finite & (absolute <= 1e-18))),
        'threshold_note': 'Area=abs(det)/2; determinant threshold also reported unchanged to compare run005 epsilon convention.',
        'UV_nonfinite_triangles': int(np.count_nonzero(~finite)),
        'UV_zero_triangles_on_small_local_faces': int(np.count_nonzero(finite & (absolute == 0) & small_faces)),
        'UV_zero_triangles_on_local_faces_above_1e_minus12': int(np.count_nonzero(finite & (absolute == 0) & ~small_faces)),
        'strict_anomaly_union_det_le_1e_minus18_or_nonfinite_or_outside': int(np.count_nonzero((finite & (absolute <= 1e-18)) | ~finite | outside)),
        'UV_area_quantiles': quantiles(areas[finite]),
        'UV_positive_area_quantiles': quantiles(areas[finite & (areas > 0)]),
        'UV_bounds': {'min': valid_uv.min(axis=0).tolist(), 'max': valid_uv.max(axis=0).tolist()} if len(valid_uv) else None,
        'UV_triangles_outside_0_1': int(np.count_nonzero(outside)),
        'UV_islands': island_counts(m, uv) if with_islands else {'not_requested': True},
        'UV_AO_sha256': ahash(uv),
    }
    bad = np.flatnonzero(~finite | (absolute <= 1e-18))
    ids = bad[:3] if len(bad) else np.arange(min(3, len(loops)))
    samples = [{'triangle_index': int(i), 'polygon_index': int(m.loop_triangles[int(i)].polygon_index),
                'loops': loops[i].tolist(), 'local_BMesh_polygon_area': float(face_areas[tri_faces[i]]), 'UV_AO': p[i].tolist() if finite[i] else None,
                'signed_determinant': float(det[i]) if finite[i] else None,
                'UV_area': float(areas[i]) if finite[i] else None} for i in ids]
    return row, samples


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, default=CASE / 'prepare/FAILED-UV-INSPECTION-ONLY.blend')
    ap.add_argument('--spec', type=Path, default=CASE / 'executed-spec-v5.json')
    ap.add_argument('--output-dir', type=Path, default=CASE / 'smart-only-measurement-v1')
    ap.add_argument('--count-islands', action='store_true', help='Optional exact-edge island count; may be slower on dense meshes.')
    args = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    assert bpy.app.version[:3] == (4, 3, 2), bpy.app.version_string
    input_path, out = args.input.resolve(), args.output_dir.resolve()
    assert input_path.is_relative_to(PRIVATE) and out.is_relative_to(PRIVATE)
    assert input_path.name == 'FAILED-UV-INSPECTION-ONLY.blend'
    assert digest(input_path) == EXPECTED_INPUT, 'Different rejected copy: do not silently change the measurement input.'
    assert not out.exists(), 'Use a new private output directory; preserve previous evidence.'
    out.mkdir(parents=True)
    spec = json.loads(args.spec.read_text())
    protected_paths = [input_path, args.spec.resolve()]
    for x in spec['linked_libraries_expected']:
        p = (R / x['source']).resolve()
        assert digest(p) == x['sha256'], x['source']
        protected_paths.append(p)
    file_before = {str(p): digest(p) for p in sorted(set(protected_paths))}
    result = {'schema': 'wewa.smart-project-only-measurement.v1', 'status': 'running',
              'script_sha256': digest(__file__), 'input_sha256': EXPECTED_INPUT,
              'blender': bpy.app.version_string, 'source_files_before': file_before,
              'no_bake_export_save_or_second_pack': True, 'count_islands_requested': args.count_islands,
              'samples_limit': 'At most3fixed triangle examples per object with before/after values, no per-triangle anomaly list.',
              'before': [], 'after_smart_only': [], 'examples': {}, 'art_accepted': False}
    started = time.monotonic()
    try:
        emit('open_rejected_copy')
        bpy.ops.wm.open_mainfile(filepath=str(input_path))
        collection = bpy.data.collections[spec['collection']]
        objects = sorted((o for o in collection.all_objects if o.type == 'MESH' and not o.hide_render), key=lambda o: o.name)
        assert len(objects) == spec['physical_mesh_copies'] == 12
        assert len({o.data.as_pointer() for o in objects}) == 12, 'No shared mesh mutation.'
        assert all(o.library is None and o.data.library is None for o in objects), 'Only local derivative copies.'
        assert all(len(o.data.uv_layers) == 2 and o.data.uv_layers[1].name == UV for o in objects)
        before = {o.name: witness(o) for o in objects}
        result['protected_meshes_before'] = before
        for obj in objects:
            emit('stats_before', object=obj.name)
            row, samples = stats(obj, args.count_islands)
            result['before'].append(row)
            result['examples'][obj.name] = [{'triangle_index': s['triangle_index'], 'before': s} for s in samples]
        assert sum(r['triangles'] for r in result['before']) == 657316
        atomic_json(out / 'measurement.json', result)
        if bpy.context.object and bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        collection.hide_viewport = False
        for obj in objects:
            obj.hide_set(False)
            obj.hide_viewport = False
            obj.data.uv_layers.active_index = 1
            assert obj.data.uv_layers.active.name == UV
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        bpy.context.scene.tool_settings.use_uv_select_sync = False
        bpy.context.view_layer.update()
        assert bpy.ops.object.mode_set(mode='EDIT') == {'FINISHED'}
        try:
            edit_objects = list(bpy.context.objects_in_mode_unique_data)
            assert {o.name for o in edit_objects} == {o.name for o in objects}, 'Not all12copies in EDIT.'
            assert bpy.ops.mesh.select_all(action='SELECT') == {'FINISHED'}
            assert bpy.ops.uv.select_all(action='SELECT') == {'FINISHED'}
            edit_rows = []
            for obj in objects:
                bm = bmesh.from_edit_mesh(obj.data)
                assert all(f.select for f in bm.faces)
                assert bm.loops.layers.uv.active is not None and bm.loops.layers.uv.active.name == UV
                edit_rows.append({'object': obj.name, 'selected_faces': sum(f.select for f in bm.faces),
                                  'active_bmesh_UV': bm.loops.layers.uv.active.name})
                del bm  # Do not retain an edit-BMesh wrapper across mode exit.
            result['actual_edit_selection'] = edit_rows
            emit('smart_project_only_begin', angle_deg=66, island_margin=0)
            result['smart_operator_result'] = sorted(bpy.ops.uv.smart_project(
                angle_limit=math.radians(66), margin_method='SCALED', island_margin=0,
                area_weight=0, correct_aspect=True, scale_to_bounds=False))
            assert result['smart_operator_result'] == ['FINISHED']
        finally:
            if bpy.context.object and bpy.context.object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
        assert bpy.context.mode == 'OBJECT'
        emit('object_mode_before_any_second_pack')
        bpy.context.view_layer.update()
        after = {o.name: witness(o) for o in objects}
        result['protected_meshes_after'] = after
        result['protected_geometry_N_nonAO_UVs_exact'] = before == after
        assert before == after, 'Geometry/N/protectedUV conservation failed; no threshold relaxation.'
        for obj in objects:
            emit('stats_after_smart_only', object=obj.name)
            row, _ = stats(obj, args.count_islands)
            result['after_smart_only'].append(row)
            m = obj.data
            uv = array(m.uv_layers[UV].data, 'uv', 2).astype(np.float64)
            for sample in result['examples'][obj.name]:
                i = sample['triangle_index']
                tri = m.loop_triangles[i]
                p = uv[list(tri.loops)]
                ab, ac = p[1] - p[0], p[2] - p[0]
                det = float(ab[0] * ac[1] - ab[1] * ac[0])
                finite = np.isfinite(p).all() and math.isfinite(det)
                sample['after_smart_only'] = {'UV_AO': p.tolist() if finite else None,
                                               'signed_determinant': det if finite else None,
                                               'UV_area': abs(det) * .5 if finite else None}
        result['totals'] = {}
        for stage in ['before', 'after_smart_only']:
            keys = ['faces', 'triangles', 'local_BMesh_faces_le_1e_minus12', 'UV_exact_zero_triangles', 'UV_area_le_1e_minus18_triangles', 'UV_abs_determinant_le_1e_minus18_triangles', 'UV_nonfinite_triangles', 'UV_zero_triangles_on_small_local_faces', 'UV_zero_triangles_on_local_faces_above_1e_minus12', 'strict_anomaly_union_det_le_1e_minus18_or_nonfinite_or_outside']
            result['totals'][stage] = {k: sum(row[k] for row in result[stage]) for k in keys}
        result['status'] = 'measurement_complete_no_atlas_acceptance_claimed'
    except Exception as exc:
        result['status'] = 'failed_stop_no_repair'
        result['error'] = f'{type(exc).__name__}: {exc}'
        raise
    finally:
        result['elapsed_seconds'] = time.monotonic() - started
        file_after = {str(p): digest(p) for p in sorted(set(protected_paths))}
        result['source_files_after'] = file_after
        result['protected_disk_sources_exact'] = file_before == file_after
        atomic_json(out / 'measurement.json', result)
        assert file_before == file_after, 'A protected source file changed.'
        emit('measurement_end', status=result['status'], output=str(out / 'measurement.json'))


if __name__ == '__main__':
    main()
