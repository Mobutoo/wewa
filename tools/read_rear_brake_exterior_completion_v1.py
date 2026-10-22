import bpy,json
from pathlib import Path
R=Path('/workspace/wewa');rows=[]
for name in ['brake-rod-clevis-v1','brake-linkage-headed-pin-v1','brake-rod-barrel-pin-v1','brake-rod-compression-spring-v1']:
 bpy.ops.wm.open_mainfile(filepath=str(R/'assets-src/moto-components'/name/'child-candidate.blend'))
 for o in bpy.context.scene.objects:
  if o.type=='MESH':rows.append(dict(family=name,object=o.name,bounds=[[min(v.co[i]for v in o.data.vertices)for i in range(3)],[max(v.co[i]for v in o.data.vertices)for i in range(3)]],matrix=[list(v)for v in o.matrix_world]))
p=R/'creative/research/rear-brake-exterior-completion-v1/native-input-geometry.json';p.write_text(json.dumps(rows,indent=2)+'\n')
