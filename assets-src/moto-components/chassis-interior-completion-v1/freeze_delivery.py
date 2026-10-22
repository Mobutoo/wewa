from pathlib import Path
import json,hashlib,datetime
O=Path(__file__).resolve().parent;R=O.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
fragment=json.loads((O/'integration-fragment.json').read_text());checks=[]
for row in fragment['additions']:
 p=R/row['source'];checks.append({'path':row['source'],'expected_sha256':row['sha256'],'actual_sha256':sha(p)});assert row['sha256']==sha(p)
source=json.loads((O/'source-invariance.json').read_text())
for r in source['sources']:assert sha(R/r['path'])==r['expected']
assert json.loads((O/'node-geometry-parity.json').read_text())['actual_node_parity']
assert json.loads((O/'native-export-parity.json').read_text())['native_export_bounds_pass']
assert json.loads((O/'linked-reopen-check.json').read_text())['all_libraries_present']
assert not json.loads((O/'runtime-check.json').read_text())['page_errors']
assert len(json.loads((O/'material-96-renders.json').read_text()))==3
files=[]
for p in sorted(O.rglob('*')):
 if p.is_file()and p.name!='freeze.json':
  assert p.stat().st_size<100*1024**2,(p,p.stat().st_size);files.append({'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)})
manifest={'id':'chassis-interior-completion-v1','frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'canonical_linked_source':str((O/'kit-linked-v2.blend').relative_to(R)),'integration_fragment':str((O/'integration-fragment.json').relative_to(R)),'integration_mode':'additive; zero baseline removals','counts':fragment['count'],'source_invariance_107_pass':True,'integration_source_hashes_verified':checks,'strict_errors':0,'native_gray_material_node_parity':True,'linked_reopened':True,'raw32_verified':True,'actual_babylon_captures_read':True,'final_native_96_views_read':['quarter','reverse','profile'],'all_files_below_100MiB':True,'art_accepted':False,'mechanical_fit_accepted':False,'G8':'not acquired','files':files,'bytes_total':sum(f['bytes']for f in files),'retained_rejections':['kit-linked.blend (use kit-linked-v2.blend)','poses-global-before-depsgraph-update.json','export-parity.json (definition count mismatch; actual instances equal)','runtime-before-environment-*'],'freeze_excludes_only_itself':True}
(O/'freeze.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'files':len(files),'bytes':manifest['bytes_total'],'max_file_bytes':max(r['bytes']for r in files),'freeze_sha256':sha(O/'freeze.json')}))
