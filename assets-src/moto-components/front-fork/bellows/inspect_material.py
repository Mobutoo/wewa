"""Read actual GLB image payloads, texture roles and original authored pixels."""
import json,struct,io,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/fork-bellows-v1'
data=(HERE/'fork-bellows-inspection.glb').read_bytes();jlen,jtype=struct.unpack_from('<II',data,12);d=json.loads(data[20:20+jlen]);binary=data[20+jlen+8:];assert len(d['materials'])==1;m=d['materials'][0]
assert abs(m['normalTexture']['scale']-.55)<1e-5
rows=[]
for role,index,name in [('normal',m['normalTexture']['index'],'bellows-original-normal.png'),('metallic-roughness',m['pbrMetallicRoughness']['metallicRoughnessTexture']['index'],'bellows-original-metallic-roughness.png')]:
 im=d['images'][d['textures'][index]['source']];v=d['bufferViews'][im['bufferView']];raw=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]
 exported=np.array(Image.open(io.BytesIO(raw)).convert('RGB'));original=np.array(Image.open(HERE/'textures'/name).convert('RGB'))
 assert exported.shape==original.shape and np.array_equal(exported,original)
 std=exported.reshape(-1,3).std(0)
 if role=='normal':assert std[0]>1 and std[1]>1 and exported[:,:,2].mean()>250
 else:assert std[1]>1 and exported[:,:,2].max()==0 and exported[:,:,0].min()==255
 rows.append({'role':role,'embedded_sha256':hashlib.sha256(raw).hexdigest(),'shape_px':list(exported.shape),'channel_std':std.tolist(),'pixels_identical_to_authored_PNG':True})
r={'export_sha256':hashlib.sha256(data).hexdigest(),'actual_embedded_images':rows,'metallic_zero':True,'normal_strength':m['normalTexture']['scale'],'reference_pixels_used':False,'reflectance_measured':False}
(OUT/'material-buffer-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
