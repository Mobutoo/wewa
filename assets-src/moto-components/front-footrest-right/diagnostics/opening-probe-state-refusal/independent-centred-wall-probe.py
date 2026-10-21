from pathlib import Path
import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path('/workspace/wewa-github/assets-src/moto-components/front-footrest-right');b=json.loads((H/'geometry-report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(H/'front-footrest-right-v1-geometry.blend'));o=bpy.data.objects[b['geometry'][0]['name']];m=o.data;m.calc_loop_triangles();tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(t.vertices)for t in m.loop_triangles],all_triangles=True)
for j in range(4):
 a=math.tau*j/4;d=Vector((0,math.cos(a),math.sin(a)));e=tree.ray_cast(Vector((.225,0,0)),d,.03);f=tree.ray_cast(e[0]+d*1e-6,d,.03);print('WALL',j,list(e[0]),list(f[0])if f[0]else None,(f[0]-e[0]).length if f[0]else None)
