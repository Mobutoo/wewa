"""Freeze coordinate dossier only; assert inputs unchanged, no model/pose edits or Git staging."""
from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;R=D.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());out=lambda n,j:(D/n).write_text(json.dumps(j,indent=2,ensure_ascii=False)+'\n')
assert not (D/'delivery-frozen.json').exists(),'Never rewrite immutable dossier'
natives=[*read(D/'native-coordinate-read.json')['parents'],*read(D/'intake-native-coordinate-read.json')['parents']];exports=[*read(D/'export-coordinate-read.json')['parents'],*read(D/'intake-export-coordinate-read.json')['parents']];assert len(natives)==len(exports)==38 and all(x['exists']for x in natives+exports)
inputs={}
for e in natives:
 p=R/e['native'];assert sha(p)==e['sha256'];inputs[str(p.relative_to(R))]=p
for e in exports:
 p=R/e['glb'];assert sha(p)==e['sha256'];inputs[str(p.relative_to(R))]=p
for fname in ['parent-inputs.json','intake-parent-inputs.json']:
 for e in read(D/fname)['parents']:
  if e.get('parameters'):inputs[e['parameters']]=R/e['parameters']
for e in read(D/'parameter-snapshots.json').values():assert sha(R/e['path'])==e['sha256']
for table in ['intake-exact-restoration.json','requested-parent-exact-restoration.json']:
 for e in read(D/table)['files']:
  if e['action']!='RESTORED_EXACT_MISSING_ONLY':continue
  p=R/e['path'];b=p.read_bytes();assert sha(p)==e['sha256'];assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==e['git_blob'];inputs[e['path']]=p
# Freeze read record/feature source metadata into uniquely located dossier copies.
S=D/'evidence-snapshots';S.mkdir(exist_ok=True);paths=set()
for e in read(D/'parent-native-inventory.json')['parents']:paths.update(e['semantic_frame']['evidence_paths'])
for e in read(D/'relative-relations.json')['relations']:paths.update(e['evidence_paths'])
snaps=[]
for rel in sorted(paths):
 p=R/rel
 if not p.is_file():continue
 if p.suffix not in ['.json','.py','.mjs']:continue
 h=sha(p);target=S/(h+'-'+p.name);target.write_bytes(p.read_bytes());snaps.append(dict(source_path=rel,snapshot_path=str(target.relative_to(R)),sha256=h,scope='Bytes read for coordinate/relationship provenance only, not repeated artistic proof audit'))
out('evidence-snapshot-index.json',dict(files=snaps,live_ledgers_not_in_fullhash=['tools/motorcycle-lab/catalog.json','creative/workflow/records/* live coordination records'],method='Relevant source evidence copied into immutable dossier snapshots; live catalogue entry separately snapshotted.'))
out('source-inputs-sha256.json',dict(scope='Actual input file hashes after read-only scene/export audit and exact restoration, no mutable live catalogues',files=[dict(path=r,sha256=sha(p),bytes=p.stat().st_size)for r,p in sorted(inputs.items())]))
out('inventory-index.json',dict(schema=1,entries=38,natives_opened_unchanged=38,glb_static_world_read=38,main_parent_inventory='parent-native-inventory.json',intake_annex='intake-mouths-world.json',relative_evidence='relative-relations.json',intake_chain='intake-relative-chain-and-coordinator-hypothesis.json',native_source_units='metres,scale_length1',restored_missing_files=sum(e['action']=='RESTORED_EXACT_MISSING_ONLY'for t in ['intake-exact-restoration.json','requested-parent-exact-restoration.json']for e in read(D/t)['files']),no_new_geometry=True,no_new_installed_pose=True,no_staging=True,no_refs_changed=True,physical_fit_certified=False,package_complete=False,art_accepted=False))
files=[p for p in D.rglob('*')if p.is_file()and'__pycache__'not in p.parts and p.name!='delivery-frozen.json'];table=dict(schema=1,scope='Frozen native/source coordinate and documented-relation dossier, existing parents only; no fabricated assembly poses',authority='Coordinator dispatch within user-authorized autonomous motorcycle completion',files=[dict(path=str(p.relative_to(R)),sha256=sha(p),bytes=p.stat().st_size)for p in sorted(files)],input_guard='source-inputs-sha256.json',new_geometry=False,new_installed_pose=False,package_complete=False,art_accepted=False);out('delivery-frozen.json',table);assert all(sha(R/e['path'])==e['sha256']for e in table['files']);print(json.dumps(dict(delivery=str((D/'delivery-frozen.json').relative_to(R)),sha256=sha(D/'delivery-frozen.json'),files=len(files),entries=38,natives=38,glbs=38)))
