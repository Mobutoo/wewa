"""Legacy filename retained; final pipeline only audits, never repairs buffers.
Source seam cleanup makes post-export tangent repair unnecessary. Fail on any
future non-unit/nonorthogonal tangent instead of hiding a new source defect.
"""
import json,struct,hashlib
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/handlebar-clamps-v1';data=(HERE/'handlebar-clamps-inspection.glb').read_bytes();sha=hashlib.sha256(data).hexdigest();jlen=struct.unpack_from('<I',data,12)[0];d=json.loads(data[20:20+jlen]);bstart=20+jlen+8;sizes={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4};types={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}
def accessor(i):
 a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];dtype=np.dtype(types[a['componentType']]);n=sizes[a['type']];return np.ndarray((a['count'],n),dtype=dtype,buffer=data,offset=bstart+v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',dtype.itemsize*n),dtype.itemsize))
checks=[]
for mi,m in enumerate(d['meshes']):
 for pi,p in enumerate(m['primitives']):
  if 'normalTexture' not in d['materials'][p['material']]:continue
  t=accessor(p['attributes']['TANGENT']).astype(float);n=accessor(p['attributes']['NORMAL']).astype(float);length=np.linalg.norm(t[:,:3],axis=1);dots=np.sum(t[:,:3]*n,axis=1);assert np.max(abs(length-1))<.001 and np.max(abs(dots))<.001,(mi,pi,'Source tangent frame invalid: stop and correct source');checks.append({'mesh':mi,'primitive':pi,'vectors':len(t),'max_unit_length_error':float(np.max(abs(length-1))),'max_normal_dot':float(np.max(abs(dots)))})
report={'input_export_sha256':sha,'export_sha256':sha,'method_counts':{'Gram-Schmidt projection':0,'analytic UV fallback on negligible sliver':0},'method':'Strict final tangent frame audit; source cleaned; no export repairs permitted','repaired_vectors':[],'checks':checks,'other_buffers_unchanged':True,'geometry_unchanged':True,'art_accepted':False};(OUT/'tangent-buffer-repair.json').write_text(json.dumps(report,indent=2)+'\n');print('WEWA_TANGENT_AUDIT',len(checks),'normal-mapped primitives, no repairs')
