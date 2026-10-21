"""Original estimated dry black rubber maps; continuous wall/morphs unchanged."""
import bpy,sys,json,math,hashlib,numpy as np
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path.insert(0,str(HERE))
from gltf_morph_tangent_compat import corrected_morph_tangent_export
OUT=ROOT/'creative/reviews/fork-bellows-v1';TEX=HERE/'textures';TEX.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(HERE/'fork-bellows-v1.blend'))
o=bpy.data.collections['WEWA_FORK_BELLOWS_ISOLATED'].objects[0]
def geometry(mesh):
 h=hashlib.sha256()
 for key in mesh.shape_keys.key_blocks:
  data=np.empty(len(key.data)*3,dtype=np.float32);key.data.foreach_get('co',data);h.update(data.tobytes())
 for p in mesh.polygons:h.update(np.array(p.vertices,dtype=np.int32).tobytes())
 return h.hexdigest()
before=geometry(o.data);N=512;tile=.010;seed=125110140;rg=np.random.default_rng(seed)
f=np.fft.fftfreq(N,d=tile/N);fx,fy=np.meshgrid(f,f)
def noise(length):
 a=np.fft.ifft2(np.fft.fft2(rg.normal(size=(N,N)))*np.exp(-2*math.pi**2*(length/3)**2*(fx*fx+fy*fy))).real
 return (a-a.mean())/a.std()
fine=noise(.00012);broad=noise(.0008);height=.0000012*fine+.0000004*broad
dx=(np.roll(height,-1,1)-np.roll(height,1,1))/(2*tile/N);dy=(np.roll(height,-1,0)-np.roll(height,1,0))/(2*tile/N)
normal=np.stack([-dx,-dy,np.ones_like(dx)],-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
rough=np.clip(.50+.018*fine+.012*broad,.42,.59)
def image(name,rgb):
 old=bpy.data.images.get(name)
 if old:bpy.data.images.remove(old)
 im=bpy.data.images.new(name,width=N,height=N,alpha=False);im.colorspace_settings.name='Non-Color'
 im.pixels.foreach_set(np.concatenate([rgb,np.ones((N,N,1))],axis=-1).astype(np.float32).ravel())
 im.filepath_raw=str(TEX/(name+'.png'));im.file_format='PNG';im.save();im.pack();return im
nm=image('bellows-original-normal',(normal+1)/2)
orm=image('bellows-original-metallic-roughness',np.stack([np.ones_like(rough),rough,np.zeros_like(rough)],-1))
m=o.data.materials[0];m.name='Dry black fork bellows - compound and reflectance estimated';m.use_nodes=True
m.node_tree.nodes.clear();nodes=m.node_tree.nodes;links=m.node_tree.links
p=nodes.new('ShaderNodeBsdfPrincipled');p.inputs['Base Color'].default_value=(.010,.012,.015,1);p.inputs['Metallic'].default_value=0
out=nodes.new('ShaderNodeOutputMaterial');links.new(p.outputs['BSDF'],out.inputs['Surface'])
t=nodes.new('ShaderNodeTexImage');t.image=nm;n=nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.55
links.new(t.outputs['Color'],n.inputs['Color']);links.new(n.outputs['Normal'],p.inputs['Normal'])
t=nodes.new('ShaderNodeTexImage');t.image=orm;c=nodes.new('ShaderNodeSeparateColor')
links.new(t.outputs['Color'],c.inputs['Color']);links.new(c.outputs['Green'],p.inputs['Roughness']);links.new(c.outputs['Blue'],p.inputs['Metallic'])
for key in o.data.shape_keys.key_blocks:key.value=0
assert before==geometry(o.data)
bpy.context.scene.camera.data.ortho_scale=.18
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
with corrected_morph_tangent_export(OUT/'morph-tangent-compatibility-check.json'):
 bpy.ops.export_scene.gltf(filepath=str(HERE/'fork-bellows-inspection.glb'),export_format='GLB',use_selection=True,export_apply=False,export_texcoords=True,export_normals=True,export_tangents=True,export_morph=True,export_morph_normal=True,export_morph_tangent=True)
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'fork-bellows-v1.blend'),compress=True)
s=json.loads((OUT/'source-geometry-check.json').read_text());s['geometry_and_shape_keys_preserved_by_material_stage']=before
s['source_sha256']=hashlib.sha256((HERE/'fork-bellows-v1.blend').read_bytes()).hexdigest();s['export_sha256']=hashlib.sha256((HERE/'fork-bellows-inspection.glb').read_bytes()).hexdigest()
(OUT/'source-geometry-check.json').write_text(json.dumps(s,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps(s,indent=2)+'\n')
r={'source_sha256':s['source_sha256'],'export_sha256':s['export_sha256'],'seed':seed,'resolution_px':[N,N],
 'original_periodic_data':True,'reference_height_tile_m':tile,'height_rms_m_estimated':float(height.std()),
 'fine_correlation_m_estimated':.00012,'broad_correlation_m_estimated':.0008,'normal_strength':.55,
 'roughness_range_estimated':[float(rough.min()),float(rough.max())],'metallic':0,
 'UV_method':'14 integer repeats circumferentially,10mm base meridian arc; planar open-end annuli10mm',
 'effective_circumferential_tile_m':[2*math.pi*.0158/14,2*math.pi*.026/14],
 'UV_morph_note':'Coordinates fixed to base wall; estimated compression/extension stretches the material; no incompressible strain model',
 'geometry_and_shape_keys_unchanged':True,'chemical_reflectance_measured':False,'photo_pixels_used':False,'art_accepted':False}
(OUT/'material-build-report.json').write_text(json.dumps(r,indent=2)+'\n');print('WEWA_BELLOWS_MATERIAL',json.dumps(r))
