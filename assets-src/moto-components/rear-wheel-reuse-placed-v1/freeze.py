from pathlib import Path
import json,hashlib,datetime
O=Path(__file__).resolve().parent;R=Path('/workspace/wewa');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((O/'add-only-fragment.json').read_text());assert len(f['add_only'])==4 and not f['remove_existing']and not f['replace_existing'];assert sum(len(r['selected_objects'])for r in f['add_only'])==7
for r in f['add_only']:assert sha(R/r['source'])==r['sha256']and sha(R/r['glb'])==r['glb_sha256']
reports=json.loads((O/'gray-render-report.json').read_text());assert len(reports)==2 and all(r['samples']==4 and r['resolution']==[640,450]for r in reports)
old=R/'assets-src/moto-components/rear-wheel-coverage-audit-v1/frozen-audit.json';assert sha(old)=='172d3157ec9acddfb76ae89206d0ab1cc9e5ad7c70d69cb626859dccf9d69b21'
files=[]
for p in sorted(O.rglob('*')):
 if not p.is_file()or p.name=='frozen-outputs.json':continue
 assert p.stat().st_size<100*1024**2;files.append(dict(path=str(p.relative_to(O)),bytes=p.stat().st_size,sha256=sha(p)))
manifest=dict(schema=1,frozen_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='FROZEN_ADD_ONLY_4_EXISTING_PARENTS_BOUNDED_REUSE',fragment='add-only-fragment.json',fragment_sha256=sha(O/'add-only-fragment.json'),native='rear-wheel-add-only-v1.blend',native_sha256=sha(O/'rear-wheel-add-only-v1.blend'),collection='REAR_WHEEL_REUSE_ADD_ONLY_V1',parents=4,source_meshes=7,new_geometry=0,new_glb_exports=0,G1='unreceived_bounded_estimates',G5='unreceived_bounded_pose_not_physical_fit',G8=False,art_accepted=False,old_audit_manifest_unchanged=True,outputs=files,total_bytes=sum(r['bytes']for r in files))
(O/'frozen-outputs.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(dict(files=len(files),bytes=manifest['total_bytes'],fragment_sha256=manifest['fragment_sha256'],native_bytes=(O/'rear-wheel-add-only-v1.blend').stat().st_size,manifest_sha256=sha(O/'frozen-outputs.json'))))
