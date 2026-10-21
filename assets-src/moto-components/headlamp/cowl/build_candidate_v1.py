"""Original clean PBR finish on bounded cowl geometry, no photograph texture or weathering."""
import bpy,numpy as np,json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[3];P=R/'creative/reviews/headlamp-cowl-v1';P.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();base_report=R/'creative/reviews/headlamp-cowl-shell-study-v14/source-geometry-check.json';j=json.loads(base_report.read_text());src=H/'headlamp-cowl-shell-study-v14.blend';assert sha(src)==j['source_sha256'];assert (R/'creative/reviews/headlamp-cowl-shell-study-v14/study-freeze-manifest.json').exists(),'Gray14 actualreading/freeze required before material candidate';plan=R/'creative/research/headlamp-cowl/material-plan-v1.json';pj=json.loads(plan.read_text());bpy.ops.wm.open_mainfile(filepath=str(src));obj=bpy.data.objects[j['object']];m=obj.data

def geometry_fingerprints():
 result={}
 for name,collection,field,dtype,size in [('positions',m.vertices,'co',np.float32,3),('oriented_corner_vertex_indices',m.loops,'vertex_index',np.int32,1),('corner_UV',m.uv_layers.active.data,'uv',np.float32,2),('corner_normals',m.corner_normals,'vector',np.float32,3)]:
  values=np.empty(len(collection)*size,dtype=dtype);collection.foreach_get(field,values);result[name]=hashlib.sha256(values.tobytes()).hexdigest()
 for name in ['WEWA_source_input_index','WEWA_source_triangle_index','WEWA_surface_class']:
  values=np.empty(len(m.polygons),np.int32);m.attributes[name].data.foreach_get('value',values);result[name]=hashlib.sha256(values.tobytes()).hexdigest()
 return result
before=geometry_fingerprints()
def material(name,c):
 a=bpy.data.materials.new(name);a.use_nodes=True;n=a.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=c['original_linear_RGBA'];n.inputs['Metallic'].default_value=c['metallic'];n.inputs['Roughness'].default_value=c['roughness'];n.inputs['IOR'].default_value=c['IOR'];n.inputs['Coat Weight'].default_value=c['coat_weight'];n.inputs['Coat Roughness'].default_value=c.get('coat_roughness',.12);a.diffuse_color=c['original_linear_RGBA'];a['WEWA_original_material']=True;a['measured_OEM_finish']=False;return a
red=material('WEWA original red coated nonmetallic paint - estimated',pj['red_paint_candidate'])
black=material('WEWA original dark moulded polymer - estimated',pj['inner_moulded_polymer_candidate'])
m.materials.clear();m.materials.append(red);m.materials.append(black)
# Cache numeric FACE data before the first material_index write allocates a new
# CustomData layer. Holding RNA attribute wrappers over this allocation is unsafe.
classes=np.empty(len(m.polygons),np.int32)
m.attributes['WEWA_surface_class'].data.foreach_get('value',classes)
centers=np.empty(len(m.polygons)*3,np.float32)
m.polygons.foreach_get('center',centers)
centers=centers.reshape(-1,3)
paint=(classes==1)|((classes==3)&(centers[:,1]<=.0016))
indices=np.where(paint,0,1).astype(np.int32)
m.polygons.foreach_set('material_index',indices)
counts={'red':int(paint.sum()),'black':int((~paint).sum())}
by_class={str(int(sc)):{'red':int(np.sum((classes==sc)&paint)),'black':int(np.sum((classes==sc)&~paint))}for sc in np.unique(classes)}
assert geometry_fingerprints()==before,'Material-only revision changed a geometric buffer';obj.name='Headlamp cowl shell - bounded relatedvariant WEWA candidate';obj['WEWA_material_only_revision']=True;obj['WEWA_exact_RDC_shape']=False;obj['WEWA_not_user_received']=True;assert not bpy.data.libraries and not[a for a in bpy.data.images if a.source=='FILE'];source=H/'headlamp-cowl-v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True);bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);root=bpy.data.objects[j['root']];root.select_set(True);bpy.context.view_layer.objects.active=obj;export=H/'headlamp-cowl-inspection.glb';bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_cameras=False,export_lights=False,export_yup=True,export_extras=True)
report={'schema':1,'revision':'headlamp-cowl-v1','source_sha256':sha(source),'export_sha256':sha(export),'geometry_baseline_source14_sha256':j['source_sha256'],'geometry_baseline_export14_sha256':j['export_sha256'],'material_plan_sha256':sha(plan),'collection':j['collection'],'root':j['root'],'object':obj.name,'actual_triangles':j['actual_triangles'],'source_geometry_buffers_before':before,'source_geometry_buffers_after':geometry_fingerprints(),'material_only_positions_indices_UV_normals_bitidentical':True,'material_face_counts':counts,'material_face_counts_by_surface_class':by_class,'texture_photographs':0,'normal_maps':0,'external_libraries':0,'external_file_images':0,'paintmask_rule':'Class1exterior +class3frontrolledrim Y<=1.6mm: red; otherfaces black. Boundary is original construction hypothesis, not a measuredpaintmask.','state':'Bounded relatedvariant form/finish candidate. Sixsupports, distinctupperwallopenings, sevenpartialrib portions; no unidentifiedhiddenreturns/hardware or exactRDCmount reconstructed. Allscale/depth/paintparameters estimated. No artistic reception/runtimeLOD/iPhonequalification.','art_accepted':False};(P/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');assert sha(src)==j['source_sha256'];print('COWL_PBR_CANDIDATE',json.dumps(report))
