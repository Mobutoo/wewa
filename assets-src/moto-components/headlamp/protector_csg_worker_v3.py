"""Original constructive solids only; external manifold CPU process, no source edits."""
import json,sys,numpy as np,manifold3d as m
from importlib.metadata import version
d=json.load(open(sys.argv[1]));stages=[];ids={row['name']:m.Manifold.reserve_ids(1)for row in [d['base']]+d['features']+d['drills']}
def solid(row):
 a=m.Manifold(m.Mesh(np.asarray(row['vertices'],np.float32),np.asarray(row['triangles'],np.uint32),run_index=np.asarray([0,3*len(row['triangles'])],np.uint32),run_original_id=np.asarray([ids[row['name']]],np.uint32)));assert a.status()==m.Error.NoError and a.volume()>0,(row['name'],a.status(),a.volume());return a
r=solid(d['base'])
for op in ['features','drills']:
 for row in d[op]:
  before=r.volume();p=solid(row);r=r+p if op=='features' else r-p;assert r.status()==m.Error.NoError and r.volume()>0,(row['name'],r.status());stages.append({'operation':op,'name':row['name'],'before_m3':before,'after_m3':r.volume()})
assert len(r.decompose())==1
mesh=r.to_mesh();owners=[None]*len(mesh.tri_verts);id_to_owner={ids[row['name']]:k for k,row in enumerate([d['base']]+d['features'])}
for k,oid in enumerate(mesh.run_original_id):
 for t in range(mesh.run_index[k]//3,mesh.run_index[k+1]//3):owners[t]=id_to_owner[int(oid)]
assert all(v in [0,1,2]for v in owners)
json.dump({'vertices':mesh.vert_properties[:,:3].tolist(),'triangles':mesh.tri_verts.tolist(),'stages':stages,'triangle_source_owners':owners,'ownership_method':'Actual Manifold run_original_id from original input solids, not nearest-surface heuristic','worker':'manifold3d','version':version('manifold3d')},open(sys.argv[2],'w'))
