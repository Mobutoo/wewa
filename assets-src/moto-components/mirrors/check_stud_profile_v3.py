"""Read-only actual final-source ray witness at the existing helical slope breaks."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/mirror-right-v3';P=json.loads((HERE/'parameters-right-v3.json').read_text());mount=Vector(P['mount_boss_centre_world_m']);pitch=P['stud_thread_pitch_working_m'];rows=[]
for rev in ['v2','v3']:
 path=HERE/f'mirror-right-{rev}.blend';digest=hashlib.sha256(path.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(path));ob=bpy.data.objects['RH continuous steel stem ball and cosmetic stud - candidate'];ob.data.calc_loop_triangles();tree=BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[tuple(t.vertices)for t in ob.data.loop_triangles],all_triangles=True);samples=[]
 for k in range(144):
  u=k/144;direction=Vector((math.cos(u*math.tau),math.sin(u*math.tau),0))
  for turn in range(-1,9):
   for phase,r in [(.15,.004),(.45,.00335),(.65,.00335),(.95,.004)]:
    q=-.004+pitch*(turn+phase+u)
    if not -.0039<q<.0058:continue
    hit,normal,face,distance=tree.ray_cast(mount+Vector((0,0,q))+direction*.010,-direction,.020);assert hit is not None
    actual=(hit-(mount+Vector((0,0,q)))).dot(direction);samples.append({'u':u,'turn':turn,'phase_break':phase,'q_m':q,'expected_radius_m':r,'actual_source_ray_radius_m':actual,'absolute_error_m':abs(actual-r)})
 maxrow=max(samples,key=lambda r:r['absolute_error_m']);rms=(sum(r['absolute_error_m']**2 for r in samples)/len(samples))**.5;rows.append({'revision':rev,'source_sha256':digest,'actual_final_body':ob.name,'sample_count':len(samples),'max_radius_error_m':maxrow['absolute_error_m'],'RMS_radius_error_m':rms,'worst_witness':maxrow});assert hashlib.sha256(path.read_bytes()).hexdigest()==digest
assert rows[1]['max_radius_error_m']<2e-7 and rows[0]['max_radius_error_m']>1e-5,rows
report={'source_sha256':rows[1]['source_sha256'],'baseline_source_sha256':rows[0]['source_sha256'],'method':'Actual final CSG body radial BVH rays at all four existing profile-break helices, 144 azimuths and visible lower stud range q=-3.9..5.8mm. No source saved; no render or material change.','sampled_sources':rows,'interpretation':'Phase-aligned sampling removes radial interpolation error along the old intended helical break curves; this verifies actual final CSG geometry, not manufacturer dimensions or final appearance.','limits':['Ray radius witness at these samples does not prove every normal or triangle between them.','Profile, diameter, pitch, hand and mounting remain estimated, not qualified threads.','Preview diffuse/reflection reading still required.'],'art_accepted':False};(OUT/'stud-profile-ray-check.json').write_text(json.dumps(report,indent=2)+'\n');print('STUD_PROFILE_ACTUAL_FINAL',[(r['revision'],r['sample_count'],r['max_radius_error_m'])for r in rows])
