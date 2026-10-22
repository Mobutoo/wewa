import pathlib,json,hashlib,datetime,os
R=pathlib.Path('/workspace/wewa');D=R/'creative/reviews/headlamp-interior-context-v1';roots=[R/'creative/research/headlamp-interior-evidence-audit-v1',D,R/'assets-src/moto-components/headlamp-interior-context-v1'];manifest=D/'frozen-checkpoint.json'
rows=[]
for folder in roots:
 for p in sorted(folder.rglob('*')):
  if p.is_file() and p!=manifest:rows.append({'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
checks=json.loads((D/'reopen-raw-check.json').read_text());assert checks['native_reopened'] and checks['original_sources_unchanged'] and checks['mesh_emission_zero']
for v in json.loads((D/'export-buffer-audit.json').read_text()):assert hashlib.sha256((R/v['path']).read_bytes()).hexdigest()==v['sha256']
obj={'frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'revision':'headlamp-interior-context-v1','files':rows,'bytes':sum(x['bytes'] for x in rows),'manifest_self_excluded':True,'protection':'0444 files, local SHA256 integrity; not WORM','G8':'pending','optical_completion':False,'native_source_export_original_hashes_verified':True}
manifest.write_text(json.dumps(obj,indent=2)+'\n')
for folder in roots:
 for p in folder.rglob('*'):
  if p.is_file():p.chmod(0o444)
assert all(hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256'] for x in rows)
print(json.dumps({'file_count':len(rows),'bytes':obj['bytes'],'manifest':str(manifest.relative_to(R)),'manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'all_hashes_verified':True}))
