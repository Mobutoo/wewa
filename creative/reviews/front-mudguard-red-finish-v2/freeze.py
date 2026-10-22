import pathlib,json,hashlib,datetime
R=pathlib.Path('/workspace/wewa');D=R/'creative/reviews/front-mudguard-red-finish-v2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((D/'main-fragment.json').read_text());checks=json.loads((D/'reopen-raw-check.json').read_text());inv=json.loads((D/'export-invariance-validator.json').read_text());bab=json.loads((D/'babylon-report.json').read_text())
assert sha(R/f['source'])==f['source_sha256']and sha(R/f['glb'])==f['glb_sha256'];assert sha(R/f['geometry_library'])==f['geometry_library_sha256'];assert sha(R/'assets-src/moto-components/front-mudguard/front-mudguard-shell-inspection.glb')==f['old_glb_sha256'];assert checks['old_native_and_glb_unchanged']and all(r['finite']and all(c['pixel_type']=='FLOAT32'for c in r['channels_actual'])for r in checks['raw']);assert inv['geometry_P_N_UV_I_bit_exact']and inv['tangents_bit_exact']and inv['validator']['numErrors']==0;assert not bab['page_errors']and not bab['http_failures']
roots=[R/'assets-src/moto-components/front-mudguard-red-finish-v2',R/'creative/research/front-mudguard-red-finish-v2',D];manifest=D/'frozen-checkpoint.json';rows=[]
for root in roots:
 for p in sorted(root.rglob('*')):
  if p.is_file()and p!=manifest:rows.append({'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)})
manifest.write_text(json.dumps({'revision':'front-mudguard-red-finish-v2','frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':rows,'main_fragment':'creative/reviews/front-mudguard-red-finish-v2/main-fragment.json','source_sha256':f['source_sha256'],'glb_sha256':f['glb_sha256'],'geometry_P_N_UV_T_I_and_nodes_bit_exact':True,'validator_errors':0,'validator_warnings':0,'native96_raw32_pairs':3,'babylon_import_executed':True,'G8':'pending','art_accepted':False,'protection':'0444 local file integrity, not WORM','manifest_self_excluded':True},indent=2)+'\n')
for root in roots:
 for p in root.rglob('*'):
  if p.is_file():p.chmod(0o444)
assert all(sha(R/x['path'])==x['sha256']for x in rows)
print(json.dumps({'manifest':str(manifest.relative_to(R)),'manifest_sha256':sha(manifest),'files':len(rows),'bytes':sum(r['bytes']for r in rows),'source_sha256':f['source_sha256'],'glb_sha256':f['glb_sha256'],'hashes_verified':True}))
