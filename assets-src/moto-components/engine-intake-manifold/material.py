"""Bake original bounded cast grain in the source UV atlas; native glTF only.

No photograph pixels or normal/tangent buffer repair. The two maps are an
estimated representative finish, not metrology or an OEM material sample.
"""
from pathlib import Path
import bpy, json, hashlib, sys, math, array
import numpy as np

H=Path(__file__).resolve().parent; R=H.parents[2]
assert not (H/'preflight-manifest.json').exists(), 'Frozen revision must stay immutable; author a separate revision'
O=R/'creative/reviews/engine-intake-manifold-v1'; T=H/'textures'; T.mkdir(exist_ok=True)
P=json.loads((H/'parameters.json').read_text()); G=P['original_grain']
geometry=json.loads((H/'topology-report.json').read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
stage=H/'engine-intake-manifold-v1-topology.blend'
assert sha(stage)==geometry['source_sha256']
bpy.ops.wm.open_mainfile(filepath=str(stage))
s=bpy.context.scene; body=bpy.data.objects[geometry['geometry'][0]['name']]
datum=body.parent
def snapshot(o):
    m=o.data; m.calc_loop_triangles()
    return {'vertices':[list(v.co)for v in m.vertices],
            'triangles':[list(t.vertices)for t in m.loop_triangles],
            'corner_normals':[list(n.vector)for n in m.corner_normals],
            'matrix':[list(r)for r in o.matrix_world]}
protected_before={o.name:snapshot(o) for o in [body]}
bpy.ops.object.select_all(action='DESELECT'); body.hide_set(False); body.select_set(True)
bpy.context.view_layer.objects.active=body
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=G['packing_margin_fraction'],area_weight=0.,correct_aspect=True,scale_to_bounds=False)
bpy.ops.object.mode_set(mode='OBJECT')
m=body.data; m.uv_layers.active.name='Original cast grain source atlas v1'
m.calc_tangents(uvmap=m.uv_layers.active.name)
tangent_lengths=[loop.tangent.length for loop in m.loops]
tangent_unit_error=max(abs(v-1) for v in tangent_lengths)
tangent_normal_dot=max(abs(loop.tangent.dot(m.corner_normals[loop.index].vector))for loop in m.loops)
uv_rechart=[]
assert tangent_unit_error<.001 and tangent_normal_dot<.001,(tangent_unit_error,tangent_normal_dot)
assert not any(loop.tangent.length<.5 for loop in m.loops),'Native source tangent remains zero'
m.calc_loop_triangles(); uv=m.uv_layers.active.data; area=[]
for tri in m.loop_triangles:
    a,b,c=[uv[i].uv for i in tri.loops]
    area.append(abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))/2)
assert min(area)>0, 'Collapsed source UV triangle'
assert protected_before=={o.name:snapshot(o)for o in [body]}, 'UV stage changed geometry/normals/pose'
mat=body.data.materials[0]; mat.name='Original representative cast alloy - estimated grain'; n=mat.node_tree.nodes; links=mat.node_tree.links
p=n.get('Principled BSDF'); output=n.get('Material Output')
coord=n.new('ShaderNodeTexCoord'); coord.name='Original recipe local metre coordinates'
scale=n.new('ShaderNodeVectorMath'); scale.operation='SCALE'; scale.inputs['Scale'].default_value=1/G['spacing_working_m']
links.new(coord.outputs['Object'],scale.inputs[0])
noise=n.new('ShaderNodeTexNoise'); noise.name='Original estimated isotropic cast grain'; noise.noise_dimensions='4D'
noise.inputs['W'].default_value=G['noise_seed_W']; noise.inputs['Scale'].default_value=1.
noise.inputs['Detail'].default_value=0.; links.new(scale.outputs['Vector'],noise.inputs['Vector'])
bump=n.new('ShaderNodeBump'); bump.name='Original recipe height estimate in metres'
bump.inputs['Strength'].default_value=1.; bump.inputs['Distance'].default_value=G['height_working_m']
links.new(noise.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],p.inputs['Normal'])
rough=n.new('ShaderNodeMapRange'); rough.name='Original bounded roughness recipe'
rough.inputs['From Min'].default_value=0.; rough.inputs['From Max'].default_value=1.
rough.inputs['To Min'].default_value=G['roughness_range'][0]; rough.inputs['To Max'].default_value=G['roughness_range'][1]
links.new(noise.outputs['Fac'],rough.inputs['Value']); links.new(rough.outputs['Result'],p.inputs['Roughness'])
s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=16
s.render.bake.use_selected_to_active=False; s.render.bake.margin=G['bake_margin_px']
s.render.bake.use_clear=False; s.render.bake.normal_space='TANGENT'
s.render.bake.normal_r='POS_X'; s.render.bake.normal_g='POS_Y'; s.render.bake.normal_b='POS_Z'
stats={}; images={}
for kind in ['normal','roughness']:
    im=bpy.data.images.new('manifold-original-'+kind+'-v1',width=G['texture_size_px'][0],height=G['texture_size_px'][1],alpha=False,float_buffer=False)
    im.colorspace_settings.name='Non-Color'
    im.generated_color=(.5,.5,1.,1.) if kind=='normal'else(.49,.49,.49,1.)
    target=n.new('ShaderNodeTexImage'); target.name='BAKE_TARGET_'+kind; target.image=im
    for node in n:node.select=False
    target.select=True; n.active=target
    if kind=='roughness':
        emit=n.new('ShaderNodeEmission'); links.new(rough.outputs['Result'],emit.inputs['Color']); links.new(emit.outputs[0],output.inputs['Surface'])
    bpy.ops.object.bake(type='NORMAL' if kind=='normal' else 'EMIT')
    if kind=='roughness':
        links.new(p.outputs['BSDF'],output.inputs['Surface']); n.remove(emit)
    pixels=np.empty(len(im.pixels),np.float32); im.pixels.foreach_get(pixels); a=pixels.reshape(-1,4)[:,:3]
    # Black unpainted padding is excluded; bake margin pixels remain valid data.
    valid=(a[:,2]>.5) if kind=='normal' else (a.max(axis=1)>.1)
    b=a[valid]; assert len(b)>100000
    stats[kind]={'pixels_excluding_unpainted_padding':len(b),'minimum_rgb':b.min(axis=0).tolist(),'maximum_rgb':b.max(axis=0).tolist(),'standard_deviation_rgb':b.std(axis=0).tolist()}
    if kind=='normal': assert min(b[:,0].std(),b[:,1].std())>.001,'Baked material normal is flat'
    else: assert b[:,0].std()>.001,'Baked roughness is constant'
    im.filepath_raw=str(T/('manifold-grain-'+kind+'-v1.png')); im.file_format='PNG'; im.save(); im.pack()
    stats[kind]['file']=str(Path(im.filepath_raw).relative_to(R)); stats[kind]['sha256']=sha(im.filepath_raw)
    images[kind]=im; n.remove(target)
# Render and export use the baked maps, original recipe nodes remain disconnected.
normaltex=n.new('ShaderNodeTexImage'); normaltex.name='Exported original tangent normal'; normaltex.image=images['normal']
normal=n.new('ShaderNodeNormalMap'); normal.space='TANGENT'; normal.uv_map=m.uv_layers.active.name; normal.inputs['Strength'].default_value=1.
links.new(normaltex.outputs['Color'],normal.inputs['Color']); links.new(normal.outputs['Normal'],p.inputs['Normal'])
roughtex=n.new('ShaderNodeTexImage'); roughtex.name='Exported original roughness'; roughtex.image=images['roughness']
links.new(roughtex.outputs['Color'],p.inputs['Roughness'])
assert protected_before=={o.name:snapshot(o)for o in [body]}, 'Bake stage changed geometry/normals/pose'
bpy.ops.object.select_all(action='DESELECT')
for o in [datum,body]:o.hide_set(False);o.select_set(True)
bpy.context.view_layer.objects.active=body
dest=H/'engine-intake-manifold-inspection.glb'
bpy.ops.export_scene.gltf(filepath=str(dest),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True)
source=H/'engine-intake-manifold-v1.blend'
for im in images.values(): im.filepath_raw='//textures/'+Path(im.filepath_raw).name
for lib in bpy.data.libraries:
    if lib.parent is None: lib.filepath=bpy.path.relpath(bpy.path.abspath(lib.filepath),start=str(H))
bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True,relative_remap=False)
report={**geometry,'source_sha256':sha(source),'export_sha256':sha(dest),'geometry_stage_source_sha256':geometry['source_sha256'],
        'material_bake_pending':False,'material_grain_pending':False,'original_grain_recipe':G,'material_maps':stats,
        'source_UV_triangle_count':len(area),'source_UV_zero_area_triangles':sum(v==0 for v in area),'source_UV_minimum_area':min(area),
        'source_UV_local_recharts':uv_rechart,'native_source_tangent_unit_error_max':tangent_unit_error,'native_source_tangent_normal_dot_max':tangent_normal_dot,
        'positions_triangles_corner_normals_and_matrices_unchanged_during_material_stage':True,
        'photo_pixels_used':False,'native_glTF_export':True,'tangents_repaired':False,'grain_or_material_measured':False,'unpainted_UV_filter_padding':{'normal':[.5,.5,1.],'roughness':.49,'bake_use_clear':False,'reason':'Neutral finite recipe values under antialiased island borders; black zero-roughness background rejected in earlier exported-UV probe.'}}
(H/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
(O/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n')
(O/'material-build-report.json').write_text(json.dumps({k:report[k]for k in ['source_sha256','export_sha256','original_grain_recipe','material_maps','source_UV_triangle_count','source_UV_minimum_area','positions_triangles_corner_normals_and_matrices_unchanged_during_material_stage','photo_pixels_used','native_glTF_export','tangents_repaired','grain_or_material_measured']},indent=2)+'\n')
assert sha(stage)==geometry['source_sha256']
print('MANIFOLD_BAKED',report['source_sha256'],report['export_sha256'],stats)
