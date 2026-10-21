"""Conditional dimensional comparisons; no contact solve or real-bike fit claim."""
import json, hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/fork-bellows-v2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=json.loads((HERE/'parameters.json').read_text());s=json.loads((OUT/'source-geometry-check.json').read_text());g=json.loads((OUT/'geometry-check.json').read_text())
assert g['technical_passed'] and s['export_sha256']==g['sha256']==sha(HERE/'fork-bellows-v2-inspection.glb')
# These radii were probed against the actual exported triangles in each of five states.
base=g['actual_morph_states'][0];probes={q['label']:q for q in base['actual_buffer_probes']}
entry=probes['entryradialsection']['nearest'];seat=probes['innerradialseat']['nearest'];col=.024
r={'source_sha256':s['source_sha256'],'export_sha256':g['sha256'],'related_outer_left_source_sha256':sha(ROOT/'assets-src/moto-components/front-fork/outer-left/fork-outer-left-v1.blend'),'method':'Radial section probes of actual exported triangles; comparing authored free dimensions under conditional coaxial overlay, not an installed-pose/contact simulation. No geometry adjusted to impose fit.','lower_entry_radius_m_actual_buffer':entry,'lower_chamber_radius_m_actual_buffer':seat,'outer_leg_neck_radius_m_estimated':col,'entry_minus_neck_radial_m':entry-col,'chamber_minus_neck_radial_m':seat-col,'conditional_result':'Unstrained entry remains about1mm radially smaller than the authored48mm neck. Chamber has about0.5mm radial clearance if aligned. Axial insertion, contact lip role and elastic stretch remain unknown. Neither a forced-fit nor real-motorcycle incompatibility is demonstrated.','all_metric_dimensions_estimated':True,'five_length_states_buffer_checked':len(g['actual_morph_states'])==5,'lower_lip_unchanged_in_length_morphs':s['lower_lip_identical_across_length_morphs'],'manufacturer_suspension_travel_verified':False,'upper_collar_fabricated_here':False,'installed_pose_verified':False,'art_accepted':False}
(OUT/'conditional-interface-check.json').write_text(json.dumps(r,indent=2)+'\n')
old=json.loads((OUT/'v1-preservation-start.json').read_text());assert sha(ROOT/old['v1_manifest_path'])==old['v1_manifest_sha256'];rows=[]
for row in old['files']:
 actual=sha(ROOT/row['path']);assert actual==row['sha256'],row['path'];rows.append({'path':row['path'],'sha256':actual})
(OUT/'v1-preservation-end.json').write_text(json.dumps({'v1_manifest_path':old['v1_manifest_path'],'v1_manifest_sha256':old['v1_manifest_sha256'],'all_files_verified_unchanged':True,'files':rows},indent=2)+'\n')
print('Conditional entry/neck radial comparison',entry-col,seat-col,'v1 files unchanged',len(rows))
