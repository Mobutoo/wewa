"""Read actual GLB images/channels/assignments; no source or buffer edits."""
import json,struct,hashlib,io
from pathlib import Path
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/frame-front-downmember-v1';data=(HERE/'frame-front-downmember-inspection.glb').read_bytes();jlen,_=struct.unpack_from('<II',data,12);d=json.loads(data[20:20+jlen]);binary=data[20+jlen+8:];m=next(m for m in d['materials']if m['name']=='Black downmember coating - composition unmeasured');assert abs(m['normalTexture']['scale']-.45)<1e-5;rows=[]
for role,index,file in [('normal',m['normalTexture']['index'],'downmember-original-coat-normal.png'),('metallic-roughness',m['pbrMetallicRoughness']['metallicRoughnessTexture']['index'],'downmember-original-coat-metallic-roughness.png')]:
 im=d['images'][d['textures'][index]['source']];v=d['bufferViews'][im['bufferView']];raw=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];actual=np.array(Image.open(io.BytesIO(raw)).convert('RGB'));source=np.array(Image.open(HERE/'textures'/file).convert('RGB'));assert actual.shape==(512,512,3)and np.array_equal(actual,source);std=actual.reshape(-1,3).std(0)
 if role=='normal':assert std[0]>1 and std[1]>1 and actual[:,:,2].mean()>250
 else:assert std[1]>1 and std[2]<.01 and abs(actual[:,:,2].mean()/255-0)<.005
 rows.append({'role':role,'embedded_sha256':hashlib.sha256(raw).hexdigest(),'shape_px':list(actual.shape),'channel_std':std.tolist(),'pixels_identical_to_authored_PNG':True})
bare=next(m for m in d['materials']if m['name']=='Unseen inner wall and short passages - finish estimated');assert'normalTexture'not in bare and abs(bare['pbrMetallicRoughness']['roughnessFactor']-.32)<1e-5;assignments=[{'mesh':m['name'],'primitives':[{'material':d['materials'][p['material']]['name'],'indices':d['accessors'][p['indices']]['count']}for p in m['primitives']]}for m in d['meshes']];assert len(assignments)==1 and len(assignments[0]['primitives'])==2
r={'export_sha256':hashlib.sha256(data).hexdigest(),'actual_embedded_images':rows,'actual_assignments':assignments,'inner_envelope_normal_texture':False,'photo_pixels_used':False,'coating_chemistry_and_RDC_reflectance_measured':False,'art_accepted':False};(OUT/'material-buffer-check.json').write_text(json.dumps(r,indent=2)+'\n');print('WEWA_FRAME_DOWNMEMBER_MATERIAL_BUFFERS',json.dumps(r))
