"""Sequential reviewed-preview -> two native96 views -> independent neutral96."""
import subprocess,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];name=sys.argv[1];O=R/'creative/reviews'/name
assert json.loads((O/'preview-review.json').read_text())['read_for_exterior_study']
blender='/workspace/scratch/blender-runtime/blender-4.3.2-linux-x64/blender'
for label,script,args in [('final','tools/powertrain_completion_render.py',[name,name,'final']),('neutral96','tools/powertrain_continuation_neutral96_v2.py',[name])]:
 with (O/(label+'-execution.log')).open('w')as log:subprocess.run([blender,'-b','--python-exit-code','1','--python',script,'--',*args],cwd=R,stdout=log,stderr=subprocess.STDOUT,check=True)
report=json.loads((O/'final-render-report.json').read_text());assert len(report['views'])>=3
print(json.dumps({'review':name,'native96_views':len(report['views']),'manual_image_read_still_required':True}))
