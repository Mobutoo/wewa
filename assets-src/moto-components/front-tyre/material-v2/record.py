"""Close the transfer STUDY; no production freeze/final96/receipt permitted.

The paired macros revealed inherited geometry debt. V3 must correct the form
and rebake if the surface changes. This manifest preserves V2 as evidence.
"""
from pathlib import Path
import hashlib,json
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/front-tyre-v2';D=R/'creative/research/front-tyre-material-v2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def rows(files):return[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(set(files))]
old=['front-tyre-v1.blend','front-tyre-inspection.glb','build.py','parameters.json']
hn=['README.md','requirements.txt','provenance.json','parameters.json','build.py','check_export.mjs','check_texture_data.py','camera_preflight.py','render_compare.py','render_whole_study.py','record.py','front-tyre-v2.blend','front-tyre-v2-inspection.glb','textures/original-rubber-baked-tangent-normal.png','textures/original-rubber-baked-metallic-roughness.png']
on=['transfer-preflight.json','checkpoint-bake-normal.json','checkpoint-bake-emit.json','material-build-report.json','material-geometry-preservation-check.json','geometry-material-buffer-check.json','texture-pixel-data-check.json','source-portability-check.json','comparison-render-report.json','material-transfer-review.json']
compare=['native-tread-detail','atlas-tread-detail','native-sidewall-detail','atlas-sidewall-detail','atlas-whole-quarter']
inputs=[H/n for n in hn]+[H.parent/n for n in old]+[R/'creative/reviews/front-tyre-v1/manifest.json']+[D/n for n in['README.md','material-transfer-plan-v1.json']]+[O/n for n in on]
for n in compare:inputs+=[O/('compare-'+n+'.'+ext)for ext in['png','json']]
s=sha(H/'front-tyre-v2.blend');g=sha(H/'front-tyre-v2-inspection.glb')
build=json.loads((O/'material-build-report.json').read_text());pres=json.loads((O/'material-geometry-preservation-check.json').read_text());check=json.loads((O/'geometry-material-buffer-check.json').read_text());port=json.loads((O/'source-portability-check.json').read_text());review=json.loads((O/'material-transfer-review.json').read_text())
assert build['source_sha256']==port['source_sha256']==review['source_sha256']==s and build['export_sha256']==pres['export_sha256']==check['export_sha256']==port['export_sha256']==review['export_sha256']==g
assert pres['all_oriented_triangle_corners_POSITION_N_UV0_and_world_matrix_exact']and pres['raw_indices_exact']and all(v['raw_exact']for v in pres['attributes'].values())
assert check['technical_passed']and not port['external_libraries']and port['saved_source_native_geometry_digest_matches']
assert review['geometry_rework_required']and not review['ready_for_final_candidate_views']and review['corrected_whole_worker_exit_code']==0 and review['study_completed_with_verified_checkpoints']
assert set(review['comparison_images_actually_read'])==set(compare)
for n in compare:
    cp=O/('compare-'+n+'.json');p=O/('compare-'+n+'.png');q=json.loads(cp.read_text())
    assert q['source_sha256']==s and q['export_sha256']==g and q['PNG_sha256']==sha(p)and q['samples']==24
    with Image.open(p)as im:assert im.size==(1400,1100)
out={'component_id':'MOTO-TYRE-FRONT-001','revision':'front-tyre-v2','source_sha256':s,'export_sha256':g,
 'scope':'Transfer study ONLY, no production/final96 receipt. Real baked original donor on unchanged legacy inspection; inherited visible junction steps/facets require G3 rework in distinctv3 and a fresh bake if geometry changes.',
 'files':rows(inputs),'historical_source_and_export_immutable':True,'geometry_tread_or_UV_modified':False,
 'new_physical_component':False,'production_candidate_ready':False,'final96_run':False,'geometry_rework_required':True,
 'exact_continuous_shader_or_mobile_received':False,'art_accepted':False}
freeze=O/'study-source-freeze.json'
if freeze.exists():assert json.loads(freeze.read_text())==out,'Never replace a closed study'
else:freeze.write_text(json.dumps(out,indent=2)+'\n')
manifest={**out,'files':rows(inputs+[freeze,O/'README.md']),'proof_ownership':'Explicit A author/source/transfer-study proofs and attributed legacy donor inputs; no ROOT independent/global proof capture.'}
(O/'study-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('FRONT_TYRE_V2_STUDY_ONLY_CLOSED',len(out['files']),len(manifest['files']),sha(O/'study-manifest.json'))
