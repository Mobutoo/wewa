"""Exercise the no-render workflow in a temporary tree without changing review assets."""
import hashlib,json,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='wewa-rim-preflight-') as directory:
 root=Path(directory);source=root/'assets-src/moto-components/front-rim';source.mkdir(parents=True)
 for name in ['build.py','parameters.json']:shutil.copy2(ROOT/'assets-src/moto-components/front-rim'/name,source/name)
 (source.parent/'front-tyre').symlink_to(ROOT/'assets-src/moto-components/front-tyre',target_is_directory=True)
 (root/'node_modules').symlink_to(ROOT/'node_modules',target_is_directory=True)
 (root/'tools').mkdir();shutil.copy2(ROOT/'tools/check_front_rim.mjs',root/'tools/check_front_rim.mjs')
 run=subprocess.run(['blender','--background','--python',str(source/'build.py'),'--','--views','none'],cwd=root,text=True,capture_output=True)
 if run.returncode:raise RuntimeError(run.stdout[-4000:]+run.stderr[-4000:])
 build=json.loads((source/'build-report.json').read_text());assert build['renders']==[]
 check=subprocess.run(['node','tools/check_front_rim.mjs'],cwd=root,text=True,capture_output=True)
 if check.returncode:raise RuntimeError(check.stdout[-4000:]+check.stderr[-4000:])
 geometry=json.loads((root/'creative/reviews/front-rim-v1/geometry-check.json').read_text())
 report={'scope':'No-render generator exercised in disposable tree; published source and views not overwritten','passed':True,'render_views':0,'generator_sha256':hashlib.sha256((source/'build.py').read_bytes()).hexdigest(),'exports':[{'name':Path(x['file']).name,'glTF_errors':x['glTF_errors'],'glTF_warnings':x['glTF_warnings']} for x in geometry['exports']],'art_accepted':False}
 (ROOT/'creative/reviews/front-rim-v1/preflight-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
