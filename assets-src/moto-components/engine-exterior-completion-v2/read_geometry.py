import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');O=Path(__file__).resolve().parent;V=R/'assets-src/moto-components/engine-exterior-completion-v1';rows=json.loads((V/'poses-and-sources.json').read_text())['parents'];out=[]
for r in rows:
 bpy.ops.wm.open_mainfile(filepath=str(R/r['source']));obs=[bpy.data.objects[n] for n in r['objects']];dg=bpy.context.evaluated_depsgraph_get()
 for ob in obs:
  ev=ob.evaluated_get(dg);me=ev.to_mesh();vs=[list(ob.matrix_world@v.co) for v in me.vertices];me.calc_loop_triangles();stride=max(1,len(vs)//20000);out.append(dict(key=r['key'],matrix=[list(x) for x in ob.matrix_world],properties={k:str(ob[k])[:1500]for k in ob.keys()},vertices=vs[::stride],triangles=len(me.loop_triangles),bounds=[[min(v[i]for v in vs)for i in range(3)],[max(v[i]for v in vs)for i in range(3)]]));ev.to_mesh_clear()
(O/'geometry-read.json').write_text(json.dumps(out,separators=(',',':')))
