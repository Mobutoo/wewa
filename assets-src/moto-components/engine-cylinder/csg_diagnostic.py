"""Robust union/cutting of original Blender construction volumes, no asset imports."""
import json,sys
from importlib.metadata import version
import manifold3d as m
import numpy as np
inputs=json.loads(open(sys.argv[1]).read());stages=[]
def solid(row):
 mesh=m.Mesh(np.asarray(row['vertices'],dtype=np.float32),np.asarray(row['triangles'],dtype=np.uint32));result=m.Manifold(mesh)
 assert result.status()==m.Error.NoError,(row['name'],result.status())
 assert result.volume()>0,(row['name'],'non-positive operand volume')
 return result
result=solid(inputs['base'])
for operation in ['features','drills']:
 for row in inputs[operation]:
  part=solid(row);before=result.volume();result=result+part if operation=='features' else result-part
  assert result.status()==m.Error.NoError,(row['name'],result.status())
  after=result.volume()
  assert after>0 and (after>=before-1e-10 if operation=='features' else after<=before+1e-10),(row['name'],before,after)
  if operation=='drills':assert after>.5*before,(row['name'],'unexpected removal of most casting',before,after)
  print('STAGE_COMPONENTS',operation,row['name'],len(result.decompose()),[p.volume()for p in result.decompose()],flush=True)
  stages.append({'operation':'union' if operation=='features' else 'subtract','part':row['name'],'status':'NoError','before_volume_m3':before,'after_volume_m3':after})
components=len(result.decompose());assert components==1,('Disconnected casting solids',components)
mesh=result.to_mesh();out={'vertices':mesh.vert_properties[:,:3].tolist(),'triangles':mesh.tri_verts.tolist(),'stages':stages,'tool':'manifold3d','tool_version':version('manifold3d'),'solid_components':components,'volume_m3':result.volume()}
open(sys.argv[2],'w').write(json.dumps(out));print('WEWA_PANEL_CSG',json.dumps({k:out[k] for k in ['tool','tool_version','solid_components','volume_m3']}))
