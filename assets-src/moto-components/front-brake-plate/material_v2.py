"""Material-only revision. Original periodic PBR data, not a photographed texture.
Run with Blender --background --threads 4 --python-exit-code 1 --python this-file.
Geometry is evaluated from v1; original construction/modifier object is retained hidden.
"""
import hashlib,json,math
from pathlib import Path
import bpy,numpy as np

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
OUT=ROOT/'creative/reviews/front-brake-plate-v2';OUT.mkdir(exist_ok=True)
TEX=HERE/'textures-v2';TEX.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(HERE/'front-brake-plate-v1.blend'))
N=512;TILE=.010;SEED=20261020
rng=np.random.default_rng(SEED)
freq=np.fft.fftfreq(N,d=TILE/N);fx,fy=np.meshgrid(freq,freq)
def periodic_noise(length):
    spectrum=np.fft.fft2(rng.normal(size=(N,N)))
    field=np.fft.ifft2(spectrum*np.exp(-2*math.pi**2*(length/3)**2*(fx*fx+fy*fy))).real
    return (field-field.mean())/field.std()
# Periodic micro-height, no lighting in albedo; RMS height is a working estimate.
fine=periodic_noise(.00016);broad=periodic_noise(.00065)
height=(.83*fine+.17*broad)*.0000018
dx=(np.roll(height,-1,axis=1)-np.roll(height,1,axis=1))/(2*TILE/N)
dy=(np.roll(height,-1,axis=0)-np.roll(height,1,axis=0))/(2*TILE/N)
normal=np.stack((-dx,-dy,np.ones_like(dx)),axis=-1)
normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
rough=np.clip(.365+.018*fine+.012*broad,.30,.44)
def image(name,rgb):
    im=bpy.data.images.new(name,width=N,height=N,alpha=False,float_buffer=False)
    im.colorspace_settings.name='Non-Color'
    rgba=np.concatenate((rgb,np.ones((N,N,1))),axis=2).astype(np.float32)
    im.pixels.foreach_set(rgba.ravel());im.filepath_raw=str(TEX/(name+'.png'));im.file_format='PNG';im.save();im.pack();return im
normal_image=image('cast-grain-normal',(normal+1)/2)
orm_image=image('cast-metallic-roughness',np.stack((np.ones_like(rough),rough,np.full_like(rough,.70)),axis=-1))
paint=bpy.data.materials['Panel silver cast coating - candidate'];nodes=paint.node_tree.nodes;links=paint.node_tree.links;p=nodes.get('Principled BSDF')
p.inputs['Base Color'].default_value=(.43,.45,.48,1)
tex=nodes.new('ShaderNodeTexImage');tex.image=orm_image;tex.label='Original periodic data: G roughness, B metallic'
sep=nodes.new('ShaderNodeSeparateColor');links.new(tex.outputs['Color'],sep.inputs['Color']);links.new(sep.outputs['Green'],p.inputs['Roughness']);links.new(sep.outputs['Blue'],p.inputs['Metallic'])
nt=nodes.new('ShaderNodeTexImage');nt.image=normal_image;nt.label='10 mm tile; estimated 1.8 micrometre RMS grain'
nm=nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.65;links.new(nt.outputs['Color'],nm.inputs['Color']);links.new(nm.outputs['Normal'],p.inputs['Normal'])
paint['texture_provenance']='Original seeded periodic mathematical height field; no reference photo pixels';paint['tile_size_m']=TILE
paint['roughness_mean_estimated']=.365;paint['height_rms_m_estimated']=.0000018

body=bpy.data.objects['Front brake panel - editable casting'];deps=bpy.context.evaluated_depsgraph_get()
original=body.copy();original.data=body.data.copy();original.name='V1 parametric casting - retained hidden';bpy.data.collections['EDITABLE_CAST_FEATURES_AND_DRILLING'].objects.link(original);original.hide_render=True;original.hide_set(True)
evaluated=bpy.data.meshes.new_from_object(body.evaluated_get(deps),depsgraph=deps)
body.modifiers.clear();body.data=evaluated
body['revision']='front-brake-plate-v2';body['geometry_change']='None; v1 evaluated surface retained, PBR maps and physical-scale UV added'

def box_uv(mesh):
    mesh.update();uv=mesh.uv_layers.new(name='Physical 10mm box projection')
    # Projection uses actual metres. Local seams can remain at box boundaries;
    # microscopic isotropic pattern, not an unwrap intended for labels or large scratches.
    for poly in mesh.polygons:
        n=poly.normal;axis=max(range(3),key=lambda a:abs(n[a]));sign=1 if n[axis]>=0 else -1
        for li in poly.loop_indices:
            co=mesh.vertices[mesh.loops[li].vertex_index].co
            pair=(sign*co.y,co.z) if axis==0 else (-sign*co.x,co.z) if axis==1 else (sign*co.x,co.y)
            uv.data[li].uv=(pair[0]/TILE,pair[1]/TILE)
box_uv(body.data)
inspection=bpy.data.objects['Front brake panel - inspection export'];box_uv(inspection.data)
def export(filename,objects):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:obj.hide_set(False);obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.export_scene.gltf(filepath=str(HERE/filename),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=False)
export('front-brake-plate-v2-inspection.glb',[inspection])
fit=[o for o in bpy.data.collections['FIT_INSPECTION_LINKED_CANDIDATES'].objects if o.type=='MESH']
export('front-wheel-panel-v2-fit-inspection.glb',[inspection]+fit)
inspection.hide_render=True;inspection.hide_set(True)
for obj in fit:obj.hide_render=True
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'front-brake-plate-v2.blend'),compress=True)
report={'revision':'front-brake-plate-v2','scope':'Material-only candidate; geometry unchanged from v1 evaluated surface','source_sha256':hashlib.sha256((HERE/'front-brake-plate-v2.blend').read_bytes()).hexdigest(),'texture_origin':'Original periodic seeded FFT height field; no photographed/manufacturer pixels','seed':SEED,'resolution_px':[N,N],'tile_size_m':TILE,'height_rms_m_estimated':float(height.std()),'grain_correlation_scale_m_estimated':.00016,'normal_strength':.65,'roughness_range':[float(rough.min()),float(rough.max())],'normal_xy_standard_deviation':normal[:,:,:2].std(axis=(0,1)).tolist(),'uv_method':'Face-dominant box projection in physical metres; boundary seams require review','maps':[{'file':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(TEX.glob('*.png'))],'reflectance_measured':False,'art_accepted':False}
(OUT/'material-build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('WEWA_PANEL_MATERIAL_V2',json.dumps(report))
