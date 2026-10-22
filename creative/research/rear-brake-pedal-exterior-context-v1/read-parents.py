import bpy,json,hashlib
from pathlib import Path
R=Path('/workspace/wewa');D=R/'creative/research/rear-brake-pedal-exterior-context-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
for suffix in ['arm','pivot-sleeve','linkage-lug','textured-pad']:
 name='brake-pedal-'+suffix+'-v1';H=R/'assets-src/moto-components'/name;p=H/'child-candidate.blend';before=sha(p);bpy.ops.wm.open_mainfile(filepath=str(p));obs=[]
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH' or ob.hide_render:continue
  m=ob.data;ps=[ob.matrix_world@v.co for v in m.vertices];m.calc_loop_triangles();obs.append(dict(name=ob.name,matrix_world=[list(r)for r in ob.matrix_world],bounds_m={'min':[min(v[i]for v in ps)for i in range(3)],'max':[max(v[i]for v in ps)for i in range(3)]},vertices=len(m.vertices),triangles=len(m.loop_triangles),materials=[m.name for m in m.materials]))
 assert len(obs)==1 and sha(p)==before;rows.append(dict(name=name,source=str(p.relative_to(R)),sha256=before,glb=str((H/'child-candidate.glb').relative_to(R)),glb_sha256=sha(H/'child-candidate.glb'),parameters=json.loads((H/'parameters.json').read_text()),objects=obs))
(D/'parent-native-read.json').write_text(json.dumps({'parents':rows,'source_unchanged':True,'no_new_geometry':True},indent=2)+'\n')
