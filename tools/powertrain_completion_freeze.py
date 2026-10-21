"""Freeze one worker-owned child only; no shared registry or Git writes."""
import argparse,json,hashlib,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('review');p.add_argument('package');p.add_argument('component');p.add_argument('source_dir');p.add_argument('--script',action='append',default=[]);p.add_argument('--remaining',action='append',default=[]);p.add_argument('--child',action='append',default=[]);a=p.parse_args()
O=R/'creative/reviews'/a.review;H=R/'assets-src/moto-components'/a.source_dir
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
protocols=O/'protocols';protocols.mkdir(exist_ok=True)
for name in a.script:
 s=R/name;dest=protocols/(sha(s)+'-'+s.name)
 if not dest.exists():shutil.copyfile(s,dest)
blends=sorted(H.glob('*candidate*.blend'));glbs=sorted(H.glob('*candidate*.glb'))
assert blends and glbs
fragment={'package':a.package,'component_id':a.component,'revision':a.review,'label':a.component+' — bounded exterior candidate','source':str(blends[-1].relative_to(R)),'files':[str(g.relative_to(R/'assets-src/moto-components'))for g in glbs],'review':a.review,'source_directory':str(H.relative_to(R)),'children_delivered':a.child,'remaining':a.remaining,'package_complete':False,'art_accepted':False,'physical_iphone_tested':False,'rigs':[]}
(O/'catalog-fragment.json').write_text(json.dumps(fragment,indent=2)+'\n')
paths=sorted(set(p for folder in [H,O]for p in folder.rglob('*')if p.is_file()and p.name not in ['delivery.json','production-manifest.json']and not p.name.endswith('.blend1')))
manifest={'schema':1,'package':a.package,'milestone':'Usable isolated child candidate; package remains incomplete','component_id':a.component,'files':[{'path':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size}for p in paths],'exact_build_scripts':[{'path':n,'sha256':sha(R/n)}for n in a.script],'remaining_children_and_limits':a.remaining,'package_complete':False,'art_accepted':False,'physical_iphone_tested':False,'coordinator_publish_required':True}
(O/'delivery.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'delivery':str((O/'delivery.json').relative_to(R)),'files':len(paths),'package_complete':False}))
