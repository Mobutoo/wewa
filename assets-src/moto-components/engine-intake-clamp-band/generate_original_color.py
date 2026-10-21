"""Rasterize an original restrained 3D color hypothesis into the unique authored UV atlas."""
from pathlib import Path
import numpy as np,json,hashlib
from PIL import Image
from scipy.ndimage import distance_transform_edt
H=Path(__file__).resolve().parent;P=json.loads((H/'material-parameters.json').read_text());B=json.loads((H/'uniform-gold-report.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert not(H/'preflight-manifest.json').exists();inp=H/B['bake_input_npz'];assert sha(inp)==B['bake_input_sha256'];d=np.load(inp);pos=d['positions'];faces=d['triangles'];uvs=d['triangle_uv'];F=P['original_color_field'];N=F['resolution'];xyz=np.zeros((N,N,3),dtype=np.float64);valid=np.zeros((N,N),dtype=bool);no_pixel=0;overlap_count=0;overlap_error=0.
for face,uv in zip(faces,uvs):
 p=uv*N-.5;lo=np.maximum(0,np.ceil(p.min(axis=0)-1e-9).astype(int));hi=np.minimum(N-1,np.floor(p.max(axis=0)+1e-9).astype(int))
 if np.any(hi<lo):no_pixel+=1;continue
 xx,yy=np.meshgrid(np.arange(lo[0],hi[0]+1),np.arange(lo[1],hi[1]+1));a,b,c=p;det=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);assert det!=0
 w1=((xx-a[0])*(c[1]-a[1])-(yy-a[1])*(c[0]-a[0]))/det;w2=((b[0]-a[0])*(yy-a[1])-(b[1]-a[1])*(xx-a[0]))/det;inside=(w1>=-1e-10)&(w2>=-1e-10)&(w1+w2<=1+1e-10)
 if not inside.any():no_pixel+=1;continue
 x=xx[inside];y=N-1-yy[inside];q=(1-w1[inside]-w2[inside])[:,None]*pos[face[0]]+w1[inside,None]*pos[face[1]]+w2[inside,None]*pos[face[2]];old=valid[y,x]
 if old.any():overlap_count+=int(old.sum());overlap_error=max(overlap_error,float(np.linalg.norm(xyz[y[old],x[old]]-q[old],axis=1).max()))
 xyz[y,x]=q;valid[y,x]=True
assert valid.sum()>N*N*.10 and overlap_error<1e-7,(int(valid.sum()),overlap_error)
rng=np.random.default_rng(F['seed']);directions=rng.normal(size=(12,3));directions/=np.linalg.norm(directions,axis=1)[:,None];wavelengths=rng.uniform(*F['world_wavelength_range_m'],12);phases=rng.uniform(0,2*np.pi,12);points=xyz[valid];signal=np.zeros(len(points))
for direction,wavelength,phase in zip(directions,wavelengths,phases):signal+=np.sin(points@direction*(2*np.pi/wavelength)+phase)
signal=np.tanh(signal/(2*np.sqrt(12)));linear=np.array(P['linear_basecolor'])[None,:]+signal[:,None]*np.array(F['linear_RGB_modulation'])[None,:];assert linear.min()>0 and linear.max()<1
srgb=np.where(linear<=.0031308,12.92*linear,1.055*linear**(1/2.4)-.055);rgb=np.zeros((N,N,3),dtype=np.uint8);rgb[valid]=np.round(srgb*255).astype(np.uint8);distance,nearest=distance_transform_edt(~valid,return_indices=True);rgb[~valid]=rgb[nearest[0][~valid],nearest[1][~valid]];out=H/'textures/original-yellow-green-static-color.png';out.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(rgb,'RGB').save(out)
r={'source_geometry_sha256':B['geometry_source_sha256'],'uniform_source_sha256':B['source_sha256'],'uniform_export_sha256':B['export_sha256'],'bake_input_sha256':sha(inp),'image':{'role':'basecolor','path':str(out.relative_to(H)),'sha256':sha(out),'width':N,'height':N,'colorspace':'sRGB','channels':'RGB8'},'seed':F['seed'],'actual_valid_surface_pixels':int(valid.sum()),'used_triangles':len(faces),'triangles_without_pixel_centre_at_this_resolution':no_pixel,'UV_pixel_overlap_count':overlap_count,'max_overlap_world_position_disagreement_m':overlap_error,'padding':'Nearest valid authored color across unused atlas, no photograph or black edge padding','original_3D_basis':{'directions':directions.tolist(),'wavelengths_m':wavelengths.tolist(),'phases':phases.tolist()},'static_linear_RGB_range':[linear.min(axis=0).tolist(),linear.max(axis=0).tolist()],'authored_mean_texel_m':B['authored_mean_atlas_texel_m'],'scope':'Original static visible yellow/green color field, continuity in authored3D before atlas rasterization. Working wavelengths3..9mm from estimated source geometry, not measured treatment or angular interference. Roughness stays constant, no photographic grain/normalmap/shadow baked. Microtriangles not separately resolved at1024 remain a texture-resolution limit, not a mesh or UV collapse.','art_accepted':False};(H/'original-color-generation.json').write_text(json.dumps(r,indent=2)+'\n');print('ORIGINAL_CLAMP_COLOR',json.dumps(r),flush=True)
