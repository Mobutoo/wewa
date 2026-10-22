import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');O=R/'assets-src/moto-components/engine-exterior-completion-v1';out=[]
paths=[p for p in (R/'assets-src/moto-components').glob('crankcase*/child-candidate.blend')]+[R/'assets-src/moto-components'/d/f for d,f in [('engine-cover-left','engine-cover-left-v2.blend'),('engine-cover-right','engine-cover-right-v2.blend'),('engine-output-cover-left','engine-output-cover-left-v1.blend'),('engine-cylinder','engine-cylinder-v1.blend'),('engine-head','engine-head-v3.blend')]]
for p in paths:
 bpy.ops.wm.open_mainfile(filepath=str(p));obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render];pts=[o.matrix_world@Vector(v) for o in obs for v in o.bound_box];row=dict(source=str(p.relative_to(R)),collections=[c.name for c in bpy.data.collections if c.library is None],objects=[o.name for o in obs],bounds=[ [min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]]);out.append(row)
(O/'native-inventory.json').write_text(json.dumps(out,indent=2))
