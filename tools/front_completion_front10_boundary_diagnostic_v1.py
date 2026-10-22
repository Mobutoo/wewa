import bpy,bmesh,sys,json,math
from pathlib import Path
R=Path('/workspace/wewa');source,out=sys.argv[sys.argv.index('--')+1:][:2];bpy.ops.wm.open_mainfile(filepath=str(R/source));rows=[]
for ob in bpy.data.objects:
 if ob.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(ob.data);edges=[e for e in bm.edges if e.is_boundary];verts=set(v for e in edges for v in e.verts);rows.append({'object':ob.name,'boundary_edges':len(edges),'boundary_vertices':[list(v.co)for v in verts]});bm.free()
(R/out).write_text(json.dumps(rows,indent=2));print(json.dumps(rows))
