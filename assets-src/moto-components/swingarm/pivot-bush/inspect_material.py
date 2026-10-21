"""Actual embedded PNG channels, material roles and source portability."""
import json,struct,io,hashlib,numpy as np
from pathlib import Path
from PIL import Image
H=Path(__file__).resolve().parent;O=H.parents[3]/'creative/reviews/swingarm-pivot-bush-v1';d=(H/'swingarm-pivot-bush-inspection.glb').read_bytes();n,_=struct.unpack_from('<II',d,12);g=json.loads(d[20:20+n]);bin=d[28+n:];assert len(g['materials'])==3;rows=[];byrole={}
for mat in g['materials']:
 name=mat['name'];slug='outer-clear'if'Outer clear envelope'in name else'inner-clear'if'Inner pierced clear sleeve'in name else'dark-annulus'if'Dark annulus'in name else None;assert slug;expected=0 if slug=='dark-annulus' else 255;images=[];assert abs(mat['normalTexture']['scale']-(.08 if slug=='inner-clear'else .25))<1e-6
 for role,index in [('normal',mat['normalTexture']['index']),('metallic-roughness',mat['pbrMetallicRoughness']['metallicRoughnessTexture']['index'])]:
  image=g['images'][g['textures'][index]['source']];view=g['bufferViews'][image['bufferView']];raw=bin[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']];a=np.array(Image.open(io.BytesIO(raw)).convert('RGB'));p=H/'textures'/('pivot-bush-'+slug+'-'+role+'.png');author=np.array(Image.open(p).convert('RGB'));assert a.shape==(512,512,3)and np.array_equal(a,author)
  if role=='metallic-roughness':assert np.all(a[:,:,0]==255)and np.all(a[:,:,2]==expected)
  else:assert a[:,:,0].std()>0 and a[:,:,1].std()>0 and a[:,:,2].mean()>250
  images.append({'role':role,'embedded_sha256':hashlib.sha256(raw).hexdigest(),'pixels_identical_to_author_PNG':True,'channel_min':a.min((0,1)).tolist(),'channel_max':a.max((0,1)).tolist()})
 rows.append({'material':name,'role':slug,'baseColor_linear':mat['pbrMetallicRoughness']['baseColorFactor'],'normal_strength':mat['normalTexture']['scale'],'images':images})
for tex in g['textures']:
 sampler=g.get('samplers',[{}])[tex.get('sampler',0)]if g.get('samplers')else{};assert sampler.get('wrapS',10497)==sampler.get('wrapT',10497)==10497
r={'export_sha256':hashlib.sha256(d).hexdigest(),'actual_materials':rows,'normal_mapped_material_count':3,'embedded_images':6,'source_PNG_pixels_preserved':True,'normal_maps_noncolor_ORM_roles_checked':True,'photo_pixels_used':False,'material_reflectance_or_chemistry_measured':False,'art_accepted':False};(O/'material-buffer-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
