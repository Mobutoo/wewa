"""Exact original volume/triangle ownership for this housing's own CAD geometry."""
import json,sys,numpy as np,manifold3d as m
from importlib.metadata import version
d=json.load(open(sys.argv[1]));rows=[d['base']]+d['features']+d['drills'];ids={row['name']:m.Manifold.reserve_ids(1)for row in rows};owners={ids[row['name']]:i for i,row in enumerate(rows)}
def solid(row):
 n=len(row['triangles']);mesh=m.Mesh(np.asarray(row['vertices'],np.float32),np.asarray(row['triangles'],np.uint32),run_index=np.asarray([0,3*n],np.uint32),run_original_id=np.asarray([ids[row['name']]],np.uint32),face_id=np.arange(n,dtype=np.uint32));s=m.Manifold(mesh);assert s.status()==m.Error.NoError and s.volume()>0,(row['name'],s.status());return s
r=solid(d['base']);stages=[]
for op in ['features','drills']:
 for row in d[op]:
  before=r.volume();v=solid(row);original_intersection=(solid(d['base'])^v)if ('firstupperpad true throughhole' in row['name'] or ' pad throughhole ' in row['name'] or 'P6 shapedreturn bore' in row['name']) else None
  if original_intersection is not None and 'P6 shapedreturn bore' not in row['name']:assert original_intersection.volume()==0 and original_intersection.num_tri()==0,('Localpad drill must not pierce originalcowl',original_intersection.volume(),original_intersection.num_tri())
  r=r+v if op=='features'else r-v;assert r.status()==m.Error.NoError and r.volume()>0;stages.append({'operation':op,'name':row['name'],'before_volume_m3':before,'after_volume_m3':r.volume(),'connected_components_after_operation':len(r.decompose()),'original_cowl_drill_intersection_volume_m3':original_intersection.volume()if original_intersection is not None else None,'original_cowl_drill_intersection_triangles':original_intersection.num_tri()if original_intersection is not None else None})
components=r.decompose()
if len(components)!=1:
 diagnostic={'rejected':True,'reason':'Disconnectedcandidatefeatures afterCSG, no mesh export permitted','stages':stages,'components':[{'volume_m3':c.volume(),'bbox_min_max_m':[np.asarray(c.to_mesh().vert_properties)[:,:3].min(0).tolist(),np.asarray(c.to_mesh().vert_properties)[:,:3].max(0).tolist()]}for c in components]}
 json.dump(diagnostic,open(sys.argv[2],'w'));print(json.dumps(diagnostic));sys.exit(0)
mesh=r.to_mesh();idsout=[None]*len(mesh.tri_verts)
for k,oid in enumerate(mesh.run_original_id):
 for t in range(mesh.run_index[k]//3,mesh.run_index[k+1]//3):idsout[t]=owners[int(oid)]
assert all(isinstance(x,int)for x in idsout);json.dump({'vertices':mesh.vert_properties[:,:3].tolist(),'triangles':mesh.tri_verts.tolist(),'triangle_source_owners':idsout,'triangle_source_face_ids':list(mesh.face_id),'stages':stages,'worker':'manifold3d','version':version('manifold3d'),'connected_components':len(r.decompose())},open(sys.argv[2],'w'))
