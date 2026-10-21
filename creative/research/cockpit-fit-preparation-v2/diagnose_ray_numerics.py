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


A=world_data(find('cockpit-cables','Visible ignition pigtail'))
B=world_data(find('instruments-v3','Shaped central cluster cover'))
p=A['vertices'][5959];d=Vector((-.2713,.8917,.3629)).normalized();traces=[]
for step in [1e-8,1e-7,1e-6]:
 origin=p.copy();hits=[]
 for i in range(15):
  loc,n,face,dist=B['tree'].ray_cast(origin,d,5.)
  if loc is None:break
  hits.append({'triangle':face,'distance_from_previous_origin':dist,'point':list(loc)})
  origin=loc+d*step
 traces.append({'step_m':step,'hits':hits})
(HERE/'ray-numerics-diagnostic.json').write_text(json.dumps({'point_vertex5959_world_m':list(p),'direction':list(d),'traces':traces},indent=2)+'\n')
print('RAY_NUMERICS',traces,flush=True)
