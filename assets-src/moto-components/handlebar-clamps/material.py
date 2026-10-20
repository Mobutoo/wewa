"""Original periodic cast-coating micrograin; source dimensions not measured."""
import bpy,numpy as np,math,json,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/handlebar-clamps-v1';TEX=HERE/'textures';TEX.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(HERE/'handlebar-clamps-v1.blend'));objects=list(bpy.data.collections['WEWA_HANDLEBAR_CLAMPS_SEPARATE_PARTS'].objects)
def geom(o):return hashlib.sha256(np.array([v.co[:] for v in o.data.vertices],dtype=np.float32).tobytes()+str([tuple(p.vertices) for p in o.data.polygons]).encode()+str(list(o.matrix_world)).encode()).hexdigest()
baseline_source_sha256=hashlib.sha256((HERE/'handlebar-clamps-v1.blend').read_bytes()).hexdigest();before={o.name:geom(o) for o in objects};N=1024;tile=.020;seed=361801;rg=np.random.default_rng(seed);f=np.fft.fftfreq(N,d=tile/N);fx,fy=np.meshgrid(f,f)
def noise(length):
 a=np.fft.ifft2(np.fft.fft2(rg.normal(size=(N,N)))*np.exp(-2*math.pi**2*(length/3)**2*(fx*fx+fy*fy))).real;return (a-a.mean())/a.std()
fine=noise(.00022);broad=noise(.00065);height=.000008*fine+.000003*broad;dx=(np.roll(height,-1,1)-np.roll(height,1,1))/(2*tile/N);dy=(np.roll(height,-1,0)-np.roll(height,1,0))/(2*tile/N);normal=np.stack([-dx,-dy,np.ones_like(dx)],-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);rough=np.clip(.425+.027*fine+.018*broad,.31,.55)
mat=bpy.data.materials['Clamp silver cast coating - estimated'];nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links;p=nodes.new('ShaderNodeBsdfPrincipled');p.inputs['Base Color'].default_value=(.18,.20,.22,1);p.inputs['Metallic'].default_value=.65;p.inputs['Roughness'].default_value=.425;out=nodes.new('ShaderNodeOutputMaterial');links.new(p.outputs['BSDF'],out.inputs['Surface'])
for im in list(bpy.data.images):
 if im.name.startswith('clamp-coating-'):bpy.data.images.remove(im)
def image(name,rgb):
 im=bpy.data.images.new(name,width=N,height=N,alpha=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.concatenate([rgb,np.ones((N,N,1))],axis=-1).astype(np.float32).ravel());im.filepath_raw=str(TEX/(name+'.png'));im.file_format='PNG';im.save();im.pack();return im
nm=image('clamp-coating-normal',(normal+1)/2);orm=image('clamp-coating-metallic-roughness',np.stack([np.ones_like(rough),rough,np.full_like(rough,.65)],-1));t=nodes.new('ShaderNodeTexImage');t.image=nm;n=nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=1;links.new(t.outputs['Color'],n.inputs['Color']);links.new(n.outputs['Normal'],p.inputs['Normal']);t=nodes.new('ShaderNodeTexImage');t.image=orm;c=nodes.new('ShaderNodeSeparateColor');links.new(t.outputs['Color'],c.inputs['Color']);links.new(c.outputs['Green'],p.inputs['Roughness']);links.new(c.outputs['Blue'],p.inputs['Metallic'])
seat=bpy.data.materials.get('Clamp satin tube-contact finish - appearance estimated') or bpy.data.materials.new('Clamp satin tube-contact finish - appearance estimated');seat.use_nodes=True;seat.node_tree.nodes.clear();sn=seat.node_tree.nodes.new('ShaderNodeBsdfPrincipled');sn.inputs['Base Color'].default_value=(.18,.20,.22,1);sn.inputs['Metallic'].default_value=.65;sn.inputs['Roughness'].default_value=.27;so=seat.node_tree.nodes.new('ShaderNodeOutputMaterial');seat.node_tree.links.new(sn.outputs['BSDF'],so.inputs['Surface']);contact_assignments=[]
for o in objects:
 mesh=o.data
 if 'bolt' not in o.name:
  seat_index=next((i for i,m in enumerate(mesh.materials) if m==seat),None)
  if seat_index is None:mesh.materials.append(seat);seat_index=len(mesh.materials)-1
  cast_index=next(i for i,m in enumerate(mesh.materials) if m==mat);count=0
  for face in mesh.polygons:
   if mesh.materials[face.material_index].name.startswith('Clamp zinc-like'):continue
   co=face.center;r=math.hypot(co.y,co.z);inward=(face.normal.y*co.y+face.normal.z*co.z)/max(r,1e-12)
   contact=(.01110<r<.01310 and inward<-.5 and abs(face.normal.x)<.90)
   face.material_index=seat_index if contact else cast_index
   if contact:count+=1
  assert count>0,o.name;contact_assignments.append({'name':o.name,'satin_contact_faces':count,'classification':'Inner cylindrical bore and small recessed seat faces; radius/inward orientation, no position or normal change'})
 mesh=o.data;mesh.update();layer=mesh.uv_layers.get('Physical 20mm box mapping') or mesh.uv_layers.new(name='Physical 20mm box mapping')
 for face in mesh.polygons:
  axis=max(range(3),key=lambda i:abs(face.normal[i]));sign=1 if face.normal[axis]>=0 else -1
  for li in face.loop_indices:
   v=mesh.vertices[mesh.loops[li].vertex_index].co;pair=(sign*v.y,v.z) if axis==0 else (-sign*v.x,v.z) if axis==1 else (sign*v.x,v.y);layer.data[li].uv=(pair[0]/tile,pair[1]/tile)
 assert before[o.name]==geom(o)
 if not any(m.type=='TRIANGULATE' for m in o.modifiers):
  tri=o.modifiers.new('Export tangent-ready triangulation','TRIANGULATE');tri.keep_custom_normals=True
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0];bpy.ops.export_scene.gltf(filepath=str(HERE/'handlebar-clamps-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True)
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'handlebar-clamps-v1.blend'),compress=True)
s=json.loads((OUT/'source-geometry-check.json').read_text());s['geometry_signatures_preserved_by_material_stage']=before;s['source_sha256']=hashlib.sha256((HERE/'handlebar-clamps-v1.blend').read_bytes()).hexdigest();s['export_sha256']=hashlib.sha256((HERE/'handlebar-clamps-inspection.glb').read_bytes()).hexdigest();(OUT/'source-geometry-check.json').write_text(json.dumps(s,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps(s,indent=2)+'\n')
r={'baseline_geometry_source_sha256':baseline_source_sha256,'contact_surface_assignments':contact_assignments,'satin_contact_finish':{'roughness_working_estimate':.27,'metallic_working_estimate':.65,'normal_texture':None,'reflectance_measured':False},'source_sha256':s['source_sha256'],'export_sha256':s['export_sha256'],'original_seeded_periodic_data':True,'seed':seed,'resolution_px':[N,N],'tile_size_m':tile,'height_rms_m_estimated':float(height.std()),'fine_correlation_m_estimated':.00022,'broad_correlation_m_estimated':.00065,'normal_strength':1,'roughness_range':[float(rough.min()),float(rough.max())],'casting_metallic_factor_estimated':.65,'separate_steel_finish':{'constant_metallic':.92,'constant_roughness':.25,'no_cast_grain_normal':True},'geometry_unchanged':True,'UV_method':'Face dominant box projection in metres; microscopic boundary seams require review','chemical_reflectance_measured':False,'photo_pixels_used':False,'art_accepted':False};(OUT/'material-build-report.json').write_text(json.dumps(r,indent=2)+'\n');print('WEWA_CLAMPS_MATERIAL',json.dumps(r))
