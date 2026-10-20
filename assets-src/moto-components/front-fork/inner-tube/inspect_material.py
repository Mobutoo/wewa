"""Compare actual embedded texture pixels and channels with original authored PNGs."""
import json,struct,io,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/front-fork-inner-tube-v1';data=(HERE/'front-fork-inner-tube-inspection.glb').read_bytes();size=struct.unpack_from('<I',data,12)[0];j=json.loads(data[20:20+size]);binary=data[28+size:];rows=[]
for i,m in enumerate(j['materials']):
 for role,index,name in [('normal',m['normalTexture']['index'],'tube-original-directional-normal.png'),('ORM',m['pbrMetallicRoughness']['metallicRoughnessTexture']['index'],'tube-original-ORM-'+str(i)+'.png')]:
  im=j['images'][j['textures'][index]['source']];view=j['bufferViews'][im['bufferView']];raw=binary[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']];a=np.array(Image.open(io.BytesIO(raw)).convert('RGB'));b=np.array(Image.open(HERE/'textures'/name).convert('RGB'));assert np.array_equal(a,b);std=a.reshape(-1,3).std(0)
  if role=='normal':assert std[1]>.1 and a[:,:,2].mean()>250
  else:assert std[1]>1 and np.all(a[:,:,0]==255) and np.all(a[:,:,2]==255)
  rows.append({'material':m['name'],'role':role,'authored_pixels_equal':True,'embedded_sha256':hashlib.sha256(raw).hexdigest(),'pixel_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'shape_px':list(a.shape),'channel_std':std.tolist()})
r={'export_sha256':hashlib.sha256(data).hexdigest(),'embedded_images':rows,'channels_verified':True,'photo_pixels_used':False,'chemical_surface_measured':False,'art_accepted':False};(OUT/'material-buffer-check.json').write_text(json.dumps(r,indent=2)+'\n');print('WEWA_TUBE_PIXELS',json.dumps(r))
