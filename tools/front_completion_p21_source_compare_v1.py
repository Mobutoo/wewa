import bpy,bmesh,json,hashlib
from pathlib import Path
R=Path('/workspace/wewa');rows=[]
for key in ['front-completion-p21-carrier-v2','front-completion-p21-carrier-v3']:
 p=R/'assets-src/moto-components'/key/'carrier-gray.blend';bpy.ops.wm.open_mainfile(filepath=str(p));m=next(o.data for o in bpy.data.objects if o.type=='MESH');bm=bmesh.new();bm.from_mesh(m);m.calc_loop_triangles();rows.append({'key':key,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'positions_sha256':hashlib.sha256(json.dumps([list(v.co)for v in m.vertices]).encode()).hexdigest(),'vertices':len(m.vertices),'triangles':len(m.loop_triangles),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_m3':bm.calc_volume(signed=True)});bm.free()
assert rows[0]['positions_sha256']==rows[1]['positions_sha256'];assert rows[1]['nonmanifold_edges']==0 and rows[1]['volume_m3']>0
(R/'creative/reviews/front-completion-p21-carrier-v3/source-check.json').write_text(json.dumps({'rows':rows,'positions_identical':True,'scope':'Actual reopened source positions, topology closure and volume; no mounted fit or artistic acceptance'},indent=2))
