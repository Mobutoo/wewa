"""Freeze a new continuation child after explicit image reading and technical proofs."""
import subprocess,sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];name=sys.argv[1];O=R/'creative/reviews'/name;H=R/'assets-src/moto-components'/name
assert not (O/'delivery.json').exists(),'Frozen children must not be rewritten'
spec=json.loads((O/'production-spec.json').read_text());report=json.loads((O/'final-render-report.json').read_text());review=json.loads((O/'final-review.json').read_text())
assert len(report['views'])>=3 and all(v['samples']==96 for v in report['views'])
assert all(v['png']in review['views_read']for v in report['views'])
assert any(v['view']=='final-neutral-independent'for v in report['views'])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for v in report['views']:assert sha(O/v['png'])==v['png_sha256']
ind=json.loads((O/'independent-export-check.json').read_text());assert ind['gray_material_actual_geometry_normals_equal']
assert all(x['gltf_errors']==0 and all(m['boundary_edges']==0 and m['connected_components']==1 for m in x['meshes'])for x in ind['exports'])
source=json.loads((O/'source-geometry-check.json').read_text());assert source['source_reopened']and source['source_sha256']==sha(H/'child-candidate.blend')and source['export_sha256']==sha(H/'child-candidate.glb')
engine=json.loads((O/'inspection-v3/engine-check.json').read_text());assert not engine['page_errors']and not engine['http_failures']and len(engine['pixel_checks'])>=4
assert engine['exports'][0]['sha256']==sha(H/'child-candidate.glb')
subprocess.run([sys.executable,'tools/check_component_raw_exr_v2.py',name,'--width','900','--height','700'],cwd=R,check=True)
scripts=[*spec['scripts'],*spec['plans'],'tools/powertrain_completion_common.py','tools/powertrain_completion_render.py','tools/powertrain_completion_validate.mjs','tools/powertrain_completion_reopen_check.py','tools/check_component_raw_exr_v2.py','tools/powertrain_continuation_neutral96_v3.py','tools/powertrain_continuation_finish_v3.py','tools/powertrain_continuation_freeze_v3.py','tools/powertrain_continuation_capture_v2.py','tools/powertrain_continuation_openings_v2.mjs','tools/powertrain_continuation_lab_v2/index.html','tools/powertrain_continuation_lab_v2/review.js','tools/powertrain_continuation_lab_v2/catalog.json','tools/powertrain_continuation_lab_v2/provenance.json']
cmd=[sys.executable,'tools/powertrain_completion_freeze.py',name,spec['package'],spec['component'],name,'--child',spec['component']]
for p in dict.fromkeys(scripts):cmd.extend(['--script',p])
for p in spec['remaining']:cmd.extend(['--remaining',p])
subprocess.run(cmd,cwd=R,check=True);d=json.loads((O/'delivery.json').read_text());bad=[p['path']for p in d['files']if sha(R/p['path'])!=p['sha256']];assert not bad
indexpath=R/'creative/research/powertrain-completion-assigned14-v1/continuation-deliveries-v14.json'
index=json.loads(indexpath.read_text())if indexpath.exists()else{'schema':1,'scope':'Only new continuation children; prior345 frozen files untouched','children':[],'packages_complete':0,'art_accepted':False,'git_touched':False}
index['children'].append({'package':spec['package'],'revision':name,'delivery':str((O/'delivery.json').relative_to(R)),'delivery_sha256':sha(O/'delivery.json'),'catalog_fragment':str((O/'catalog-fragment.json').relative_to(R)),'files':len(d['files']),'native96_views':len(report['views']),'independent_neutral_read':True,'hash_mismatches':bad})
indexpath.write_text(json.dumps(index,indent=2)+'\n')
flat=[json.loads((R/x['catalog_fragment']).read_text())for x in index['children']];(indexpath.parent/'continuation-catalog-fragments-flat-v14.json').write_text(json.dumps(flat,indent=2)+'\n')
print(json.dumps(index['children'][-1]))
