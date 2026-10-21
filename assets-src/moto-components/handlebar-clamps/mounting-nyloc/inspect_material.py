"""Read actual embedded image pixels and material assignments, no GLB mutation."""
import json,struct,io,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/handlebar-mount-nyloc-v1';data=(HERE/'handlebar-mount-nyloc-inspection.glb').read_bytes();jlen,jtype=struct.unpack_from('<II',data,12);d=json.loads(data[20:20+jlen]);binary=data[20+jlen+8:];rows=[]
for name,prefix,strength,metallic in [('Silver locknut exterior - alloy and coating unmeasured','nyloc-original-metal',.55,.93),('Blue nonmetal insert - genericfamily appearance estimate','nyloc-original-polymer',.45,0)]:
 m=next(x for x in d['materials']if x['name']==name);assert abs(m['normalTexture']['scale']-strength)<1e-5
 for role,index,file in [('normal',m['normalTexture']['index'],prefix+'-normal.png'),('metallic-roughness',m['pbrMetallicRoughness']['metallicRoughnessTexture']['index'],prefix+'-metallic-roughness.png')]:
  im=d['images'][d['textures'][index]['source']];v=d['bufferViews'][im['bufferView']];raw=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];exported=np.array(Image.open(io.BytesIO(raw)).convert('RGB'));original=np.array(Image.open(HERE/'textures'/file).convert('RGB'));assert np.array_equal(exported,original);std=exported.reshape(-1,3).std(0)
  if role=='normal':assert std[0]>1 and std[1]>1 and exported[:,:,2].mean()>250
  else:assert std[1]>1 and std[2]<.01 and abs(exported[:,:,2].mean()/255-metallic)<.005
  rows.append({'material':name,'role':role,'embedded_sha256':hashlib.sha256(raw).hexdigest(),'shape_px':list(exported.shape),'channel_std':std.tolist(),'pixels_identical_to_authored_PNG':True})
bare=next(x for x in d['materials']if x['name']=='Locknut thread and bearing - smoother estimate');assert'normalTexture'not in bare and abs(bare['pbrMetallicRoughness']['roughnessFactor']-.24)<1e-5
assignments=[{'mesh':m['name'],'primitives':[{'material':d['materials'][p['material']]['name'],'index_accessor_count':d['accessors'][p['indices']]['count']}for p in m['primitives']]}for m in d['meshes']];assert len(assignments)==2 and sum(len(m['primitives'])for m in assignments)==3
r={'export_sha256':hashlib.sha256(data).hexdigest(),'actual_embedded_images':rows,'actual_material_assignments':assignments,'smoother_thread_and_bearing_normal_texture':False,'photo_pixels_used':False,'chemical_reflectance_measured':False,'current_RDC_identity_verified':False}
(OUT/'material-buffer-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
