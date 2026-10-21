from pathlib import Path
import bpy,json,tempfile,subprocess,shutil
from control_geometry import mesh_object

def csg(base,features,drills,collection,mat,root,name):
 def row(o):
  deps=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(deps);m=ev.to_mesh();m.calc_loop_triangles();r={'name':o.name,'vertices':[list(o.matrix_world@v.co)for v in m.vertices],'triangles':[list(t.vertices)for t in m.loop_triangles]};ev.to_mesh_clear();return r
 with tempfile.TemporaryDirectory(prefix='wewa-head-csg-')as tmp:
  inp=Path(tmp)/'in.json';out=Path(tmp)/'out.json';inp.write_text(json.dumps({'base':row(base),'features':[row(o)for o in features],'drills':[row(o)for o in drills]}));subprocess.run([shutil.which('python'),str(Path(__file__).with_name('csg_kernel_v2.py')),str(inp),str(out)],check=True);data=json.loads(out.read_text())
 result=mesh_object(name,data['vertices'],data['triangles'],collection,mat)
 for o in[base]+features+drills:o.hide_render=True;o.hide_set(True)
 return result,data
