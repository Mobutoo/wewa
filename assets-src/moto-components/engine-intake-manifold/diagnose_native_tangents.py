"""Bake original bounded cast grain in the source UV atlas; native glTF only.

No photograph pixels or normal/tangent buffer repair. The two maps are an
estimated representative finish, not metrology or an OEM material sample.
"""
from pathlib import Path
import bpy, json, hashlib, sys, math, array
import numpy as np

H=Path(__file__).resolve().parent; R=H.parents[2]
O=R/'creative/reviews/engine-intake-manifold-v1'; T=H/'textures'; T.mkdir(exist_ok=True)
P=json.loads((H/'parameters.json').read_text()); G=P['original_grain']
geometry=json.loads((H/'geometry-report.json').read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
stage=H/'engine-intake-manifold-v1-geometry.blend'
assert sha(stage)==geometry['source_sha256']
bpy.ops.wm.open_mainfile(filepath=str(stage))
s=bpy.context.scene; body=bpy.data.objects[geometry['geometry'][0]['name']]
datum=body.parent
def snapshot(o):
    m=o.data; m.calc_loop_triangles()
    return {'vertices':[list(v.co)for v in m.vertices],
            'triangles':[list(t.vertices)for t in m.loop_triangles],
            'corner_normals':[list(n.vector)for n in m.corner_normals],
            'matrix':[list(r)for r in o.matrix_world]}
protected_before={o.name:snapshot(o) for o in [body]}
bpy.ops.object.select_all(action='DESELECT'); body.hide_set(False); body.select_set(True)
bpy.context.view_layer.objects.active=body
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=G['packing_margin_fraction'],area_weight=0.,correct_aspect=True,scale_to_bounds=False)
bpy.ops.object.mode_set(mode='OBJECT')
m=body.data; m.uv_layers.active.name='Original cast grain source atlas v1'
m.calc_tangents(uvmap=m.uv_layers.active.name)
tangent_lengths=[loop.tangent.length for loop in m.loops]
tangent_unit_error=max(abs(v-1) for v in tangent_lengths)
tangent_normal_dot=max(abs(loop.tangent.dot(m.corner_normals[loop.index].vector))for loop in m.loops)
uv_rechart=[]

rows=[]
for poly in m.polygons:
    loops=[m.loops[i]for i in poly.loop_indices]
    errs=[(abs(l.tangent.length-1),abs(l.tangent.dot(m.corner_normals[l.index].vector)))for l in loops]
    if any(a>.001 or b>.001 for a,b in errs):
        ids=list(poly.vertices);v=[m.vertices[i].co for i in ids];lengths=[(v[(i+1)%3]-v[i]).length for i in range(3)]
        rows.append({'face':poly.index,'vertices':ids,'positions':[list(q)for q in v],'edges_m':lengths,'altitude_min_m':2*poly.area/max(lengths),'loop_tangent_errors':errs,'UV':[list(m.uv_layers.active.data[l.index].uv)for l in loops]})
report={'source_sha256':sha(stage),'bad_faces':rows,'bad_face_count':len(rows),'total_faces':len(m.polygons),'max_unit_error':tangent_unit_error,'max_dot_error':tangent_normal_dot,'tangents_modified':False}
D=Path('/workspace/wewa-assets/work-in-progress/engine-intake-manifold/native-tangent-diagnostic');D.mkdir(exist_ok=True)
(D/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
