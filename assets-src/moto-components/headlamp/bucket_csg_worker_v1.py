"""Original constructive solids only; external manifold CPU process, no source edits."""
import json,sys,numpy as np,manifold3d as m
from importlib.metadata import version
d=json.load(open(sys.argv[1]));stages=[]
def solid(row):
 a=m.Manifold(m.Mesh(np.asarray(row['vertices'],np.float32),np.asarray(row['triangles'],np.uint32)));assert a.status()==m.Error.NoError and a.volume()>0,(row['name'],a.status(),a.volume());return a
r=solid(d['base'])
for op in ['features','drills']:
 for row in d[op]:
  before=r.volume();p=solid(row);r=r+p if op=='features' else r-p;assert r.status()==m.Error.NoError and r.volume()>0,(row['name'],r.status());stages.append({'operation':op,'name':row['name'],'before_m3':before,'after_m3':r.volume()})
assert len(r.decompose())==1
mesh=r.to_mesh();json.dump({'vertices':mesh.vert_properties[:,:3].tolist(),'triangles':mesh.tri_verts.tolist(),'stages':stages,'worker':'manifold3d','version':version('manifold3d')},open(sys.argv[2],'w'))
