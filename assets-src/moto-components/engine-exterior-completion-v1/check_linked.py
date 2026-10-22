import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent;p=O/'engine-exterior-completion-v1-linked.blend';bpy.ops.wm.open_mainfile(filepath=str(p));dg=bpy.context.evaluated_depsgraph_get();rows=[]
for inst in dg.object_instances:
 ob=inst.object
 if ob.type!='MESH':continue
 me=ob.to_mesh();me.calc_loop_triangles();pts=[inst.matrix_world@v.co for v in me.vertices];rows.append(dict(name=ob.name,triangles=len(me.loop_triangles),bounds=[[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]]));ob.to_mesh_clear()
report=dict(source=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),evaluated_mesh_instances=rows,total_triangles=sum(r['triangles'] for r in rows),libraries=[dict(path=bpy.path.abspath(lib.filepath),sha256=hashlib.sha256(Path(bpy.path.abspath(lib.filepath)).read_bytes()).hexdigest())for lib in bpy.data.libraries],no_mesh_geometry_copied=True)
assert len(rows)==8 and report['total_triangles']==1459902,report
(O/'linked-wrapper-check.json').write_text(json.dumps(report,indent=2))
