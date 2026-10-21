"""Reopen worker .blend and inspect actual evaluated meshes, without changing the source."""
import bpy,json,sys,hashlib,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];cfg=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());source=R/cfg['source'];assert Path(bpy.data.filepath).resolve()==source.resolve();rows=[]
for ob in bpy.data.objects:
 if ob.type!='MESH':continue
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles();areas=[t.area for t in m.loop_triangles];assert areas and min(areas)>0
 assert all(math.isfinite(x)for v in m.vertices for x in v.co)
 rows.append(dict(name=ob.name,vertices=len(m.vertices),triangles=len(m.loop_triangles),minimum_triangle_area_m2=min(areas),collections=[c.name for c in ob.users_collection],uv_layers=[u.name for u in m.uv_layers],materials=[m.name for m in m.materials]));ev.to_mesh_clear()
assert rows;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();out=R/'creative/reviews'/cfg['review'];out.mkdir(exist_ok=True,parents=True)
(out/'source-geometry-check.json').write_text(json.dumps(dict(source_sha256=sha(source),export_sha256=sha(R/'assets-src/moto-components'/cfg['files'][0]),source_reopened=True,meshes=rows,triangles=sum(r['triangles']for r in rows),source_unchanged=True,protocol_sha256=sha(Path(__file__)),scope='Actual evaluated mesh finite/area inspection and frozen file association; not source/export positional parity, exact measurements or fit/art reception'),indent=2)+'\n')
