"""Original optional silver coating grain, never photographs or baked illumination.
Physical pitch/height are estimated working controls, not measured coating properties.
"""
from pathlib import Path
import bpy,numpy as np,math,hashlib,json

def apply_original_grain(mat,folder,uv_name,tile_m=.006,height_rms_m=.000003):
 folder=Path(folder);folder.mkdir(exist_ok=True,parents=True);n=256;rng=np.random.default_rng(541287);f=np.fft.fftfreq(n);fx,fy=np.meshgrid(f,f)
 def noise(sigma):
  field=np.fft.ifft2(np.fft.fft2(rng.normal(size=(n,n)))*np.exp(-2*math.pi**2*sigma**2*(fx*fx+fy*fy))).real
  return (field-field.mean())/field.std()
 height=noise(3.0)*height_rms_m;pitch=tile_m/n;du=(np.roll(height,-1,axis=1)-np.roll(height,1,axis=1))/(2*pitch);dv=(np.roll(height,-1,axis=0)-np.roll(height,1,axis=0))/(2*pitch)
 vectors=np.stack((-du,-dv,np.ones_like(du)),axis=-1);vectors/=np.linalg.norm(vectors,axis=-1,keepdims=True);normal=vectors*.5+.5
 rough=np.clip(.42+.035*noise(2.5),.34,.50);packed=np.stack((np.ones_like(rough),rough,np.full_like(rough,.20)),axis=-1)
 def image(name,rgb):
  im=bpy.data.images.new(name,width=n,height=n,alpha=False);im.colorspace_settings.name='Non-Color';rgba=np.concatenate((rgb,np.ones((n,n,1))),axis=-1).astype(np.float32);im.pixels.foreach_set(rgba.ravel());im.filepath_raw=str(folder/(name+'.png'));im.file_format='PNG';im.save();im.pack();return im
 normal_im=image('silver-coating-normal',normal);orm_im=image('silver-coating-metallic-roughness',packed)
 nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=nodes.get('Principled BSDF');uv=nodes.new('ShaderNodeUVMap');uv.uv_map=uv_name
 normtex=nodes.new('ShaderNodeTexImage');normtex.image=normal_im;normtex.extension='REPEAT';normtex.interpolation='Linear';links.new(uv.outputs['UV'],normtex.inputs['Vector']);norm=nodes.new('ShaderNodeNormalMap');norm.space='TANGENT';norm.uv_map=uv_name;norm.inputs['Strength'].default_value=1;links.new(normtex.outputs['Color'],norm.inputs['Color']);links.new(norm.outputs['Normal'],p.inputs['Normal'])
 ormtex=nodes.new('ShaderNodeTexImage');ormtex.image=orm_im;ormtex.extension='REPEAT';ormtex.interpolation='Linear';links.new(uv.outputs['UV'],ormtex.inputs['Vector']);sep=nodes.new('ShaderNodeSeparateColor');links.new(ormtex.outputs['Color'],sep.inputs['Color']);links.new(sep.outputs['Green'],p.inputs['Roughness']);links.new(sep.outputs['Blue'],p.inputs['Metallic'])
 report={'origin':'Original seeded periodic Fourier height/noise fields; no photographed pixels','seed':541287,'image_px':[n,n],'tile_projected_working_m':tile_m,'pixel_pitch_working_m':pitch,'source_height_field_RMS_working_m':float(height.std()),'source_height_range_m':[float(height.min()),float(height.max())],'source_analytic_normal_length_max_error':float(np.max(np.abs(np.linalg.norm(vectors,axis=-1)-1))),'normal_map_layout':'RGB Non-Color OpenGL+Y tangent-space; source height is not exported mesh displacement','normal_scale':1,'roughness_range':[float(rough.min()),float(rough.max())],'metallic_channel':.20,'metallic_roughness_layout':'R1 Groughness Bmetallic, Non-Color','uv_policy':'6mm projected charts on dominant face axes, estimated surface stretch, nondegenerate perimeter/bore UVs','grain_pitch_or_height_measured':False,'all_dimensions_estimated':True,'images':[{'file':im.name+'.png','sha256':hashlib.sha256((folder/(im.name+'.png')).read_bytes()).hexdigest()} for im in [normal_im,orm_im]],'material_accepted':False}
 (folder/'grain-generation.json').write_text(json.dumps(report,indent=2)+'\n');return report
