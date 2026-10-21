"""Worker-only gray milestone. Reads child source; no shared catalog/Git mutation."""
import argparse,json,hashlib,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('review');p.add_argument('package');p.add_argument('source_dir');p.add_argument('--script',action='append',default=[]);a=p.parse_args();O=R/'creative/reviews'/a.review;H=R/'assets-src/moto-components'/a.source_dir;F=O/'gray-frozen';F.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['geometry-check.json','gray-review.json','gray-render-report.json','independent-export-check.json']:
 if(O/n).exists():shutil.copyfile(O/n,F/n)
for n in a.script:shutil.copyfile(R/n,F/Path(n).name)
paths=list(F.iterdir())+list(H.glob('*gray*.blend'))+list(H.glob('*gray*.glb'))+list(H.glob('parameters*.json'))+list(O.glob('gray-*.png'))+list((O/'raw').glob('gray-*.exr'))
f={'package':a.package,'revision':a.review+'-gray','source':[str(p.relative_to(R))for p in H.glob('*gray*.blend')],'files':[str(p.relative_to(R/'assets-src/moto-components'))for p in H.glob('*gray*.glb')],'review':a.review,'scope':'Gray child milestone only; package incomplete','package_complete':False,'art_accepted':False};(O/'gray-catalog-fragment.json').write_text(json.dumps(f,indent=2)+'\n');paths.append(O/'gray-catalog-fragment.json');(O/'gray-delivery.json').write_text(json.dumps(dict(schema=1,package=a.package,milestone='Gray source and checks',files=[dict(path=str(p.relative_to(R)),sha256=sha(p),bytes=p.stat().st_size)for p in paths],package_complete=False,art_accepted=False),indent=2)+'\n');print(O/'gray-delivery.json')
