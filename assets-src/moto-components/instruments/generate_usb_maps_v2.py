"""Reuse our authored project normal map; derive original USB roughness maps.
No documentary pixels, captured lighting, external texture or BRDF measurement.
"""
from pathlib import Path
import numpy as np,json,hashlib,shutil
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[2];source=H.parent/'mirrors/textures-left';O=H/'textures-v2/usb';O.mkdir(parents=True,exist_ok=True)
normal=source/'polymer-normal.png';mr=source/'polymer-metallic-roughness.png';a=np.asarray(Image.open(mr).convert('RGB'),dtype=float);g=a[:,:,1];field=np.clip((g-g.mean())/g.std(),-2.5,2.5)
shutil.copy2(normal,O/'original-polymer-normal.png');rows=[]
for name,centre,sigma in [('surround',108,5),('capsule',166,4)]:
 image=np.zeros(a.shape,dtype=np.uint8);image[:,:,0]=255;image[:,:,1]=np.round(np.clip(centre+sigma*field,0,255)).astype(np.uint8);path=O/(name+'-metallic-roughness.png');Image.fromarray(image).save(path);rows.append({'file':str(path.relative_to(R)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'roughness_G_range_uint8':[int(image[:,:,1].min()),int(image[:,:,1].max())],'metallic_B_range_uint8':[0,0]})
report={'authorship':'Original project procedural normal map reused from mirror polymer; original roughness remapping for two working USB surfaces','source_normal_path':str(normal.relative_to(R)),'source_normal_sha256':hashlib.sha256(normal.read_bytes()).hexdigest(),'source_MR_path':str(mr.relative_to(R)),'source_MR_sha256':hashlib.sha256(mr.read_bytes()).hexdigest(),'normal_bytes_reused_identically':True,'normal_tile_working_m':.010,'original_normal_height_RMS_estimated_m':.000002,'not_measured_USB_BRDF':True,'USB_material_split_not_certified':True,'roughness_maps':rows,'photographic_pixels_used':False,'art_accepted':False};(O/'authorship.json').write_text(json.dumps(report,indent=2)+'\n')
