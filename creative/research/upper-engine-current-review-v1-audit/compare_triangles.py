"""Actual GLB primitive buffers vs freshly evaluated source/copy arrays.
No new geometric distance tolerance: test exact local POSITIONs/topology; report world
float32/TRS roundoff and preserve builder v2's existing1e-6 matrix coefficient guard.
"""
from pathlib import Path
import json,hashlib,numpy as np
from scipy.spatial import cKDTree
H=Path(__file__).resolve().parent;A=np.load(H/'evaluated-arrays.npz');G=json.loads((H/'delivery-buffer-arrays.json').read_text());rows=[]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
Q=np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]],dtype=np.float64)
def oriented(t):
 k=np.argmin(t,axis=1);t=np.take_along_axis(t,(k[:,None]+np.arange(3))%3,axis=1);order=np.lexsort((t[:,2],t[:,1],t[:,0]));return t[order],order
for e in G['entries']:
 for origin in ['source','assembly']:
  key=e['key'];local=A[origin+'_'+key+'__local'].astype(np.float64);expected=local[:,[0,2,1]];expected[:,2]*=-1;actual=np.array(e['positions_local_glTF'],dtype=np.float64);tri=A[origin+'_'+key+'__triangles'];gt=np.array(e['triangles'],dtype=np.int64)
  dist,mapped=cKDTree(expected).query(actual,k=1,workers=1);back,_=cKDTree(actual).query(expected,k=1,workers=1)
  assert float(dist.max())==0 and float(back.max())==0,(key,origin,'Local POSITION differs',dist.max(),back.max())
  # Co-located vertices/UV or normal seams represent the same geometric corner;
  # merge exact coordinate duplicates in both references, preserving orientation and multiplicity.
  unique,rep=np.unique(expected,axis=0,return_inverse=True);before,si=oriented(rep[tri]);after,gi=oriented(rep[mapped[gt]])
  assert np.array_equal(before,after),(key,origin,'Oriented geometric triangle multiset differs')
  source_matrix=A[origin+'_'+key+'__matrix_world'];targetmatrix=Q@source_matrix@Q.T;glbmatrix=np.array(e['world_matrix_column_major']).reshape(4,4).T;delta=glbmatrix-targetmatrix
  assert np.max(np.abs(delta))<1e-6,(key,origin,'Existing builder coefficient guard exceeded',delta)
  expected_world=A[origin+'_'+key+'__world'].astype(np.float64)[:,[0,2,1]];expected_world[:,2]*=-1;world=np.array(e['positions_world_glTF'],dtype=np.float64);nearest=np.linalg.norm(world-expected_world[mapped],axis=1)
  # Exact local coordinates imply world displacement comes from evaluated matrix/TRS
  # roundoff plus Blender float32 point evaluation; test that algebra explicitly.
  predicted=actual@targetmatrix[:3,:3].T+targetmatrix[:3,3];world_from_glb=actual@glbmatrix[:3,:3].T+glbmatrix[:3,3]
  source_eval_error=predicted-expected_world[mapped];matrix_effect=actual@delta[:3,:3].T+delta[:3,3];residual=(world-expected_world[mapped])-(source_eval_error+matrix_effect)
  rows.append({'key':key,'reference':origin,'source_vertices':len(local),'delivery_vertices_with_primitive_seam_duplicates':len(actual),'triangles':len(tri),'delivery_triangles':len(gt),'local_positions_bidirectional_max_m':0.,'exact_oriented_geometric_triangle_multiset':True,'seam_policy':'Exact coincident coordinate vertices canonicalised, cyclic orientation and triangle multiplicity retained; no tolerance clustering or normal/UV acceptance inferred.','matrix_max_coefficient_delta':float(np.max(np.abs(delta))),'world_max_matched_corner_distance_m':float(nearest.max()),'world_transform_float64_algebra_residual_max_m':float(np.max(np.abs(residual))),'source_float32_point_evaluation_error_max_m':float(np.max(np.linalg.norm(source_eval_error,axis=1))),'actual_node_TRS_roundoff_effect_max_m':float(np.max(np.linalg.norm(matrix_effect,axis=1))),'matched_sorted_oriented_triangles_sha256':hashlib.sha256(before.astype(np.int64).tobytes()).hexdigest()})
report={'method':__doc__,'delivery_sha256':G['sha256'],'entries':rows,'drawn_mesh_instances':len(G['entries']),'drawn_triangles':sum(len(e['triangles'])for e in G['entries']),'maximum_world_corner_distance_m':max(r['world_max_matched_corner_distance_m']for r in rows),'matrix_coefficient_guard_reused_from_builder_v2':1e-6,'no_new_distance_threshold':True,'inputs':[{'path':str(H.name+'/'+p),'sha256':sha(H/p)}for p in ['evaluated-arrays.npz','evaluated-source-assembly.json','delivery-buffer-arrays.json']],'tool_sha256':sha(__file__),'no_model_modified':True}
(H/'oriented-triangle-parity.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in ['entries','inputs','method']},indent=2))
