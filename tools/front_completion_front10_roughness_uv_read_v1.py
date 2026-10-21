"""Read actual GLB scalar texture UVs and packed G channel; no reference/visual acceptance."""
import struct,json,sys,io,hashlib,math
from pathlib import Path
from PIL import Image
p=Path(sys.argv[1]);out=Path(sys.argv[2]);b=p.read_bytes();o=12
while o<len(b):
 n,t=struct.unpack_from('<II',b,o);v=b[o+8:o+8+n]
 if t==0x4e4f534a:j=json.loads(v)
 if t==0x004e4942:data=v
 o+=n+8
def acc(i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];fmt={5126:'f',5125:'I',5123:'H'}[a['componentType']];n={'VEC3':3,'VEC2':2,'SCALAR':1}[a['type']];size=struct.calcsize(fmt);stride=v.get('byteStride',n*size);base=v.get('byteOffset',0)+a.get('byteOffset',0);return [struct.unpack_from('<'+fmt*n,data,base+k*stride)for k in range(a['count'])]
counts={'planar_triangles':0,'constant_cast_triangles':0,'constant_machined_triangles':0};maxerr=0.;bad=0;Gs=set()
for mesh in j['meshes']:
 for q in mesh['primitives']:
  binding=j['materials'][q['material']]['pbrMetallicRoughness']['metallicRoughnessTexture'];tex=j['textures'][binding['index']];img=j['images'][tex['source']];v=j['bufferViews'][img['bufferView']];im=Image.open(io.BytesIO(data[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']])).convert('RGB');positions=acc(q['attributes']['POSITION']);uv=acc(q['attributes']['TEXCOORD_'+str(binding.get('texCoord',0))]);idx=[x[0]for x in acc(q['indices'])]
  for k in range(0,len(idx),3):
   ids=idx[k:k+3];flat=all(abs(positions[i][1]-.027)<1e-7 for i in ids)
   if flat:
    counts['planar_triangles']+=1
    for i in ids:
     want=(.5+positions[i][0]/.13,.5+positions[i][2]/.13);e=max(abs(a-c)for a,c in zip(uv[i],want));maxerr=max(maxerr,e);bad+=e>2e-6
   else:
    same=max(abs(uv[i][c]-uv[ids[0]][c])for i in ids for c in [0,1])<1e-7
    if not same:bad+=1;continue
    u,v=uv[ids[0]];pix=im.getpixel((min(im.width-1,max(0,int(u*im.width))),min(im.height-1,max(0,int(v*im.height)))));Gs.add(pix[1]);counts['constant_machined_triangles'if pix[1]==56 else 'constant_cast_triangles']+=1;bad+=pix[1]not in [56,107]
report={'GLB':str(p),'sha256':hashlib.sha256(b).hexdigest(),'actual_triangle_UV_counts':counts,'maximum_planar_UV_error':maxerr,'unexpected_mapping_count':bad,'constant_samples_actual_G':sorted(Gs),'constant_UV_intentional':'Roughness scalar only; no normal map or tangent basis','scope':'Actual exported binding/UV/pixels, not measured finish or art acceptance'};out.write_text(json.dumps(report,indent=2));print(json.dumps(report));assert bad==0
