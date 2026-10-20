"""Robust processing of this component's original construction volumes only."""
import json,sys
import numpy as np
import manifold3d as m
from importlib.metadata import version
data=json.loads(open(sys.argv[1]).read())
def solid(row):
 value=m.Manifold(m.Mesh(np.asarray(row['vertices'],dtype=np.float32),np.asarray(row['triangles'],dtype=np.uint32)))
 assert value.status()==m.Error.NoError and value.volume()>0,(row['name'],value.status(),value.volume())
 return value
result=solid(data['base']);stages=[]
for operation in ['features','drills']:
 for row in data[operation]:
  before=result.volume();part=solid(row);result=result+part if operation=='features' else result-part
  assert result.status()==m.Error.NoError and result.volume()>1e-12,(row['name'],result.status(),result.volume())
  stages.append({'operation':operation,'part':row['name'],'before_volume_m3':before,'after_volume_m3':result.volume()})
parts=len(result.decompose());assert parts==1,('Disconnected component',parts)
mesh=result.to_mesh();out={'vertices':mesh.vert_properties[:,:3].tolist(),'triangles':mesh.tri_verts.tolist(),'stages':stages,'solid_components':parts,'volume_m3':result.volume(),'worker':'manifold3d','worker_version':version('manifold3d')}
open(sys.argv[2],'w').write(json.dumps(out))
