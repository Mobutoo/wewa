import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/wewa');D=R/'creative/research/passenger-footrest-left-exterior-context-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
for name in ['passenger-footrest-stay-left-v1','passenger-footpeg-metal-v1','passenger-footrest-rubber-jk113008-v1']:
 H=R/'assets-src/moto-components'/name;source=H/'child-candidate.blend';before=sha(source);bpy.ops.wm.open_mainfile(filepath=str(source));obs=[]
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH' or ob.hide_render:continue
  m=ob.data;m.calc_loop_triangles();ps=[ob.matrix_world@v.co for v in m.vertices];obs.append(dict(name=ob.name,matrix_world=[list(r)for r in ob.matrix_world],vertices=len(ps),triangles=len(m.loop_triangles),bounds_m={'min':[min(p[i]for p in ps)for i in range(3)],'max':[max(p[i]for p in ps)for i in range(3)]},materials=[m.name for m in m.materials],surface_normal_samples=[{'vertex':i,'point':list(m.vertices[i].co),'normal':list(m.vertices[i].normal)}for i in [0,len(m.vertices)//3,len(m.vertices)//2]]))
 assert len(obs)==1 and sha(source)==before
 rows.append(dict(parent=name,source=str(source.relative_to(R)),sha256=before,glb=str((H/'child-candidate.glb').relative_to(R)),glb_sha256=sha(H/'child-candidate.glb'),parameters=json.loads((H/'parameters.json').read_text()),objects=obs))
(D/'native-parent-audit.json').write_text(json.dumps({'parents':rows,'scope':'Actual native frame/normals/bounds audit before composition, no source edits'},indent=2)+'\n')
