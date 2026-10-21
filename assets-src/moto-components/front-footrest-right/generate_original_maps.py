"""Original seeded representative coating fields, no photograph sampling or measured roughness."""
from pathlib import Path
import numpy as np,json,hashlib
from scipy.ndimage import gaussian_filter
from PIL import Image
H=Path(__file__).resolve().parent;P=json.loads((H/'parameters.json').read_text());G=P['material_original'];T=H/'textures';T.mkdir(exist_ok=True);N=G['texture_size_px'][0];rng=np.random.default_rng(113001)
def field(sigma):
 x=gaussian_filter(rng.standard_normal((N,N)).astype(np.float32),sigma,mode='wrap');return x/max(float(x.std()),1e-8)
fine=field(1.4);broad=field(5.0);signal=np.clip(.65*fine+.35*broad,-3,3)/3
base=np.array(G['linear_base_color'],dtype=np.float32)[None,None,:]*(1+.08*signal[:,:,None]);srgb=np.where(base<=.0031308,12.92*base,1.055*np.power(base,1/2.4)-.055);color=np.uint8(np.clip(np.rint(srgb*255),0,255))
rough=.33+.05*signal;roughness=np.uint8(np.clip(np.rint(rough[:,:,None].repeat(3,2)*255),0,255))
height=fine*G['microheight_working_std_m'];pixel=G['UV_tile_physical_extent_m']/N;dx=(np.roll(height,-1,1)-np.roll(height,1,1))/(2*pixel);dy=(np.roll(height,-1,0)-np.roll(height,1,0))/(2*pixel);normal=np.stack([-dx,dy,np.ones_like(dx)],2);normal/=np.linalg.norm(normal,axis=2,keepdims=True);normal_pixels=np.uint8(np.clip(np.rint((normal*.5+.5)*255),0,255))
rows=[]
for role,a in [('basecolor',color),('roughness',roughness),('normal',normal_pixels)]:
 p=T/('footrest-rh-original-'+role+'-v1.png');Image.fromarray(a,'RGB').save(p);rows.append({'role':role,'path':str(p.relative_to(H)),'size_px':[N,N],'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'min_u8':a.reshape(-1,3).min(0).tolist(),'max_u8':a.reshape(-1,3).max(0).tolist(),'colorspace':'sRGB'if role=='basecolor'else'Non-Color'})
x={'generator':'Seed113001 wrap Gaussian original fields, no photo pixels','parameters':G,'images':rows,'height_std_m_working':float(height.std()),'field_grain_is_estimated':True,'maps_not_measured':True,'normal_opengl_Y':True,'metallic_factor':0,'chemical_coating_identity_confirmed':False,'art_accepted':False};(H/'original-map-generation.json').write_text(json.dumps(x,indent=2)+'\n');print(json.dumps(x))
