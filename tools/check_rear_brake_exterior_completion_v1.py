import bpy,bmesh,json,math,sys,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');K='rear-brake-exterior-completion-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K
bpy.ops.wm.open_mainfile(filepath=str(H/'rear-brake-exterior.blend'));P=json.loads((H/'parameters.json').read_text());rows=[]
for name in P['objects']:
 ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);unseen=set(bm.verts);counts=[]
 while unseen:
  q=[unseen.pop()];count=0
  while q:
   v=q.pop();count+=1
   for e in v.link_edges:
    w=e.other_vert(v)
    if w in unseen:unseen.remove(w);q.append(w)
  counts.append(count)
 bm.free();assert len(counts)==1,(name,counts);rows.append(dict(object=name,connected_components=1))
A=Vector(P['rod_start_lug_hole_m']);B=Vector(P['lever_barrel_world_m']);clevis=bpy.data.objects['RBE_BRAKE_ROD_CLEVIS'];barrel=bpy.data.objects['RBE_BRAKE_ROD_BARREL_PIN'];pin=bpy.data.objects['RBE_BRAKE_LINKAGE_HEADED_PIN'];lever=bpy.data.objects['JW131601_OBSERVED_CURVED_STRAP_AND_DOUBLE_EYES']
errors=dict(clevis_eye_to_lug_m=(clevis.matrix_world@Vector((.020,0,0))-A).length,barrel_centre_to_lever_eye_m=(barrel.matrix_world@Vector((0,0,.010))-B).length,lever_eye_to_barrel_m=(lever.matrix_world@Vector((.09,0,0))-B).length)
assert max(errors.values())<2e-7
angle=math.degrees(math.acos(min(1,abs(barrel.matrix_world.to_3x3().col[2].normalized().dot(lever.matrix_world.to_3x3().col[2].normalized())))))
proof=dict(objects=rows,actual_saved_native_reopened=True,endpoint_registration_errors=errors,rod_barrel_axis_deviation_deg=math.degrees(math.acos(min(1,abs(barrel.matrix_world.to_3x3().col[0].normalized().dot(Vector(P['rod_direction']).normalized()))))),barrel_to_lever_fork_axis_angle_deg=angle,source_estimate_limits=['Spring/nut seat and fork nominal contacts are estimated; no operating travel checked','Barrel tilt relative to lever eyes about5degrees: tiny nominal edge overlaps possible at fork eye depending thickness; not a machined fit certificate','Current pedal and panel poses are historical bounded context, not measured assembled endpoints'],mechanical_fit_passed=False,art_accepted=False,all_dimensions_estimated=True)
(O/'native-registration-check.json').write_text(json.dumps(proof,indent=2)+'\n')
