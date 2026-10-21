"""Freeze only one new front10 child and flat sidecars. No shared registers or Git."""
from pathlib import Path
import json,hashlib,sys
R=Path('/workspace/wewa');K,stem=sys.argv[1:3];H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=json.loads((O/'child-plan.json').read_text());review=json.loads((O/'visual-review.json').read_text());assert len(review['native96_images_actually_read'])>=6
raw=json.loads((O/'raw-check.json').read_text());assert len(raw['files'])>=6
for stage in ['gray','material']:
 p=H/(stem+'-'+stage+'.glb');d=json.loads(Path(str(p)+'.validator.json').read_text());assert d['issues']['numErrors']==d['issues']['numWarnings']==0;d=json.loads(Path(str(p)+'.buffers.json').read_text());assert d['triangles_at_or_below_1e18_m2']==d['bad_normal_lengths']==0
par=json.loads((O/'material-parity.json').read_text());assert par['binary_geometry_equal'] and par['mesh_accessors_nodes_equal']
reports=[]
for stage in ['gray','material']:
 rp=O/(stage+'-96')/'render-report.json';d=json.loads(rp.read_text());assert len(d['views'])>=3;assert d['source_sha256']==sha(R/d['source'])
 for v in d['views']:
  assert v['samples']==96
  for n in ['PNG','EXR']:v[n+'_sha256']=sha(R/v[n])
 reports.append(d)
(O/'render-report.json').write_text(json.dumps({'component_id':plan['component_id'],'package':plan['package'],'revision':K,'stages':reports,'views':[v for d in reports for v in d['views']],'native96_pair_count':len(raw['files']),'art_accepted':False,'mounted_fit':False},indent=2))
source=H/(stem+'-material.blend');meta=json.loads((O/'material-source-metadata.json').read_text());assert meta['source_sha256']==sha(source)
asset={'component_id':plan['component_id'],'package':plan['package'],'revision':K,'label':plan['child'],'source':str(source.relative_to(R)),'source_sha256':sha(source),'collection':'Scene Collection','collection_kind':'scene_root','source_objects':list(meta['mesh_objects']),'files':[K+'/'+stem+'-material.glb'],'review':K,'render_report':str((O/'render-report.json').relative_to(R)),'details':plan['scope'],'package_complete':False,'art_accepted':False,'mounted_fit':False}
(O/'catalog-fragment.json').write_text(json.dumps(asset,indent=2))
delivery={**plan,'revision':K,'new_geometry':True,'state':'Bounded related isolated exterior, gray and clean material hypothesis reviewed','source':asset['source'],'gray_source':str((H/(stem+'-gray.blend')).relative_to(R)),'catalog_fragment':str((O/'catalog-fragment.json').relative_to(R)),'render_report':str((O/'render-report.json').relative_to(R)),'native96_pairs':len(raw['files']),'actual_babylon':'Not executed; coordinator standalone inspection pending','material_hypothesis_only':True,'material_fidelity_verified':False,'current_RDC_identity':False,'mounted_fit':False,'package_complete':False,'art_accepted':False,'git_touched':False,'root_registers_modified':False}
(O/'delivery.json').write_text(json.dumps(delivery,indent=2))
files=[p for base in [H,O] for p in base.rglob('*')if p.is_file()and p.name not in ['frozen-checkpoint.json','ready-paths.txt']];protocols=[R/'tools'/x for x in plan['protocols']]+[R/'tools'/x for x in ['front_completion_front10_render_v1.py','front_completion_front10_material_v1.py','front_completion_front10_finalize_v1.py','front_completion_validate.mjs','front_completion_buffers_v1.mjs','front_completion_material_parity_v1.mjs','front_completion_check_raw_v1.py','front_completion_source_metadata_v1.py','blender_component_camera_preflight.py']];files=sorted(set(files+protocols));rows=[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in files];(O/'frozen-checkpoint.json').write_text(json.dumps({'checkpoint':K,'frozen_files':rows,'no_changes_after_freeze':True,'scope':'Exact bytes; technical/exterior study only, not user art acceptance'},indent=2));(O/'ready-paths.txt').write_text('\n'.join(x['path']for x in rows)+'\n'+str((O/'frozen-checkpoint.json').relative_to(R))+'\n'+str((O/'ready-paths.txt').relative_to(R))+'\n');print(K,len(rows),'files frozen')
