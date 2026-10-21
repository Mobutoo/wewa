"""Read-only native intensity regions, no photo edit or physical measurement."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
from scipy.ndimage import label,find_objects
H=Path(__file__).resolve().parent;R=H.parents[2];D=R/'creative/research/seat-base';photo=Path('/workspace/wewa-assets/references/body-powertrain-18/seat-crosland-00.jpg');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(photo)=='cbf73ddab044bcf0c5ef1bbd23230ef9ab63fa281243bf4076c3c08e7b01fbbf';im=np.array(Image.open(photo).convert('RGB'));assert im.shape==(1734,1300,3);rows=[]
for threshold in [170,190,210]:
 mask=(im[:,:,0]>threshold)&(im[:,:,1]>threshold)&(im[:,:,2]>threshold*.8);mask[:280]=False;mask[1200:]=False;mask[:,:420]=False;mask[:,800:]=False;lab,n=label(mask);regions=[]
 for i,s in enumerate(find_objects(lab),1):
  if not s:continue
  y,x=np.where(lab[s]==i)
  if len(x)>150:regions.append({'pixels':len(x),'bbox_px':[s[1].start,s[0].start,s[1].stop-1,s[0].stop-1],'intensity_centroid_px':[float(x.mean()+s[1].start),float(y.mean()+s[0].start)]})
 assert len(regions)==6;rows.append({'threshold_R_G':threshold,'threshold_B':threshold*.8,'regions':regions})
report={'schema':1,'tool_sha256':sha(Path(__file__)),'private_photo_path':str(photo),'photo_sha256':sha(photo),'raster_px':[1300,1734],'coordinate_origin':'Native top-left, no crop/scale transform','ROI_xy':[420,280,799,1199],'intensity_region_passes':rows,'interpretation':'Three pairs of bright circular/elliptical regions within dark base fields confirmed by actual native photograph. Consistent with openings through plastic exposing light material, not proof of a hole through full seat or measured 3D circle.','manual_boundary_reading_plusminus_px':10,'manual_bound_is':'Conservative image interpretation only; stable intensity centroids do not create2px physical center accuracy, camera pose or metric depth','physical_circle_or_ellipse':None,'current_RDC_part_identity':False,'pixels_public':False,'used_as_texture':False,'art_accepted':False};(D/'six-light-regions-native-reading-v1.json').write_text(json.dumps(report,indent=2)+'\n');print('Native six bright regions read, no physical dimensions')
