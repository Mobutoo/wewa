"""Localize the single observed current-source crossing; no renders or saves."""
import bpy
import hashlib
import json
from pathlib import Path
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
source = ROOT / 'assets-src/moto-components/cockpit-current-review-v1/cockpit-current-review-v1.blend'
expected = json.loads((HERE / 'current-contact-checks.json').read_text())['assembly_source_sha256']
assert sha(source) == expected
bpy.ops.wm.open_mainfile(filepath=str(source))
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
objects = list(bpy.data.collections['MOTORCYCLE18_LINKED_REVIEW_COPIES'].all_objects)


def data(prefix):
    obj = next(o for o in objects if o.type == 'MESH' and o.name.startswith(prefix))
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles()
        vertices = [evaluated.matrix_world @ v.co for v in mesh.vertices]
        triangles = [tuple(t.vertices) for t in mesh.loop_triangles]
        return obj.name, vertices, triangles, BVHTree.FromPolygons(vertices, triangles, all_triangles=True)
    finally:
        evaluated.to_mesh_clear()


a = data('M18 [cockpit-cables] Visible ignition pigtail')
b = data('M18 [instruments-v3] Shaped central cluster cover')
pairs = a[3].overlap(b[3])
points = []
for i, j in pairs:
    ta = [a[1][k] for k in a[2][i]]
    tb = [b[1][k] for k in b[2][j]]
    for edges, target in [(ta, tb), (tb, ta)]:
        for k in range(3):
            start, end = edges[k], edges[(k + 1) % 3]
            direction = end - start
            if direction.length < 1e-12:
                continue
            point = intersect_ray_tri(*target, direction.normalized(), start, True)
            if point is not None and -1e-8 <= (point - start).dot(direction.normalized()) <= direction.length + 1e-8:
                if not any((point - p).length < 1e-7 for p in points):
                    points.append(point)
assert len(pairs) == 32 and points
report = {'schema': 'wewa.cockpit-pigtail-intersection-localization.v1',
          'assembly_source_sha256': expected, 'tool_sha256': sha(__file__),
          'a': a[0], 'b': b[0], 'triangle_pair_count': len(pairs),
          'actual_triangle_pairs': [list(p) for p in pairs],
          'segment_triangle_intersection_points_Blender_world_m': [list(p) for p in points],
          'intersection_point_bounds_Blender_world_m': {
              'min': [min(p[k] for p in points) for k in range(3)],
              'max': [max(p[k] for p in points) for k in range(3)]},
          'scope': 'Surface intersection of the digital candidates, not minimum clearance or OEM shape error.',
          'source_modified_or_rendered': False, 'art_accepted': False}
assert sha(source) == expected
out = HERE / 'pigtail-crossing-localization.json'
assert not out.exists()
out.write_text(json.dumps(report, indent=2) + '\n')
print('PIGTAIL_INTERSECTION_LOCALIZED', len(points), report['intersection_point_bounds_Blender_world_m'])
