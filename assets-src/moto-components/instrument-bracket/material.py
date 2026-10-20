"""Original periodic coating data, explicitly estimated. Geometry preserved."""
import bpy,numpy as np,math,json,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/instrument-bracket-v1';TEX=HERE/'textures';TEX.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(HERE/'instrument-bracket-v1.blend'));body=bpy.data.collections['WEWA_INSTRUMENT_BRACKET_ISOLATED'].objects[0]
def geom(mesh):return hashlib.sha256(np.array([v.co[:] for v in mesh.vertices],dtype=np.float32).tobytes()+str([tuple(p.vertices) for p in mesh.polygons]).encode()).hexdigest()
before=geom(body.data);N=512;tile=.010;seed=402404;rg=np.random.default_rng(seed);f=np.fft.fftfreq(N,d=tile/N);fx,fy=np.meshgrid(f,f)
def noise(length):
 a=np.fft.ifft2(np.fft.fft2(rg.normal(size=(N,N)))*np.exp(-2*math.pi**2*(length/3)**2*(fx*fx+fy*fy))).real;return (a-a.mean())/a.std()
fine=noise(.00025);broad=noise(.0007);height=.000005*fine+.000002*broad;dx=(np.roll(height,-1,1)-np.roll(height,1,1))/(2*tile/N);dy=(np.roll(height,-1,0)-np.roll(height,1,0))/(2*tile/N);normal=np.stack([-dx,-dy,np.ones_like(dx)],-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);rough=np.clip(.38+.020*fine+.012*broad,.29,.49)
def image(name,rgb):
 im=bpy.data.images.new(name,width=N,height=N,alpha=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.concatenate([rgb,np.ones((N,N,1))],axis=-1).astype(np.float32).ravel());im.filepath_raw=str(TEX/(name+'.png'));im.file_format='PNG';im.save();im.pack();return im
mat=bpy.data.materials['Black protective coating - appearance only'];mat.node_tree.nodes.clear();p=mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled');p.inputs['Base Color'].default_value=(.015,.020,.026,1);out=mat.node_tree.nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(p.outputs['BSDF'],out.inputs['Surface'])
for im in list(bpy.data.images):
 if im.name.startswith('bracket-coating-'):bpy.data.images.remove(im)
nm=image('bracket-coating-normal',(normal+1)/2);orm=image('bracket-coating-metallic-roughness',np.stack([np.ones_like(rough),rough,np.full_like(rough,.25)],-1));mat=bpy.data.materials['Black protective coating - appearance only'];nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=nodes.get('Principled BSDF');t=nodes.new('ShaderNodeTexImage');t.image=nm;n=nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.7;links.new(t.outputs['Color'],n.inputs['Color']);links.new(n.outputs['Normal'],p.inputs['Normal']);t=nodes.new('ShaderNodeTexImage');t.image=orm;c=nodes.new('ShaderNodeSeparateColor');links.new(t.outputs['Color'],c.inputs['Color']);links.new(c.outputs['Green'],p.inputs['Roughness']);links.new(c.outputs['Blue'],p.inputs['Metallic'])
mesh=body.data;mesh.update();layer=mesh.uv_layers.get('Physical 10mm box mapping') or mesh.uv_layers.new(name='Physical 10mm box mapping')
for face in mesh.polygons:
 axis=max(range(3),key=lambda i:abs(face.normal[i]));sign=1 if face.normal[axis]>=0 else -1
 for li in face.loop_indices:
  v=mesh.vertices[mesh.loops[li].vertex_index].co;pair=(sign*v.y,v.z) if axis==0 else (-sign*v.x,v.z) if axis==1 else (sign*v.x,v.y);layer.data[li].uv=(pair[0]/tile,pair[1]/tile)
assert before==geom(mesh)
if not any(m.type=='TRIANGULATE' for m in body.modifiers):
 tri=body.modifiers.new('Export tangent-ready triangulation','TRIANGULATE');tri.keep_custom_normals=True
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body;bpy.ops.export_scene.gltf(filepath=str(HERE/'instrument-bracket-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True)
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'instrument-bracket-v1.blend'),compress=True)
s=json.loads((OUT/'source-geometry-check.json').read_text());s['geometry_sha256_preserved_by_material_stage']=before;s['source_sha256']=hashlib.sha256((HERE/'instrument-bracket-v1.blend').read_bytes()).hexdigest();s['export_sha256']=hashlib.sha256((HERE/'instrument-bracket-inspection.glb').read_bytes()).hexdigest();(OUT/'source-geometry-check.json').write_text(json.dumps(s,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps(s,indent=2)+'\n')
r={'source_sha256':s['source_sha256'],'export_sha256':s['export_sha256'],'original_seeded_periodic_data':True,'seed':seed,'resolution_px':[N,N],'tile_size_m':tile,'height_rms_m_estimated':float(height.std()),'fine_correlation_m_estimated':.00025,'normal_strength':.7,'roughness_range':[float(rough.min()),float(rough.max())],'geometry_unchanged':True,'UV_method':'Face dominant box projection in metres; microscopic boundary seams require review','chemical_reflectance_measured':False,'photo_pixels_used':False,'art_accepted':False};(OUT/'material-build-report.json').write_text(json.dumps(r,indent=2)+'\n');print('WEWA_BRACKET_MATERIAL',json.dumps(r))
