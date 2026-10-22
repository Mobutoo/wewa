"""Reopen actual candidate source and compare its mesh digest with gray baseline."""
import sys,json,hashlib,bpy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import digest,sha,R,write
review,source_dir=sys.argv[sys.argv.index('--')+1:];H=R/'assets-src/moto-components'/source_dir;O=R/'creative/reviews'/review;assert Path(bpy.data.filepath).resolve()==(H/'child-candidate.blend').resolve();base=json.loads((O/'geometry-check.json').read_text());rows=[]
for row in base['objects']:
 ob=bpy.data.objects[row['object']];value=digest(ob.data);assert value==row['geometry_digest'];rows.append(dict(object=ob.name,geometry_digest=value,gray_equal=True))
write(O,'source-geometry-check.json',dict(source_reopened=True,source_sha256=sha(H/'child-candidate.blend'),export_sha256=sha(H/'child-candidate.glb'),objects=rows,scope='Actual reopened source versus gray mesh; no hidden fit or photo calibration',art_accepted=False))
