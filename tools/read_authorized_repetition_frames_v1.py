"""Read actual source frames before provisional repeated placements; no source edits."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=json.loads((R/'tools/motorcycle-lab/catalog.json').read_text())['assets'];O=R/'creative/research/authorized-repetition-layout-v1';O.mkdir(exist_ok=True)
keys=['indicator-front-left-stalk','indicator-front-right-stalk','rear-indicator-left-stalk-v1','rear-indicator-right-stalk-v1','indicator-front-lens','indicator-front-housing','rear-indicator-mount-washer-v2'];rows=[]
for k in keys:
 c=C[k];p=R/'assets-src/moto-components'/c['source'];before=hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(p));names=c.get('collection');col=bpy.data.collections.get(names);obs=list(col.all_objects)if col else list(bpy.context.scene.objects);out=[]
 for ob in obs:
  if ob.type!='MESH':continue
  vs=[ob.matrix_world@v.co for v in ob.data.vertices];lo=[min(v[a]for v in vs)for a in range(3)];hi=[max(v[a]for v in vs)for a in range(3)];out.append(dict(name=ob.name,matrix=[list(v)for v in ob.matrix_world],bounds=[lo,hi],vertices=len(vs),materials=[m.name for m in ob.data.materials]))
 rows.append(dict(key=k,source=str(p.relative_to(R)),sha256=before,collection=names,meshes=out));assert before==hashlib.sha256(p.read_bytes()).hexdigest()
(O/'source-frames.json').write_text(json.dumps(dict(scope='Actual native source coordinate read; no installed fit reception',rows=rows),indent=2)+'\n')
