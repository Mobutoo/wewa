"""Material-only original striations; frozen source geometry remains bit-identical.

No normalmap/tangent buffer work or relief claim. Two real source-atlas maps.
"""
from pathlib import Path
import bpy,json,hashlib,math,numpy as np
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-intake-insulator-v2';T=H/'textures-v2';T.mkdir(exist_ok=True)
assert not (H/'preflight-manifest-v2.json').exists(),'Frozen v2 must remain immutable'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();P=json.loads((H/'parameters-v2.json').read_text());G=P['original_grain'];source1=H/'engine-intake-insulator-v1.blend';pre1=H/'preflight-manifest.json';m1=json.loads(pre1.read_text());assert sha(source1)==m1['source_sha256']==P['protected_source_sha256'];assert sha(H/'engine-intake-insulator-inspection.glb')==m1['export_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source1));s=bpy.context.scene;old=json.loads((H/'build-report.json').read_text());o=bpy.data.objects[old['geometry'][0]['name']];datum=o.parent

def snapshot(obj):
 m=obj.data;m.calc_loop_triangles()
 return {'positions':[list(v.co)for v in m.vertices],'polygons':[list(p.vertices)for p in m.polygons],'loop_triangles':[list(t.vertices)for t in m.loop_triangles],'corner_normals':[list(n.vector)for n in m.corner_normals],'world_matrix':[list(r)for r in obj.matrix_world],'parent_matrix':[list(r)for r in obj.parent.matrix_world]}
before=snapshot(o);native_digest=lambda q:hashlib.sha256(json.dumps(q,separators=(',',':')).encode()).hexdigest();protected_digest=native_digest(before)
bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=G['packing_margin_fraction'],area_weight=0,correct_aspect=True,scale_to_bounds=False);bpy.ops.object.mode_set(mode='OBJECT');mesh=o.data;mesh.uv_layers.active.name='Original insulator striation atlas v2';mesh.calc_loop_triangles();UV=mesh.uv_layers.active.data;areas=[]
for tri in mesh.loop_triangles:
 a,b,c=[UV[i].uv for i in tri.loops];areas.append(abs((b-a).cross(c-a))/2)
assert min(areas)>0 and before==snapshot(o)
mat=o.data.materials[0];mat.name='Original dark insulating finish - estimated striations v2';n=mat.node_tree.nodes;links=mat.node_tree.links;p=n.get('Principled BSDF');out=n.get('Material Output')
coord=n.new('ShaderNodeTexCoord');coord.name='Original part-local metre coordinates'
rotate=n.new('ShaderNodeVectorRotate');rotate.rotation_type='AXIS_ANGLE';rotate.inputs['Axis'].default_value=(0,0,1);rotate.inputs['Angle'].default_value=math.radians(G['direction_working_deg']);links.new(coord.outputs['Object'],rotate.inputs['Vector'])
scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(1/G['directional_transverse_spacing_working_m'],1/G['directional_length_working_m'],1/G['fine_spacing_working_m']);links.new(rotate.outputs['Vector'],scale.inputs[0])
streak=n.new('ShaderNodeTexNoise');streak.name='Original irregular elongated streaks - angle scale estimated';streak.noise_dimensions='4D';streak.inputs['Scale'].default_value=1;streak.inputs['Detail'].default_value=.8;streak.inputs['Roughness'].default_value=.6;streak.inputs['W'].default_value=G['noise_seed_W'];links.new(scale.outputs['Vector'],streak.inputs['Vector'])
fineScale=n.new('ShaderNodeVectorMath');fineScale.operation='SCALE';fineScale.inputs['Scale'].default_value=1/G['fine_spacing_working_m'];links.new(coord.outputs['Object'],fineScale.inputs[0]);fine=n.new('ShaderNodeTexNoise');fine.name='Original fine chromatic and roughness grain - no relief';fine.noise_dimensions='4D';fine.inputs['Scale'].default_value=1;fine.inputs['Detail'].default_value=0;fine.inputs['W'].default_value=G['noise_seed_W']+1;links.new(fineScale.outputs['Vector'],fine.inputs['Vector'])
a=n.new('ShaderNodeMath');a.operation='MULTIPLY';a.inputs[1].default_value=.7;links.new(streak.outputs['Fac'],a.inputs[0]);b=n.new('ShaderNodeMath');b.operation='MULTIPLY';b.inputs[1].default_value=.3;links.new(fine.outputs['Fac'],b.inputs[0]);mix=n.new('ShaderNodeMath');mix.operation='ADD';links.new(a.outputs[0],mix.inputs[0]);links.new(b.outputs[0],mix.inputs[1])
rough=n.new('ShaderNodeMapRange');rough.name='Original bounded roughness response';rough.inputs['To Min'].default_value=G['roughness_range'][0];rough.inputs['To Max'].default_value=G['roughness_range'][1];links.new(mix.outputs[0],rough.inputs['Value']);links.new(rough.outputs['Result'],p.inputs['Roughness'])
colorMult=n.new('ShaderNodeMapRange');colorMult.inputs['To Min'].default_value=G['basecolor_multiplier_range'][0];colorMult.inputs['To Max'].default_value=G['basecolor_multiplier_range'][1];links.new(mix.outputs[0],colorMult.inputs['Value'])
color=n.new('ShaderNodeMixRGB');color.blend_type='MULTIPLY';color.inputs[0].default_value=1;color.inputs[1].default_value=(*P['material_original']['linear_base_color'],1);links.new(colorMult.outputs['Result'],color.inputs[2]);links.new(color.outputs['Color'],p.inputs['Base Color'])
# Grain is a bounded variation of color/roughness; no normal, bump or displacement node.
assert not p.inputs['Normal'].is_linked
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16;s.render.bake.use_selected_to_active=False;s.render.bake.use_clear=False;s.render.bake.margin=G['bake_margin_px'];images={};stats={}
for kind,signal,background in [('basecolor',color.outputs['Color'],(*P['material_original']['linear_base_color'],1)),('roughness',rough.outputs['Result'],(.48,.48,.48,1))]:
 im=bpy.data.images.new('insulator-original-'+kind+'-v2',width=G['texture_size_px'][0],height=G['texture_size_px'][1],alpha=False);im.colorspace_settings.name='sRGB'if kind=='basecolor'else'Non-Color';im.generated_color=background
 target=n.new('ShaderNodeTexImage');target.name='BAKE_TARGET_'+kind;target.image=im
 for node in n:node.select=False
 target.select=True;n.active=target;emit=n.new('ShaderNodeEmission');links.new(signal,emit.inputs['Color']);links.new(emit.outputs[0],out.inputs['Surface']);bpy.ops.object.bake(type='EMIT');links.new(p.outputs['BSDF'],out.inputs['Surface']);n.remove(emit)
 px=np.empty(len(im.pixels),dtype=np.float32);im.pixels.foreach_get(px);v=px.reshape(-1,4)[:,:3];assert min(v.std(axis=0))>.0001,'Original signal is constant'
 im.filepath_raw=str(T/('insulator-striation-'+kind+'-v2.png'));im.file_format='PNG';im.save();im.pack();stats[kind]={'file':str(Path(im.filepath_raw).relative_to(R)),'sha256':sha(im.filepath_raw),'pixels':len(v),'minimum_buffer_rgb':v.min(axis=0).tolist(),'maximum_buffer_rgb':v.max(axis=0).tolist(),'std_buffer_rgb':v.std(axis=0).tolist(),'colorspace':im.colorspace_settings.name};images[kind]=im;n.remove(target)
for kind,inputName in [('basecolor','Base Color'),('roughness','Roughness')]:
 tex=n.new('ShaderNodeTexImage');tex.name='Exported original '+kind+' v2';tex.image=images[kind];links.new(tex.outputs['Color'],p.inputs[inputName])
assert before==snapshot(o),'Material-only revision changed source geometry/indices/normals/matrices'
bpy.ops.object.select_all(action='DESELECT')
for obj in [datum,o]:obj.hide_set(False);obj.select_set(True)
bpy.context.view_layer.objects.active=o;glb=H/'engine-intake-insulator-v2-inspection.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=False)
for im in images.values():im.filepath_raw='//textures-v2/'+Path(im.filepath_raw).name
for lib in bpy.data.libraries:
 if lib.parent is None:lib.filepath=bpy.path.relpath(bpy.path.abspath(lib.filepath),start=str(H))
source=H/'engine-intake-insulator-v2.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True,relative_remap=False)
r={**old,'revision':P['revision'],'source_sha256':sha(source),'export_sha256':sha(glb),'protected_v1_source_sha256':sha(source1),'protected_v1_geometry_digest':protected_digest,'new_geometry_digest':native_digest(snapshot(o)),'positions_indices_corner_normals_matrices_bit_identical':True,'material_revision_only':True,'normalmap_applied':False,'bump_or_displacement_applied':False,'tangent_attribute_exported':False,'native_tangent_buffers_repaired':False,'source_UV_triangle_count':len(areas),'source_UV_zero_area_triangles':sum(a==0 for a in areas),'source_UV_minimum_area':min(areas),'original_finish_recipe':G,'maps':stats,'photographic_pixels_used':False,'substrate_chemistry_or_relief_depth_measured':False,'art_accepted':False}
(H/'build-report-v2.json').write_text(json.dumps(r,indent=2)+'\n');(O/'source-material-check.json').write_text(json.dumps(r,indent=2)+'\n');assert sha(source1)==P['protected_source_sha256'];print('INSULATOR2_COLOR_ROUGHNESS',sha(source),sha(glb),stats,flush=True)
