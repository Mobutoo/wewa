"""Inspect actual embedded GLB pixels/material roles, no assumptions from node names."""
import json,struct,io,hashlib,numpy as np
from PIL import Image
from pathlib import Path
H=Path(__file__).resolve().parent;O=H.parents[2]/'creative/reviews/rear-rim-v1';data=(H/'rear-rim-inspection.glb').read_bytes();n,_=struct.unpack_from('<II',data,12);g=json.loads(data[20:20+n]);binary=data[28+n:];assert len(g['materials'])==2;body=next(m for m in g['materials']if'normalTexture'in m);inner=next(m for m in g['materials']if'normalTexture'not in m);assert abs(body['normalTexture']['scale']-.4)<1e-6;rows=[]
for role,index,name in [('normal',body['normalTexture']['index'],'rear-rim-original-normal.png'),('metallic-roughness',body['pbrMetallicRoughness']['metallicRoughnessTexture']['index'],'rear-rim-original-metallic-roughness.png')]:
 image=g['images'][g['textures'][index]['source']];v=g['bufferViews'][image['bufferView']];raw=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];a=np.array(Image.open(io.BytesIO(raw)).convert('RGB'));b=np.array(Image.open(H/'textures'/name).convert('RGB'));assert np.array_equal(a,b) and a.shape==(512,512,3);std=a.reshape(-1,3).std(0)
 if role=='normal':assert std[0]>0 and std[1]>0 and a[:,:,2].mean()>250
 else:assert std[1]>0 and a[:,:,2].max()==a[:,:,2].min() and a[:,:,0].min()==255
 rows.append({'role':role,'embedded_sha256':hashlib.sha256(raw).hexdigest(),'size_px':[512,512],'pixels_identical_to_author_PNG':True,'channel_min':a.reshape(-1,3).min(0).tolist(),'channel_max':a.reshape(-1,3).max(0).tolist(),'channel_std':std.tolist()})
p=inner['pbrMetallicRoughness'];assert abs(p['roughnessFactor']-.27)<1e-6 and abs(p['metallicFactor']-.55)<1e-6 and'normalTexture'not in inner
r={'export_sha256':hashlib.sha256(data).hexdigest(),'actual_material_count':2,'normal_mapped_material_count':1,'actual_embedded_images':rows,'normal_strength':body['normalTexture']['scale'],'body_baseColor_linear':body['pbrMetallicRoughness']['baseColorFactor'],'inner_surface_roughness':p['roughnessFactor'],'inner_surface_metallic':p['metallicFactor'],'inner_normalmap_present':False,'inner_surface_is_certified_friction_or_bearing_seat':False,'photo_pixels_used':False,'physical_reflectance_measured':False};(O/'material-buffer-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
