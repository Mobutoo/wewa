"""Read an exact catalogued Blender collection without saving or changing it."""
import argparse
import bmesh
import bpy
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('asset')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
config = json.loads((ROOT / 'tools/motorcycle-lab/catalog.json').read_text())['assets'][args.asset]
source = ROOT / 'assets-src/moto-components' / config['source']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = sha(source)
bpy.ops.wm.open_mainfile(filepath=str(source))
bpy.context.view_layer.update()
collection = bpy.data.collections[config['collection']]
objects = [o for o in collection.all_objects if o.type == 'MESH' and not o.hide_render]
assert objects, 'Empty component collection'
rows = []
for ob in objects:
    evaluated = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    mesh.calc_loop_triangles()
    coordinates = [ob.matrix_world @ v.co for v in mesh.vertices]
    assert all(math.isfinite(x) for v in coordinates for x in v)
    areas = [((coordinates[t.vertices[1]] - coordinates[t.vertices[0]]).cross(
        coordinates[t.vertices[2]] - coordinates[t.vertices[0]])).length / 2
        for t in mesh.loop_triangles]
    assert areas and min(areas) > 0
    bm = bmesh.new()
    bm.from_mesh(mesh)
    manifold_errors = sum(not e.is_manifold for e in bm.edges)
    volume = bm.calc_volume(signed=True)
    bm.free()
    assert manifold_errors == 0 and volume > 0, (ob.name, manifold_errors, volume)
    rows.append({'object': ob.name, 'vertices': len(mesh.vertices),
                 'triangles': len(mesh.loop_triangles),
                 'minimum_triangle_area_world_m2': min(areas),
                 'non_manifold_edges': manifold_errors,
                 'signed_volume_local_m3': volume,
                 'world_matrix': [list(row) for row in ob.matrix_world],
                 'bounds_world_m': [[min(v[k] for v in coordinates), max(v[k] for v in coordinates)]
                                    for k in range(3)]})
    evaluated.to_mesh_clear()
assert sha(source) == before
report = {'schema': 1, 'asset': args.asset, 'revision': config['review'],
          'source_sha256': before, 'source': str(source.relative_to(ROOT)),
          'checker': str(Path(__file__).relative_to(ROOT)), 'checker_sha256': sha(Path(__file__)),
          'blender_version': bpy.app.version_string, 'read_only_source_unchanged': True,
          'collection': config['collection'], 'objects': rows,
          'scope': 'Evaluated visible source meshes: finite vertices, nonzero triangle areas, '
                   'closed edges and positive local volume. No self-intersection, wall-thickness, '
                   'OEM variant, installed-fit, artistic or device-performance certification.',
          'art_accepted': False}
target = ROOT / 'creative/reviews' / config['review'] / 'source-geometry-check.json'
target.write_text(json.dumps(report, indent=2) + '\n')
print('READ_ONLY_SOURCE_CHECK', args.asset, sum(r['triangles'] for r in rows), flush=True)
