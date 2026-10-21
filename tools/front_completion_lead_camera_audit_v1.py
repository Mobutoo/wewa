import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');key='front-completion-p09-leads-material-v2';O=R/'creative/reviews'/key/'camera-proof-v4';O.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'assets-src/moto-components'/key/'leads-material.blend'));obs=[o for o in bpy.data.objects if o.type=='MESH'];rows=[]
for v in json.loads((R/'creative/reviews'/key/'render-report.json').read_text())['views']:
 if not v['view'].startswith('terminal-'):continue
 eye=Vector(v['camera']);target=Vector(v['target']);forward=(target-eye).normalized();depths=[(ob.matrix_world@vert.co-eye).dot(forward)for ob in obs for vert in ob.data.vertices];rows.append({'view':v['view'],'minimum_whole_source_depth_m':min(depths),'maximum_whole_source_depth_m':max(depths),'whole_source_in_front_of_camera':min(depths)>0})
(O/'prior-v3-depth-audit.json').write_text(json.dumps({'scope':'Read-only depth test of complete saved source, including intentionally off-frame bodies; no source or prior proof changed','views':rows},indent=2));print(rows)
