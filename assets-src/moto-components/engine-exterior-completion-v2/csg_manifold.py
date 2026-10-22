import sys,json
from pathlib import Path
import numpy as np
sys.path.insert(0,'/workspace/scratch/engine-v2-csg-deps')
import manifold3d as m
O=Path(__file__).resolve().parent;d=np.load(O/'csg-inputs.npz');solids=[];rows=[]
for key in ['body','apron','tool']:
 mesh=m.Mesh(np.asarray(d[key+'_v'],dtype=np.float32),np.asarray(d[key+'_f'],dtype=np.uint32));solid=m.Manifold(mesh);rows.append(dict(key=key,status=str(solid.status()),triangles=solid.num_tri(),volume=solid.volume()));assert solid.status()==m.Error.NoError,rows[-1];solids.append(solid)
result=(solids[0]+solids[1])-solids[2];assert result.status()==m.Error.NoError,result.status();mesh=result.to_mesh();np.savez_compressed(O/'csg-result.npz',vertices=mesh.vert_properties[:,:3],triangles=mesh.tri_verts);(O/'csg-operation-check.json').write_text(json.dumps(dict(solver='manifold3d 3.5.4',inputs=rows,result=dict(status=str(result.status()),triangles=result.num_tri(),volume=result.volume()),operation='same photographed casting union then original source service clearance difference; no welding or remeshing'),indent=2))
