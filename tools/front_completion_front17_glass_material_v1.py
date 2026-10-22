"""Continuous glazing skin transmission hypothesis, no wall or optical reception."""
from pathlib import Path
import runpy,hashlib,sys,json
R=Path('/workspace/wewa');parent=R/'tools/front_completion_front15_capsule_material_v1.py'
assert hashlib.sha256(parent.read_bytes()).hexdigest()=='1296d38c73549a575b69e66f22b5e695f237bfd7947203ad95d9c3fdcb7b1306'
runpy.run_path(str(parent),run_name='__main__')
key,stem=sys.argv[sys.argv.index('--')+1:][:2];p=R/'creative/reviews'/key/'material-plan.json';d=json.loads(p.read_text());d['limitations']=['Continuous single outer glazing surface only; no actual inner wall, glass thickness or physically verified refraction','Clear-glass IOR/transmission/color and roughness are uncalibrated hypotheses','Reflector, striae and optical prescription excluded; geometry unchanged','G4 held, separate Blender/Babylon transmission limit must be reported'];d['parent_protocol_sha256']='1296d38c73549a575b69e66f22b5e695f237bfd7947203ad95d9c3fdcb7b1306';p.write_text(json.dumps(d,indent=2))
