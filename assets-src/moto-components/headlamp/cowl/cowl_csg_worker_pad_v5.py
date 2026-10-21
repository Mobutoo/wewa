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
assert all(isinstance(x,int)for x in idsout)
# Preserve Float32 positions/boundaries while avoiding a quantized CSG sliver.
vv=np.asarray(mesh.vert_properties[:,:3],np.float32).astype(np.float64);tt=np.asarray(mesh.tri_verts,np.uint32).copy();fids=np.asarray(mesh.face_id,np.uint32);ownerarr=np.asarray(idsout,np.int32)
def values(tri,owner,fid):
 row=rows[owner];a,b,c=np.asarray(row['vertices'],np.float64)[np.asarray(row['triangles'][fid],np.int64)];v0=b-a;v1=c-a;d00=v0@v0;d01=v0@v1;d11=v1@v1;den=d00*d11-d01*d01;assert den>0;pts=vv[np.asarray(tri,np.int64)];q=pts-a;d20=q@v0;d21=q@v1;be=(d11*d20-d01*d21)/den;ga=(d00*d21-d01*d20)/den;weights=np.column_stack([1-be-ga,be,ga]);normal=weights@np.asarray(row['corner_normals'][fid],np.float64);normal/=np.linalg.norm(normal,axis=1)[:,None];normal*=1 if owner<=len(d['features'])else-1;cross=np.cross(pts[1]-pts[0],pts[2]-pts[0]);length=np.linalg.norm(cross);fn=cross/length if length else np.zeros(3);uv=(weights@np.asarray(row['triangle_UV'][fid],np.float64)).astype(np.float32).astype(np.float64);uvcross=np.linalg.det(np.array([uv[1]-uv[0],uv[2]-uv[0]]));on=np.cross(v0,v1);on/=np.linalg.norm(on);on*=1 if owner<=len(d['features'])else-1
 return {'min_dot':float(np.min(normal@fn))if length else-1,'area_m2':float(length/2),'original_face_normal_dot':float(on@fn),'UV_area_after_Float32':abs(float(uvcross))/2,'max_original_plane_distance_m':float(max(abs((pts-a)@on))),'min_bary':float(weights.min()),'max_bary':float(weights.max())}
# Vectorized original-field interpolation to identify ONLY actual failing faces.
mindots=np.ones(len(tt))
for owner,row in enumerate(rows):
 ix=np.flatnonzero(ownerarr==owner)
 if not len(ix):continue
 sf=fids[ix];abc=np.asarray(row['vertices'],np.float64)[np.asarray(row['triangles'],np.int64)[sf]];aa=abc[:,0];ab=abc[:,1]-aa;ac=abc[:,2]-aa;q=vv[tt[ix]]-aa[:,None,:];d00=np.sum(ab*ab,axis=1);d01=np.sum(ab*ac,axis=1);d11=np.sum(ac*ac,axis=1);den=d00*d11-d01*d01;assert np.all(den>0);d20=np.einsum('ntk,nk->nt',q,ab);d21=np.einsum('ntk,nk->nt',q,ac);be=(d11[:,None]*d20-d01[:,None]*d21)/den[:,None];ga=(d00[:,None]*d21-d01[:,None]*d20)/den[:,None];weights=np.stack([1-be-ga,be,ga],axis=2);nn=np.einsum('ntk,nkc->ntc',weights,np.asarray(row['corner_normals'],np.float64)[sf]);nn/=np.linalg.norm(nn,axis=2)[:,:,None];nn*=1 if owner<=len(d['features'])else-1;points=vv[tt[ix]];cross=np.cross(points[:,1]-points[:,0],points[:,2]-points[:,0]);fn=cross/np.linalg.norm(cross,axis=1)[:,None];mindots[ix]=np.min(np.sum(nn*fn[:,None,:],axis=2),axis=1)
failures=np.flatnonzero(mindots<.9);flips=[]
def patch_boundary(triangles):
 from collections import Counter
 result=Counter()
 for tri in triangles:
  for a,b in zip(tri,np.roll(tri,-1)):
   a=int(a);b=int(b)
   if result[(b,a)]:result[(b,a)]-=1
   else:result[(a,b)]+=1
 return +result
for tid in failures:
 owner=int(ownerarr[tid]);fid=int(fids[tid]);old=tt[tid].copy();best=None
 for k in range(3):
  u,v,w=map(int,[old[k],old[(k+1)%3],old[(k+2)%3]]);neighbors=np.flatnonzero(np.sum(np.isin(tt,[u,v]),axis=1)==2)
  for nid in neighbors:
   if nid==tid or ownerarr[nid]!=owner or fids[nid]!=fid:continue
   neighbor=tt[nid].copy();z=next(int(x)for x in neighbor if x not in[u,v]);new=np.array([[w,z,v],[z,w,u]],np.uint32)
   if len({u,v,w,z})!=4 or patch_boundary([old,neighbor])!=patch_boundary(new):continue
   checks=[values(t,owner,fid)for t in new]
   if any(c['min_dot']<=.905 or c['original_face_normal_dot']<.99 or c['UV_area_after_Float32']==0 or c['max_original_plane_distance_m']>1e-7 or c['min_bary']<-.001 or c['max_bary']>1.001 for c in checks):continue
   score=min(c['min_dot']for c in checks)
   if best is None or score>best[0]:best=(score,int(nid),neighbor,new,checks)
 if best is None:
  json.dump({'rejected':True,'reason':'No boundary/position/ownership preserving internaldiagonal flip resolves quantized CSGsliver','triangle':int(tid),'source_owner':owner,'source_face':fid,'check':values(old,owner,fid)},open(sys.argv[2],'w'));sys.exit(0)
 score,nid,neighbor,new,checks=best;oldchecks=[values(t,owner,fid)for t in[old,neighbor]];origin=vv[old[0]];oldvol=sum(np.dot(vv[t[0]]-origin,np.cross(vv[t[1]]-origin,vv[t[2]]-origin))/6 for t in[old,neighbor]);newvol=sum(np.dot(vv[t[0]]-origin,np.cross(vv[t[1]]-origin,vv[t[2]]-origin))/6 for t in new);tt[tid],tt[nid]=new;flips.append({'changed_triangle_indices':[int(tid),nid],'source_input':owner,'source_face':fid,'vertices_before':[old.tolist(),neighbor.tolist()],'vertices_after':new.tolist(),'same_oriented_patch_boundary':True,'all_vertex_positions_unchanged':True,'source_ownership_unchanged':True,'before_checks':oldchecks,'after_checks':checks,'signed_patch_volume_delta_from_Float32_noncoplanarity_m3':float(newvol-oldvol)})
if flips:
 print('FLOAT32_DIAGONAL_CANDIDATE',json.dumps(flips),flush=True);validator=m.Manifold(m.Mesh(np.ascontiguousarray(mesh.vert_properties,dtype=np.float32).copy(order="C"),np.ascontiguousarray(tt,dtype=np.uint32).copy(order="C"),run_index=np.ascontiguousarray(mesh.run_index,dtype=np.uint32).copy(order="C"),run_original_id=np.ascontiguousarray(mesh.run_original_id,dtype=np.uint32).copy(order="C"),face_id=np.ascontiguousarray(fids,dtype=np.uint32).copy(order="C")));assert validator.status()==m.Error.NoError and validator.volume()>0 and len(validator.decompose())==1 and validator.num_tri()==len(tt),'Changedboundary/topology/trianglecount';print('FLOAT32_DIAGONAL_TRANSPORT',json.dumps(flips))
json.dump({'vertices':mesh.vert_properties[:,:3].tolist(),'triangles':tt.tolist(),'triangle_source_owners':idsout,'triangle_source_face_ids':fids.tolist(),'stages':stages,'worker':'manifold3d','version':version('manifold3d'),'connected_components':len(r.decompose()),'float32_transport_normalization':transport,'float32_diagonal_transport':{'applied':bool(flips),'flips':flips,'positions_unchanged':True,'normal_field_not_repaired':True,'scope':'Only an internal diagonal between two triangles of exactsame original inputface. Boundary and vertexpositions retained; finiteFloat32 noncoplanarity volume delta documented. No shape parameter change or globalremeshing.'}},open(sys.argv[2],'w'))
