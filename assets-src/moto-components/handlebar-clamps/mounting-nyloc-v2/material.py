"""Original estimated metal and polymer maps; no photo pixels or geometry edits."""
import bpy,numpy as np,math,json,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/handlebar-mount-nyloc-v2';TEX=HERE/'textures';TEX.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(HERE/'handlebar-mount-nyloc-v2.blend'));objects=list(bpy.data.collections['WEWA_HANDLEBAR_MOUNT_NYLOC_ISOLATED'].objects);metal=next(o for o in objects if o.name.startswith('Locknut metal'));insert=next(o for o in objects if o!=metal)
def geom(o):
 return hashlib.sha256(np.array([v.co[:]for v in o.data.vertices],dtype=np.float32).tobytes()+str([(tuple(p.vertices),p.use_smooth)for p in o.data.polygons]).encode()).hexdigest()
before={o.name:geom(o)for o in objects};N=512;tile=.006;seed=39042215;rng=np.random.default_rng(seed);f=np.fft.fftfreq(N,d=tile/N);fx,fy=np.meshgrid(f,f);reports=[]
def noise(correlation):
 a=np.fft.ifft2(np.fft.fft2(rng.normal(size=(N,N)))*np.exp(-2*math.pi**2*(correlation/3)**2*(fx*fx+fy*fy))).real
 return (a-a.mean())/a.std()
def image(name,rgb):
 old=bpy.data.images.get(name)
 if old:bpy.data.images.remove(old)
 im=bpy.data.images.new(name,width=N,height=N,alpha=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.concatenate([rgb,np.ones((N,N,1))],-1).astype(np.float32).ravel());im.filepath_raw=str(TEX/(name+'.png'));im.file_format='PNG';im.save();im.pack();return im
def textured(name,prefix,color,metallic,roughness,heightRMS,correlation,strength):
 fine=noise(correlation);broad=noise(correlation*5);height=heightRMS*(.95*fine+.2*broad);dx=(np.roll(height,-1,1)-np.roll(height,1,1))/(2*tile/N);dy=(np.roll(height,-1,0)-np.roll(height,1,0))/(2*tile/N);normal=np.stack([-dx,-dy,np.ones_like(dx)],-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);rough=np.clip(roughness+.015*fine+.009*broad,roughness-.08,roughness+.08)
 nm=image(prefix+'-normal',(normal+1)/2);orm=image(prefix+'-metallic-roughness',np.stack([np.ones_like(rough),rough,np.full_like(rough,metallic)],-1))
 m=bpy.data.materials.get(name)or bpy.data.materials.new(name);m.use_nodes=True;m.node_tree.nodes.clear();nodes=m.node_tree.nodes;links=m.node_tree.links;p=nodes.new('ShaderNodeBsdfPrincipled');p.inputs['Base Color'].default_value=(*color,1);out=nodes.new('ShaderNodeOutputMaterial');links.new(p.outputs['BSDF'],out.inputs['Surface']);t=nodes.new('ShaderNodeTexImage');t.image=nm;n=nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=strength;links.new(t.outputs['Color'],n.inputs['Color']);links.new(n.outputs['Normal'],p.inputs['Normal']);t=nodes.new('ShaderNodeTexImage');t.image=orm;c=nodes.new('ShaderNodeSeparateColor');links.new(t.outputs['Color'],c.inputs['Color']);links.new(c.outputs['Green'],p.inputs['Roughness']);links.new(c.outputs['Blue'],p.inputs['Metallic'])
 reports.append({'material':name,'prefix':prefix,'reference_tile_m':tile,'height_rms_m_estimated':float(height.std()),'fine_correlation_m_estimated':correlation,'roughness_range_estimated':[float(rough.min()),float(rough.max())],'normal_strength':strength,'metallic_estimated':metallic,'color_linear_estimated':list(color)});return m
surface=textured('Silver locknut exterior - alloy and coating unmeasured','nyloc-original-metal',(.55,.58,.62),.93,.29,.0000013,.00011,.55)
polymer=textured('Blue nonmetal insert - genericfamily appearance estimate','nyloc-original-polymer',(.015,.024,.16),0,.34,.00000045,.00009,.45)
bare=bpy.data.materials.get('Locknut thread and bearing - smoother estimate')or bpy.data.materials.new('Locknut thread and bearing - smoother estimate');bare.use_nodes=True;p=bare.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.55,.58,.62,1);p.inputs['Metallic'].default_value=.93;p.inputs['Roughness'].default_value=.24
metal.data.materials.clear();metal.data.materials.append(surface);metal.data.materials.append(bare);insert.data.materials.clear();insert.data.materials.append(polymer);count=0
for face in metal.data.polygons:
 q=face.center;r=math.hypot(q.x,q.y);face.material_index=1 if(r<.00545 and q.z<.0070)or(q.z<.00001 and face.normal.z<-.9)else 0
 if face.material_index==1:count+=1
assert all(before[o.name]==geom(o)for o in objects)
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=metal
bpy.ops.export_scene.gltf(filepath=str(HERE/'handlebar-mount-nyloc-v2-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True)
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'handlebar-mount-nyloc-v2.blend'),compress=True)
s=json.loads((OUT/'source-geometry-check.json').read_text());s['geometry_and_shading_flags_preserved_by_material_stage']=before;s['source_sha256']=hashlib.sha256((HERE/'handlebar-mount-nyloc-v2.blend').read_bytes()).hexdigest();s['export_sha256']=hashlib.sha256((HERE/'handlebar-mount-nyloc-v2-inspection.glb').read_bytes()).hexdigest();(OUT/'source-geometry-check.json').write_text(json.dumps(s,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps(s,indent=2)+'\n')
r={'source_sha256':s['source_sha256'],'export_sha256':s['export_sha256'],'original_seeded_periodic_data':True,'seed':seed,'resolution_px':[N,N],'materials':reports,'smoother_thread_and_bearing_faces':count,'UV_note':'Source6mm arc reference and10 integer circumferential repeats preserved; effective circumferentialperiod varies with radius, exterior~4.96–6.15mm,polymer~2.95–4.18mm. Not a calibrated isotropic microgeometry measurement.','geometry_and_shading_flags_unchanged':True,'current_RDC_coating_or_insert_color_verified':False,'photo_pixels_used':False,'art_accepted':False};(OUT/'material-build-report.json').write_text(json.dumps(r,indent=2)+'\n');print('WEWA_NYLOC_MATERIAL',json.dumps(r))
