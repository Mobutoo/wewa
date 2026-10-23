"""Remove zero-area cowl triangles from Blender export, preserving every vertex/material byte.
Keep raw export and record exact removals. New procedural pieces must have no such faces.
"""
from pathlib import Path
import json,hashlib
import numpy as np
from derive_handlebar_registration_v2 import decode,encode
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets-src/moto-components/visual-proportions-v2';REV=ROOT/'creative/reviews/visual-proportions-v2'
raw=(OUT/'proportion-additions-raw.glb').read_bytes();doc,binary=decode(raw);data=bytearray(binary);rows=[]
types={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}
def values(idx,n):
 a=doc['accessors'][idx];v=doc['bufferViews'][a['bufferView']];dtype=np.dtype(types[a['componentType']]);start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',dtype.itemsize*n)
 return np.ndarray((a['count'],n),dtype=dtype,buffer=binary,offset=start,strides=(stride,dtype.itemsize)).copy()
for mesh in doc['meshes']:
 for k,p in enumerate(mesh['primitives']):
  positions=values(p['attributes']['POSITION'],3).astype(float);idx=values(p['indices'],1).reshape(-1);tri=idx.reshape(-1,3)
  area=.5*np.linalg.norm(np.cross(positions[tri[:,1]]-positions[tri[:,0]],positions[tri[:,2]]-positions[tri[:,0]]),axis=1);keep=area>1e-15
  if keep.all():continue
  assert 'cowl' in mesh['name'].lower(),mesh['name']
  a=doc['accessors'][p['indices']];v=doc['bufferViews'][a['bufferView']];assert sum(x.get('bufferView')==a['bufferView'] for x in doc['accessors'])==1
  assert not v.get('byteStride')
  filtered=tri[keep].reshape(-1);blob=filtered.astype(types[a['componentType']]).tobytes();start=v.get('byteOffset',0)+a.get('byteOffset',0);data[start:start+len(blob)]=blob
  a['count']=len(filtered);v['byteLength']=a.get('byteOffset',0)+len(blob)
  if 'min'in a:a['min']=[int(filtered.min())]
  if 'max'in a:a['max']=[int(filtered.max())]
  rows.append({'mesh':mesh['name'],'primitive':k,'removed_triangles':int((~keep).sum()),'triangle_indices':np.flatnonzero(~keep).tolist(),'minimum_retained_area_m2':float(area[keep].min())})
final=encode(doc,bytes(data));(OUT/'proportion-additions.glb').write_bytes(final)
(REV/'triangle-cleanup.json').write_text(json.dumps({'raw_sha256':hashlib.sha256(raw).hexdigest(),'clean_sha256':hashlib.sha256(final).hexdigest(),'removed':rows,'vertices_normals_materials_unchanged':True,'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n')
print('COWL_TRIANGLE_CLEANUP',sum(r['removed_triangles'] for r in rows))
