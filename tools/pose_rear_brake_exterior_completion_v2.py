"""G2 rigid pose correction only; original frozen candidate untouched."""
import bpy,json,math,sys,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path('/workspace/wewa');K='rear-brake-exterior-completion-v1';H=R/'assets-src/moto-components'/K/'pose-correction-v2';O=R/'creative/reviews'/K/'pose-correction-v2';D=R/'creative/research'/K/'pose-correction-v2';oldH=H.parent
sys.path.insert(0,str(R/'tools'));from powertrain_completion_common_open_v1 import digest,look
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def basis(x,z):
 x=Vector(x).normalized();z=Vector(z);z=(z-x*x.dot(z)).normalized();y=z.cross(x).normalized();return Matrix((x,y,z)).transposed().to_4x4()
bpy.ops.wm.open_mainfile(filepath=str(oldH/'rear-brake-exterior.blend'));bpy.context.preferences.filepaths.save_version=0
P=json.loads((oldH/'parameters.json').read_text());A=Vector(P['rod_start_lug_hole_m']);B=Vector(P['lever_barrel_world_m']);C=Vector(P['cam_bore_world_m']);d=(B-A).normalized();u=(B-C).normalized();N=u.cross(d).normalized()
if N.x>0:N=-N
objs=[bpy.data.objects[name]for name in P['objects']];before={o.name:dict(mesh_digest=digest(o.data),matrix=[list(r)for r in o.matrix_world])for o in objs}
lever=bpy.data.objects['JW131601_OBSERVED_CURVED_STRAP_AND_DOUBLE_EYES'];barrel=bpy.data.objects['RBE_BRAKE_ROD_BARREL_PIN'];stub=bpy.data.objects['RBE_EXPOSED_CAM_SHAFT_STUB_ONLY']
lever.matrix_world=basis(u,N);lever.matrix_world.translation=C
barrel.matrix_world=basis(d,N);barrel.matrix_world.translation=B-N*.010
# Same unchanged shaft mesh, rotate rigidly around exterior cam datumC.
Q=Vector((-1,0,0)).rotation_difference(N).to_matrix().to_4x4();stub.matrix_world=Matrix.Translation(C)@Q@Matrix.Translation(-C)@stub.matrix_world
for o in objs:assert digest(o.data)==before[o.name]['mesh_digest']
P.update(pose_revision='v2',common_lever_barrel_normal=list(N),scope='G2 rigid poses only: lever and barrel normals common; rod straight and unchanged; shaft stub same mesh rigidly aligned to common normal. No new shape, hidden joint or spline. Panel/pedal source poses remain unchanged.',art_accepted=False,mechanical_fit_received=False)
write(H/'parameters.json',P);bpy.ops.wm.save_as_mainfile(filepath=str(H/'rear-brake-exterior-pose-v2.blend'),compress=True)
bpy.ops.object.select_all(action='DESELECT')
for o in objs:o.select_set(True)
bpy.context.view_layer.objects.active=lever;bpy.ops.export_scene.gltf(filepath=str(H/'rear-brake-exterior-pose-v2.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_tangents=False)
f=json.loads((oldH/'integration-fragment.json').read_text())
for row in f['additions']:row.update(source=str((H/'rear-brake-exterior-pose-v2.blend').relative_to(R)),sha256=sha(H/'rear-brake-exterior-pose-v2.blend'))
f['pose_revision']='v2';f['replaces_candidate_fragment_only']=str((oldH/'integration-fragment.json').relative_to(R));write(H/'integration-fragment.json',f)
routes=[dict(key=r['key'],source_blend=r['source'],glb=str((H/'rear-brake-exterior-pose-v2.glb').relative_to(R)),selected_objects=r['selected_objects'])for r in f['additions']];write(D/'export-routes.json',dict(rows=routes));write(D/'new-parents-only.json',dict(parents=f['additions']))
# Exact axes/centres and source mesh invariance, not just nominal object names.
def angle(a,b):return math.degrees(math.acos(max(-1,min(1,abs(Vector(a).normalized().dot(Vector(b).normalized()))))))
assert (lever.matrix_world@Vector((.09,0,0))-B).length<1e-7
assert (barrel.matrix_world@Vector((0,0,.01))-B).length<1e-7
assert lever.matrix_world.to_3x3().col[2].cross(barrel.matrix_world.to_3x3().col[2]).length<1e-6
assert barrel.matrix_world.to_3x3().col[0].cross(d).length<1e-6
# Inspect actual triangle surface crossings at changed mating interfaces.
from mathutils.bvhtree import BVHTree
def tree(o):
 m=o.data;m.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(t.vertices)for t in m.loop_triangles],all_triangles=True,epsilon=0)
panel=next(o for o in bpy.context.scene.objects if o.name.startswith('CONTEXT_ONLY_DS151069'))
pairs=[]
for a,b in [(lever,barrel),(lever,stub),(stub,panel)]:
 crosses=tree(a).overlap(tree(b));pairs.append(dict(a=a.name,b=b.name,actual_surface_triangle_crossings=len(crosses)))
assert pairs[0]['actual_surface_triangle_crossings']==0,pairs
assert pairs[1]['actual_surface_triangle_crossings']==0,pairs
write(O/'G2-pose-check.json',dict(before=before,after={o.name:dict(mesh_digest=digest(o.data),matrix=[list(r)for r in o.matrix_world])for o in objs},all_meshes_exactly_unchanged=True,rod_unchanged=before['RBE_PF161001_ESTIMATED_INSTALLED_ROD']['matrix']==[list(r)for r in bpy.data.objects['RBE_PF161001_ESTIMATED_INSTALLED_ROD'].matrix_world],common_axis_angle_deg=angle(lever.matrix_world.to_3x3().col[2],barrel.matrix_world.to_3x3().col[2]),barrel_axis_dot_rod=d.dot(N),lever_cam_datum_m=list(C),lever_barrel_datum_m=list(B),triangles=pairs,mechanical_fit_received=False,art_accepted=False))
