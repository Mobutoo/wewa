import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector,Euler
O=Path(__file__).resolve().parent;R=Path('/workspace/wewa');old=R/'assets-src/moto-components/passenger-footrest-rubber-jk113008-v1';metal=R/'assets-src/moto-components/passenger-footpeg-metal-v1';base=R/'creative/reviews/whole-exterior-coverage-v19/linked-parents-check.json';whole=json.loads(base.read_text());rows=[r for r in whole['parents']if r['source']in[str((old/'child-candidate.blend').relative_to(R)),str((metal/'child-candidate.blend').relative_to(R))]]
def matrix(r):return Matrix.Translation(Vector(r['translation_m']))@Euler(tuple(math.radians(x)for x in r['rotation_degrees']),'XYZ').to_matrix().to_4x4()
read={}
for key,p in [('rubber',old/'child-candidate.blend'),('metal',metal/'child-candidate.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(p));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'and not o.hide_render];ob=next(o for o in obs if ('JK113008'if key=='rubber'else'PASSENGER_PEG')in o.name);me=ob.data;me.calc_loop_triangles();read[key]=dict(source=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),object=ob.name,object_matrix=[list(x)for x in ob.matrix_world],vertices=[list(ob.matrix_world@v.co)for v in me.vertices],vertices_count=len(me.vertices),polygons=len(me.polygons),triangles=len(me.loop_triangles),uv_layers=[uv.name for uv in me.uv_layers],has_custom_normals=me.has_custom_normals)
results=[]
for side in ['LH','RH']:
 rubber=next(r for r in rows if r['key'].startswith(side)and'JK113008' in str(r.get('selected_objects')));peg=next(r for r in rows if r['key'].startswith(side)and'PASSENGER_PEG' in str(r.get('selected_objects')));M=matrix(rubber).inverted()@matrix(peg);points=[M@Vector(v)for v in read['metal']['vertices']];band=[p for p in points if .01<=p.x<=.09];missing=[p for p in band if 225<=math.degrees(math.atan2(p.z,p.y))%360<=315];results.append(dict(side=side,rubber_parent=rubber['key'],metal_parent=peg['key'],rubber_world_matrix=[list(x)for x in matrix(rubber)],metal_world_matrix=[list(x)for x in matrix(peg)],metal_to_rubber=[list(x)for x in M],relative_axis_dot=(M.to_3x3()@Vector((1,0,0))).dot(Vector((1,0,0))),metal_max_radial_in_body_m=max(math.hypot(p.y,p.z)for p in band),metal_max_radial_in_omitted_quarter_m=max(math.hypot(p.y,p.z)for p in missing),metal_points_in_omitted_quarter=len(missing)))
# Keep large vertex arrays out of public diagnosis; counts and actual transforms suffice.
for x in read.values():x.pop('vertices')
(O/'G2-pose-diagnosis.json').write_text(json.dumps(dict(base=str(base.relative_to(R)),base_sha256=hashlib.sha256(base.read_bytes()).hexdigest(),parent_count=whole['parent_count'],sources=read,sides=results,scope='Actual native metal transformed into each current rubber local frame before deciding shape change; no OEM seat/retention inferred'),indent=2))
print(json.dumps(results))
