"""Original periodic coating data, explicitly estimated. Geometry preserved."""
import bpy,numpy as np,math,json,hashlib
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/steering-lower-v1';TEX=HERE/'textures';TEX.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(HERE/'steering-lower-v1.blend'));body=bpy.data.collections['WEWA_STEERING_LOWER_BODY_ISOLATED'].objects[0]
def geom(mesh):return hashlib.sha256(np.array([v.co[:] for v in mesh.vertices],dtype=np.float32).tobytes()+str([tuple(p.vertices) for p in mesh.polygons]).encode()).hexdigest()
body.data.materials[0].name='Black coated lower casting - visual estimate';
edge=bpy.data.objects['EDGE'];edge.location=(.18,-.15,-.25);edge.rotation_euler=(Vector((0,.04,0))-edge.location).to_track_quat('-Z','Y').to_euler();edge.data.energy=.8
before=geom(body.data);N=512;tile=.016;seed=181020;rg=np.random.default_rng(seed);f=np.fft.fftfreq(N,d=tile/N);fx,fy=np.meshgrid(f,f)
def noise(length):
 a=np.fft.ifft2(np.fft.fft2(rg.normal(size=(N,N)))*np.exp(-2*math.pi**2*(length/3)**2*(fx*fx+fy*fy))).real;return (a-a.mean())/a.std()
fine=noise(.00025);broad=noise(.001);height=.000005*fine+.000002*broad;dx=(np.roll(height,-1,1)-np.roll(height,1,1))/(2*tile/N);dy=(np.roll(height,-1,0)-np.roll(height,1,0))/(2*tile/N);normal=np.stack([-dx,-dy,np.ones_like(dx)],-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);rough=np.clip(.27+.025*fine+.012*broad,.18,.40)
def image(name,rgb):
 im=bpy.data.images.new(name,width=N,height=N,alpha=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.concatenate([rgb,np.ones((N,N,1))],axis=-1).astype(np.float32).ravel());im.filepath_raw=str(TEX/(name+'.png'));im.file_format='PNG';im.save();im.pack();return im
mat=bpy.data.materials['Black coated lower casting - visual estimate'];mat.node_tree.nodes.clear();p=mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled');p.inputs['Base Color'].default_value=(.015,.020,.026,1);out=mat.node_tree.nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(p.outputs['BSDF'],out.inputs['Surface'])
for im in list(bpy.data.images):
 if im.name.startswith('lower-coating-'):bpy.data.images.remove(im)
nm=image('lower-coating-normal',(normal+1)/2);orm=image('lower-coating-metallic-roughness',np.stack([np.ones_like(rough),rough,np.full_like(rough,.25)],-1));mat=bpy.data.materials['Black coated lower casting - visual estimate'];nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=nodes.get('Principled BSDF');t=nodes.new('ShaderNodeTexImage');t.image=nm;n=nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.7;links.new(t.outputs['Color'],n.inputs['Color']);links.new(n.outputs['Normal'],p.inputs['Normal']);t=nodes.new('ShaderNodeTexImage');t.image=orm;c=nodes.new('ShaderNodeSeparateColor');links.new(t.outputs['Color'],c.inputs['Color']);links.new(c.outputs['Green'],p.inputs['Roughness']);links.new(c.outputs['Blue'],p.inputs['Metallic'])
mesh=body.data;mesh.update();layer=mesh.uv_layers.get('Physical16mm dominant box mapping') or mesh.uv_layers.new(name='Physical16mm dominant box mapping')
for face in mesh.polygons:
 axis=max(range(3),key=lambda i:abs(face.normal[i]));sign=1 if face.normal[axis]>=0 else -1
 for li in face.loop_indices:
  v=mesh.vertices[mesh.loops[li].vertex_index].co;pair=(sign*v.y,v.z) if axis==0 else (-sign*v.x,v.z) if axis==1 else (sign*v.x,v.y);layer.data[li].uv=(pair[0]/tile,pair[1]/tile)

# Photo-visible bore faces are smoother and distinct from the coated casting.
bare=bpy.data.materials.get('Machined bore finish - appearance estimated') or bpy.data.materials.new('Machined bore finish - appearance estimated');bare.use_nodes=True;bp=bare.node_tree.nodes.get('Principled BSDF');bp.inputs['Base Color'].default_value=(.18,.20,.22,1);bp.inputs['Roughness'].default_value=.30;bp.inputs['Metallic'].default_value=.65
if bare.name not in [m.name for m in body.data.materials]:body.data.materials.append(bare)
idx=list(body.data.materials).index(bare);counts=0
for face in mesh.polygons:
 q=face.center;n=face.normal;contact=False
 for cx,cy,r in [(-.0875,0,.01555),(.0875,0,.01555),(0,.045,.0125),(-.023,.002,.0027),(.023,.002,.0027)]:
  dx=q.x-cx;dy=q.y-cy;rr=math.hypot(dx,dy)
  if abs(rr-r)<.00020 and rr>0 and (dx*n.x+dy*n.y)/rr<-.65 and abs(n.z)<.9:contact=True
 for cx in [-.0875,.0875]:
  dy=q.y-.021;dz=q.z;rr=math.hypot(dy,dz)
  if abs(rr-.0052)<.00020 and rr>0 and (dy*n.y+dz*n.z)/rr<-.65 and abs(n.x)<.9:contact=True
 face.material_index=idx if contact else 0
 if contact:counts+=1

assert before==geom(mesh)
if not any(m.type=='TRIANGULATE' for m in body.modifiers):
 tri=body.modifiers.new('Export tangent-ready triangulation','TRIANGULATE');tri.keep_custom_normals=True
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body;bpy.ops.export_scene.gltf(filepath=str(HERE/'steering-lower-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True)
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'steering-lower-v1.blend'),compress=True)
s=json.loads((OUT/'source-geometry-check.json').read_text());s['geometry_sha256_preserved_by_material_stage']=before;s['source_sha256']=hashlib.sha256((HERE/'steering-lower-v1.blend').read_bytes()).hexdigest();s['export_sha256']=hashlib.sha256((HERE/'steering-lower-inspection.glb').read_bytes()).hexdigest();(OUT/'source-geometry-check.json').write_text(json.dumps(s,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps(s,indent=2)+'\n')
r={'source_sha256':s['source_sha256'],'export_sha256':s['export_sha256'],'original_seeded_periodic_data':True,'seed':seed,'resolution_px':[N,N],'tile_size_m':tile,'height_rms_m_estimated':float(height.std()),'fine_correlation_m_estimated':.00025,'normal_strength':.7,'roughness_range':[float(rough.min()),float(rough.max())],'geometry_unchanged':True,'smoother_bore_face_count':counts,'bare_finish_estimated':{'roughness':.30,'metallic':.65,'normal_texture':False},'UV_method':'Face dominant box projection in metres; microscopic boundary seams require review','chemical_reflectance_measured':False,'photo_pixels_used':False,'art_accepted':False};(OUT/'material-build-report.json').write_text(json.dumps(r,indent=2)+'\n');print('WEWA_LOWER_MATERIAL',json.dumps(r))
