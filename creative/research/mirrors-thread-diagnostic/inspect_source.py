"""Read-only audit of the original cosmetic stud sampling; never saves Blender files."""
import bpy, json, hashlib, math
from pathlib import Path
ROOT=Path('/workspace/wewa-github');HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for side,revision in [('left','v1'),('right','v2')]:
 folder=ROOT/'assets-src/moto-components/mirrors';source=folder/f'mirror-{side}-{revision}.blend';params=folder/('parameters-left.json' if side=='left' else 'parameters-right-v2.json');p=json.loads(params.read_text());digest=sha(source);mount=p['mount_boss_centre_world_m'];pitch=p['stud_thread_pitch_working_m'];bpy.ops.wm.open_mainfile(filepath=str(source));candidates=[o for o in bpy.data.objects if 'cosmetic helical stud construction' in o.name];objects=[]
 for ob in candidates:
  verts=[ob.matrix_world@v.co for v in ob.data.vertices];zs=sorted(set(round(v.z-mount[2],9)for v in verts));errors=[];phases=[]
  for v in verts:
   x,y,z=v.x-mount[0],v.y-mount[1],v.z-mount[2];theta=math.atan2(y,x)%math.tau;phase=((z+.004)/pitch-theta/math.tau)%1;value=1 if phase<.15 or phase>=.95 else 1-(phase-.15)/.30 if phase<.45 else 0 if phase<.65 else (phase-.65)/.30;r=.00335+.00065*value;errors.append(abs(math.hypot(x,y)-r));phases.append(min(abs(phase-t)for t in [.15,.45,.65,.95]))
  dz=[b-a for a,b in zip(zs,zs[1:])];objects.append({'object':ob.name,'vertices':len(verts),'axial_levels':len(zs),'axial_step_m_range':[min(dz),max(dz)],'analytic_profile_vertex_radius_error_max_m':max(errors),'crease_phase_distance_min_max':[min(phases),max(phases)],'explanation':'Vertices follow the intended analytic radial profile, but uniform Z rings are not aligned with its four helical slope break curves. Linear faces therefore cross creases; a correct radial value at vertices does not ensure a smooth or constant-width helical ridge.'})
 assert sha(source)==digest
 rows.append({'side':side,'source_path':str(source.relative_to(ROOT)),'source_sha256':digest,'pitch_working_m':pitch,'pitch_status':'Estimated cosmetic geometry, not a manufacturer specification','construction_objects':objects,'source_unchanged':True})
report={'schema':1,'scope':'Read-only construction audit after frozen optical v3 source; no mesh, normals, materials, export or saved image changed.','sources':rows,'observed_visual_reserve':'mirror-right-v2/base-close.png shows wavy/segmented bright thread below the nut. This audit tests a sampling cause, not an OEM shape.','next_conditional_method':'If revised, preserve the same estimated analytic profile/radius/pitch and place the four phase-break helices in mesh edges, with explicit closed runout/caps. Check full solid after union, actual triangle/UV areas, retained non-stud buffers, neutral/reflective closeups and mounting interfaces before final rendering.','limits':['The final Boolean mesh may also affect normals; this audit alone does not isolate every contribution to the saved render.','No OEM diameter/pitch/hand or mating-thread compatibility is established.','Do not infer artistic acceptance from this numerical inspection.'],'art_accepted':False}
(HERE/'source-audit.json').write_text(json.dumps(report,indent=2)+'\n');print('READ_ONLY_STUD_AUDIT',[(r['side'],len(r['construction_objects']))for r in rows])
