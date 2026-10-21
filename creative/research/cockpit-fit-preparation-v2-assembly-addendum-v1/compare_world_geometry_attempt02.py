"""Actual evaluated triangles against actual delivery buffers; no model mutation."""
from pathlib import Path
import json,hashlib,collections
import numpy as np
from scipy.spatial import cKDTree
H=Path(__file__).resolve().parent;sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest();a=np.load(H/'evaluated-arrays.npz');meta=json.loads((H/'evaluated-source-assembly.json').read_text());glb=json.loads((H/'delivery-buffer-arrays.json').read_text());rows=[]
def cyclic(t):
 t=tuple(int(i)for i in t);k=t.index(min(t));return t[k:]+t[:k]
for e in glb['entries']:
 key=e['key'];src=a['source_'+key+'__world'].astype(np.float64);expected=src[:,[0,2,1]];expected[:,2]*=-1;actual=np.array(e['positions_world_glTF'],dtype=np.float64);st=a['source_'+key+'__triangles'];gt=np.array(e['triangles'],dtype=np.int32)
 tree=cKDTree(expected);dist,mapped=tree.query(actual,k=1,workers=1);rd,_=cKDTree(actual).query(expected,k=1,workers=1)
 before=collections.Counter(cyclic(t)for t in st);after=collections.Counter(cyclic(t)for t in mapped[gt]);same=before==after
 # Every real delivered triangle is matched to a real source triangle, with cyclic
 # orientation preserved; index splits from UV/normal seams are mapped by position.
 max_corner=0.;triangle_map=[]
 if same:
  available={}
  for i,t in enumerate(st):available.setdefault(cyclic(t),[]).append(i)
  for i,t in enumerate(gt):
   j=available[cyclic(mapped[t])].pop();triangle_map.append(j);S=expected[st[j]];G=actual[t];errors=[float(np.max(np.linalg.norm(G-np.roll(S,-k,axis=0),axis=1)))for k in range(3)];max_corner=max(max_corner,min(errors))
 assert same,(key,'Actual oriented triangle multiset differs',len(before-after),len(after-before))
 assert max(dist.max(),rd.max(),max_corner)<=5e-8,(key,'World geometry exceeds50nm',dist.max(),rd.max(),max_corner)
 r={'key':key,'source_vertices':len(expected),'delivery_vertices':len(actual),'actual_triangles':len(st),'delivery_triangles':len(gt),'GLB_to_source_max_vertex_distance_m':float(dist.max()),'source_to_GLB_max_vertex_distance_m':float(rd.max()),'every_oriented_triangle_multiset_identical_after_actual_position_mapping':same,'maximum_matched_triangle_corner_world_distance_m':max_corner,'mapped_source_vertex_indices_sha256':hashlib.sha256(mapped.astype(np.int32).tobytes()).hexdigest(),'matched_source_triangle_indices_sha256':hashlib.sha256(np.asarray(triangle_map,dtype=np.int32).tobytes()).hexdigest()}
 rows.append(r)
report={'schema':1,'method':'Fresh evaluated Blender source world vertices converted(x,z,-y); real indexed POSITION buffers transformed by real delivery node worldmatrix. Bidirectional nearest actual vertices; exact oriented triangle multiset after seam-duplicate position mapping; every matched triangle corner distance computed. No pixel metric or browser matrix used to derive source.','tolerance_m':5e-8,'entries':rows,'input_arrays_sha256':sha(H/'evaluated-arrays.npz'),'input_delivery_buffers_sha256':sha(H/'delivery-buffer-arrays.json'),'tool_sha256':sha(__file__),'source_vs_assembly_all_four_arrays_bit_identical':all(v['bit_identical']for x in meta['entries']for v in x['source_vs_assembly'].values()),'models_modified':False}
report['source_vs_assembly_local_positions_and_triangles_bit_identical']=all(x['source_vs_assembly'][f]['bit_identical']for x in meta['entries']for f in ['local','triangles'])
report['source_vs_assembly_max_world_coordinate_delta_m']=max(x['source_vs_assembly']['world']['max_absolute_delta']for x in meta['entries'])
assert report['source_vs_assembly_local_positions_and_triangles_bit_identical']
assert report['source_vs_assembly_max_world_coordinate_delta_m']<=5e-8
(H/'world-geometry-parity.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
