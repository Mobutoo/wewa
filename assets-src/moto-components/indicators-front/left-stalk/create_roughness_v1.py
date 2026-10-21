"""Original periodic roughness only; no documentary pixels or surface-normal claims."""
from pathlib import Path
import numpy as np,json,hashlib
from scipy.ndimage import gaussian_filter
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/indicator-front-left-stalk-v1';O.mkdir(parents=True,exist_ok=True);a=gaussian_filter(np.random.default_rng(0x57455741).normal(size=(1024,1024)),sigma=2,mode='wrap');a=(a-a.mean())/a.std();g=np.rint(np.clip(.62+.015*a,.57,.68)*255).astype(np.uint8);rgb=np.stack([np.full_like(g,255),g,np.zeros_like(g)],axis=-1);p=H/'original-stalk-roughness-v1.png';Image.fromarray(rgb).save(p);q={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size_px':[1024,1024],'seed':0x57455741,'gaussian_sigma_px':2,'wrap':'periodic','actual_quantized_mean_G':float(g.mean()/255),'actual_quantized_RMS_G':float(g.std()/255),'RGB_channels':'R=255/G=original roughness/B=0','private_photo_pixels':False,'actual_physical_grain_or_polymergrade_measured':False};(O/'original-roughness-report.json').write_text(json.dumps(q,indent=2)+'\n');print(q)
