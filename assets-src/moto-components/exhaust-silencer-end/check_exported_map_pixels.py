"""Decode native payloads and sample actual exported UV corners and centers."""
from pathlib import Path
import json,hashlib,numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[3];H=R/'assets-src/moto-components/exhaust-silencer-end';O=R/'creative/reviews/exhaust-silencer-end-v1';D=Path('/workspace/wewa-assets/work-in-progress/exhaust-silencer-end/exported-v1-textures');report=json.loads((O/'material-export-check.json').read_text());P=json.loads((H/'parameters.json').read_text());UV=np.asarray(json.loads((D/'actual_UV_vertices_and_triangle_centres.json').read_text()));assert np.isfinite(UV).all()and((UV>=0)&(UV<=1)).all();rows=[]
for t in report['textures']:
 p=Path(t['extracted_actual_embedded_bytes']);assert hashlib.sha256(p.read_bytes()).hexdigest()==t['sha256'];a=np.asarray(Image.open(p).convert('RGB'),dtype=float)/255.;h,w=a.shape[:2]
 if t['role']=='basecolor':a=np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
 x=np.clip(UV[:,0]*w-.5,0,w-1);y=np.clip(UV[:,1]*h-.5,0,h-1);ix=x.astype(int);iy=y.astype(int);jx=np.minimum(ix+1,w-1);jy=np.minimum(iy+1,h-1);fx=(x-ix)[:,None];fy=(y-iy)[:,None];b=(a[iy,ix]*(1-fx)+a[iy,jx]*fx)*(1-fy)+(a[jy,ix]*(1-fx)+a[jy,jx]*fx)*fy
 if t['role']=='basecolor':
  base=np.asarray(P['material_original']['linear_base_color']);lo,hi=P['material_original']['color_multiplier_range'];assert(b>=base*lo-.0007).all()and(b<=base*hi+.0007).all(),'Color UV samples outside bounded original recipe';assert min(b.std(axis=0))>.00001
 else:
  lo,hi=P['material_original']['roughness_range'];assert b[:,1].min()>lo-.005 and b[:,1].max()<hi+.005;assert b[:,1].std()>.001;assert (b[:,2]*report['native_exported_material']['metallic']).max()==0
 rows.append({**t,'size_px':[w,h],'actual_UV_samples':len(UV),'sampled_min_rgb':b.min(axis=0).tolist(),'sampled_max_rgb':b.max(axis=0).tolist(),'sampled_std_rgb':b.std(axis=0).tolist(),'sampling_space':'Linear RGB decoded per texel before bilinear filtering'if t['role']=='basecolor'else'Linear Non-Color roughness G; metallic B times material factor','sampled_not_exhaustive_filter_proof':True})
r={'source_sha256':report['source_sha256'],'export_sha256':report['export_sha256'],'textures':rows,'native_embedded_payloads_actually_decoded':True,'original_color_roughness_only':True,'no_normalmap_or_relief_claim':True,'art_accepted':False};(O/'actual-embedded-map-pixel-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
