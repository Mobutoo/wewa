"""Read actual embedded maps under actual native UV samples, no export mutation."""
from pathlib import Path
import json,hashlib,numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[3];H=R/'assets-src/moto-components/exhaust-header-gasket';O=R/'creative/reviews/exhaust-header-gasket-v2';D=Path('/workspace/wewa-assets/work-in-progress/exhaust-header-gasket/exported-v2-textures');report=json.loads((O/'material-export-check.json').read_text());P=json.loads((H/'parameters-v2.json').read_text());G=P['material_original'];UV=np.asarray(json.loads((D/'actual_UV_vertices_and_triangle_centres.json').read_text()));assert np.isfinite(UV).all()and((UV>=0)&(UV<=1)).all();rows=[]
for t in report['textures']:
 p=Path(t['extracted_actual_embedded_bytes']);assert hashlib.sha256(p.read_bytes()).hexdigest()==t['sha256'];a=np.asarray(Image.open(p).convert('RGB'),dtype=float)/255.;h,w=a.shape[:2]
 if t['role']=='basecolor':a=np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
 x=np.clip(UV[:,0]*w-.5,0,w-1);y=np.clip(UV[:,1]*h-.5,0,h-1);ix=x.astype(int);iy=y.astype(int);jx=np.minimum(ix+1,w-1);jy=np.minimum(iy+1,h-1);fx=(x-ix)[:,None];fy=(y-iy)[:,None];b=(a[iy,ix]*(1-fx)+a[iy,jx]*fx)*(1-fy)+(a[jy,ix]*(1-fx)+a[jy,jx]*fx)*fy;extra={}
 if t['role']=='basecolor':
  base=np.asarray(G['linear_base_color']);lo,hi=G['color_multiplier_range'];encode=lambda x:np.where(x<=.0031308,12.92*x,1.055*x**(1/2.4)-.055);decode=lambda x:np.where(x<=.04045,x/12.92,((x+.055)/1.055)**2.4);lower=decode(np.floor(encode(base*lo)*255)/255);upper=decode(np.ceil(encode(base*hi)*255)/255);assert(b>=lower-1e-7).all()and(b<=upper+1e-7).all();assert max(b.std(axis=0))>1e-5
 elif t['role']=='metallic_roughness':
  lo,hi=G['roughness_range'];assert b[:,1].min()>lo-.005 and b[:,1].max()<hi+.005;assert b[:,1].std()>.001;assert np.max(np.abs(b[:,2]*report['native_exported_material']['metallic']-G['metallic']))<1e-6
 else:
  vectors=b*2-1;length=np.linalg.norm(vectors,axis=1);assert length.min()>.25 and length.max()<1.1 and b[:,2].min()>.5;assert max(b[:,:2].std(axis=0))>.0001;extra={'filtered_decoded_vector_length_min':float(length.min()),'filtered_decoded_vector_length_max':float(length.max()),'scope':'glTF shader renormalizes filtered normal. Check nonzero finite actual normal signal, no physical height calibration.'}
 rows.append({**t,'size_px':[w,h],'actual_UV_samples':len(UV),'sampled_min_rgb':b.min(axis=0).tolist(),'sampled_max_rgb':b.max(axis=0).tolist(),'sampled_std_rgb':b.std(axis=0).tolist(),**extra})
r={'source_sha256':report['source_sha256'],'export_sha256':report['export_sha256'],'textures':rows,'native_embedded_payloads_actually_decoded':True,'normalmap_real_signal':True,'height_or_optical_scale_measured':False,'photo_pixels_used':False,'art_accepted':False};(O/'actual-embedded-map-pixel-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
