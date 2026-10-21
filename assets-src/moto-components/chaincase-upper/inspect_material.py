"""Actual embedded PNG pixels and glTF material roles, original candidate only."""
import json,struct,io,hashlib,numpy as np
from pathlib import Path
from PIL import Image
H=Path(__file__).resolve().parent;O=H.parents[2]/'creative/reviews/chaincase-upper-v1';d=(H/'chaincase-upper-inspection.glb').read_bytes();n,_=struct.unpack_from('<II',d,12);g=json.loads(d[20:20+n]);buf=d[28+n:];assert len(g['materials'])==1;mat=g['materials'][0];assert not mat.get('doubleSided',False);rows=[];coat=mat['extensions']['KHR_materials_clearcoat'];assert abs(coat['clearcoatFactor']-.12)<1e-6 and abs(coat['clearcoatRoughnessFactor']-.20)<1e-6;assert abs(mat['normalTexture']['scale']-.12)<1e-6
for role,index in [('normal',mat['normalTexture']['index']),('metallic-roughness',mat['pbrMetallicRoughness']['metallicRoughnessTexture']['index'])]:
 im=g['images'][g['textures'][index]['source']];view=g['bufferViews'][im['bufferView']];raw=buf[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']];a=np.array(Image.open(io.BytesIO(raw)).convert('RGB'));p=H/'textures'/('chaincase-upper-original-'+role+'.png');assert a.shape==(512,512,3)and np.array_equal(a,np.array(Image.open(p).convert('RGB')))
 if role=='metallic-roughness':assert np.all(a[:,:,0]==255)and np.all(a[:,:,2]==0)
 else:assert a[:,:,0].std()>0 and a[:,:,1].std()>0 and a[:,:,2].mean()>250
 rows.append({'role':role,'embedded_sha256':hashlib.sha256(raw).hexdigest(),'pixels_identical_to_author_PNG':True,'channel_min':a.min((0,1)).tolist(),'channel_max':a.max((0,1)).tolist()})
for tex in g['textures']:
 sampler=g.get('samplers',[{}])[tex.get('sampler',0)]if g.get('samplers')else{};assert sampler.get('wrapS',10497)==sampler.get('wrapT',10497)==10497
r={'export_sha256':hashlib.sha256(d).hexdigest(),'baseColor_linear':mat['pbrMetallicRoughness']['baseColorFactor'],'normal_strength':mat['normalTexture']['scale'],'actual_clearcoat_extension':coat,'component_complete':False,'actual_images':rows,'normal_mapped_material_count':1,'embedded_images':2,'source_PNG_pixels_preserved':True,'photo_pixels_used':False,'material_grade_or_reflectance_measured':False,'art_accepted':False};(O/'material-buffer-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
