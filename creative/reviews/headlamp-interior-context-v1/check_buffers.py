import pathlib,struct,json,math,hashlib
R=pathlib.Path('/workspace/wewa');D=R/'creative/reviews/headlamp-interior-context-v1';inputs=json.loads((D/'native-inputs.json').read_text());paths=[(R/v['path']).with_suffix('.glb') for v in inputs.values()];paths.append(R/'assets-src/moto-components/headlamp-interior-context-v1/bulb-provisional.glb');res=[]
for p in paths:
 b=p.read_bytes();assert b[:4]==b'glTF';n,t=struct.unpack_from('<II',b,12);g=json.loads(b[20:20+n]);off=20+n;bn,bt=struct.unpack_from('<II',b,off);binary=b[off+8:off+8+bn];counts=[];bounds=[]
 for mesh in g['meshes']:
  for pr in mesh['primitives']:
   a=g['accessors'][pr['attributes']['POSITION']];v=g['bufferViews'][a['bufferView']];start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',12)
   xyz=[struct.unpack_from('<fff',binary,start+i*stride) for i in range(a['count'])];assert all(math.isfinite(c) for x in xyz for c in x)
   counts.append(a['count']);bounds.append([[min(x[i] for x in xyz),max(x[i] for x in xyz)] for i in range(3)])
 res.append({'path':str(p.relative_to(R)),'sha256':hashlib.sha256(b).hexdigest(),'position_counts':counts,'actual_position_bounds_gltf_m':bounds,'materials':g.get('materials',[]),'finite_positions':True})
(D/'export-buffer-audit.json').write_text(json.dumps(res,indent=2)+'\n');print([(r['path'],r['position_counts']) for r in res])
