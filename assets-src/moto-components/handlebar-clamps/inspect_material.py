"""Read actual GLB embedded image bytes, compare pixels with original authored maps."""
import json,struct,io,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/handlebar-clamps-v1';data=(HERE/'handlebar-clamps-inspection.glb').read_bytes();jlen,jtype=struct.unpack_from('<II',data,12);d=json.loads(data[20:20+jlen]);bstart=20+jlen+8;binary=data[bstart:];mat=d['materials'][0]
assert mat['normalTexture'].get('scale',1)>.99 and 'metallicRoughnessTexture' in mat['pbrMetallicRoughness']
rows=[]
for role,index,name in [('normal',mat['normalTexture']['index'],'clamp-coating-normal.png'),('metallic-roughness',mat['pbrMetallicRoughness']['metallicRoughnessTexture']['index'],'clamp-coating-metallic-roughness.png')]:
 im=d['images'][d['textures'][index]['source']];v=d['bufferViews'][im['bufferView']];raw=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];embedded=np.array(Image.open(io.BytesIO(raw)).convert('RGB'));original=np.array(Image.open(HERE/'textures'/name).convert('RGB'));assert embedded.shape==original.shape and np.array_equal(embedded,original),(role,'Embedded pixels differ');std=embedded.reshape(-1,3).std(0)
 if role=='normal':assert std[0]>1 and std[1]>1 and embedded[:,:,2].mean()>240
 else:assert std[1]>1 and std[2]<.01 and abs(embedded[:,:,2].mean()/255-.65)<.006
 rows.append({'role':role,'embedded_image_sha256':hashlib.sha256(raw).hexdigest(),'pixel_sha256':hashlib.sha256(embedded.tobytes()).hexdigest(),'shape_px':list(embedded.shape),'pixel_channel_std':std.tolist(),'authored_png_pixels_identical':True})
seat=next(m for m in d['materials'] if 'satin tube-contact' in m['name']);assert 'normalTexture' not in seat and abs(seat['pbrMetallicRoughness']['roughnessFactor']-.27)<1e-6
report={'satin_contact_material_actual':seat,'export_sha256':hashlib.sha256(data).hexdigest(),'actual_embedded_images':rows,'normal_and_ORM_channels_checked':True,'source_photo_pixels_used':False,'reflectance_measured':False,'art_accepted':False};(OUT/'material-buffer-check.json').write_text(json.dumps(report,indent=2)+'\n');print('WEWA_MATERIAL_BUFFER',json.dumps(report))
