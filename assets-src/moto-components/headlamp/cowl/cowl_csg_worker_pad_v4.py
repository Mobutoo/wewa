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
mesh=r.to_mesh()
# Normalize ONLYa provenFloat32degeneration. No simplify/toleranceincrease.
def cyclic_triangle_keys(mesh):
 vv=np.asarray(mesh.vert_properties[:,:3],np.float32);tt=np.asarray(mesh.tri_verts,dtype=np.int64);points=vv[tt];bits=np.ascontiguousarray(points).view(np.uint32);start=np.lexsort((bits[:,:,2],bits[:,:,1],bits[:,:,0]),axis=1)[:,0];order=(start[:,None]+np.arange(3)[None,:])%3;canonical=np.take_along_axis(bits,order[:,:,None],axis=1).reshape(len(tt),9);origin=np.zeros(len(tt),np.uint32)
 for k,oid in enumerate(mesh.run_original_id):origin[mesh.run_index[k]//3:mesh.run_index[k+1]//3]=int(oid)
 keys=np.column_stack([origin,np.asarray(mesh.face_id,np.uint32),canonical]);return keys,points
old_keys,old_points=cyclic_triangle_keys(mesh);crosses=np.cross(old_points[:,1].astype(np.float64)-old_points[:,0],old_points[:,2].astype(np.float64)-old_points[:,0]);zero=np.linalg.norm(crosses,axis=1)==0;transport={'normalization_applied':False,'exact_zero_areas_before':int(np.sum(zero))}
if np.any(zero):
 before_vertices=np.asarray(mesh.vert_properties[:,:3],np.float32);before_count=len(mesh.tri_verts);before_volume=r.volume();before_tol=r.get_tolerance();rr=m.Manifold(mesh);assert rr.status()==m.Error.NoError and rr.volume()>0 and len(rr.decompose())==1;after=rr.to_mesh();new_keys,new_points=cyclic_triangle_keys(after);expected=old_keys[~zero]
 def sortedkeys(keys):return keys[np.lexsort(tuple(keys[:,k]for k in range(keys.shape[1]-1,-1,-1)))]
 assert np.array_equal(sortedkeys(expected),sortedkeys(new_keys)),'Transport changed a nonzeroorientedtriangle/origin/faceID'
 all_positions_retained=all(tuple(v)in set_positions for v in[])if False else True
 old_positions=set(map(tuple,before_vertices));assert all(tuple(v)in old_positions for v in np.asarray(after.vert_properties[:,:3],np.float32)),'Transport moved/generatedvertices'
 new_cross=np.cross(new_points[:,1].astype(np.float64)-new_points[:,0],new_points[:,2].astype(np.float64)-new_points[:,0]);assert np.all(np.linalg.norm(new_cross,axis=1)>0),'Stilldegenerateafterroundtrip';transport.update(normalization_applied=True,input_vertices=len(before_vertices),output_vertices=len(after.vert_properties),input_triangles=before_count,output_triangles=len(after.tri_verts),removed_triangles=int(np.sum(zero)),all_remaining_oriented_triangles_positions_originIDs_faceIDs_bitidentical=True,all_output_positions_bitidentical_subset=True,max_vertex_displacement_m=0,volume_before_internalDouble_m3=before_volume,volume_after_Float32_m3=rr.volume(),tolerance_before=before_tol,tolerance_after=rr.get_tolerance(),explicit_simplify_or_tolerance_change=False,connected_components_after=len(rr.decompose()),exact_zero_areas_after=0);mesh=after;r=rr
idsout=[None]*len(mesh.tri_verts)
for k,oid in enumerate(mesh.run_original_id):
 for t in range(mesh.run_index[k]//3,mesh.run_index[k+1]//3):idsout[t]=owners[int(oid)]
assert all(isinstance(x,int)for x in idsout);json.dump({'vertices':mesh.vert_properties[:,:3].tolist(),'triangles':mesh.tri_verts.tolist(),'triangle_source_owners':idsout,'triangle_source_face_ids':list(mesh.face_id),'stages':stages,'worker':'manifold3d','version':version('manifold3d'),'connected_components':len(r.decompose()),'float32_transport_normalization':transport},open(sys.argv[2],'w'))
