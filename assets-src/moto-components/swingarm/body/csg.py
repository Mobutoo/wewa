"""Source-only constructive solids from original authored volumes; no imported geometry."""
import json,sys
from importlib.metadata import version
import manifold3d as m
import numpy as np
src=json.loads(open(sys.argv[1]).read());stages=[]
def solid(row):
 out=m.Manifold(m.Mesh(np.asarray(row['vertices'],dtype=np.float32),np.asarray(row['triangles'],dtype=np.uint32)))
 assert out.status()==m.Error.NoError,(row['name'],out.status())
 assert out.volume()>0,(row['name'],'nonpositive operand volume')
 return out
result=solid(src['base'])
for operation in ['features','drills']:
 for row in src[operation]:
  operand=solid(row);before=result.volume();result=result+operand if operation=='features' else result-operand;after=result.volume()
  assert result.status()==m.Error.NoError and after>0,(row['name'],result.status(),after)
  assert after>=before-1e-11 if operation=='features' else after<=before+1e-11
  stages.append({'operation':'union' if operation=='features' else 'subtract','name':row['name'],'before_volume_m3':before,'after_volume_m3':after,'status':'NoError'})
parts=len(result.decompose());assert parts==1,('Disconnected body',parts)
out=result.to_mesh();report={'vertices':out.vert_properties[:,:3].tolist(),'triangles':out.tri_verts.tolist(),'stages':stages,'tool':'manifold3d','tool_version':version('manifold3d'),'solid_components':parts,'volume_m3':result.volume()}
open(sys.argv[2],'w').write(json.dumps(report));print('WEWA_SWINGARM_SOURCE_CSG',len(report['vertices']),len(report['triangles']),report['volume_m3'])
