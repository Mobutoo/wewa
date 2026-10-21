"""Isolated observed annular front; G5 remains explicitly unmounted/blocked."""
from pathlib import Path
import bpy,bmesh,json,hashlib,sys
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/exhaust-header-gasket-v1';P=json.loads((H/'parameters.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert not(H/'preflight-manifest.json').exists()
for k in ['header_interfaces','header_parameters']:assert sha(R/P[k])==P[k+'_sha256']
sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import material,check_mesh,export,studio
sys.path.insert(0,str(H));from annular_geometry import build
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;parts=bpy.data.collections.new('WEWA_EXHAUST_HEADER_GASKET');stage=bpy.data.collections.new('GASKET_STUDIO_NOT_EXPORTED');s.collection.children.link(parts);s.collection.children.link(stage);vertices,faces,normals,UV,shape=build(P);m=bpy.data.meshes.new('Raised annular exterior envelope - section unmeasured');m.from_pydata(vertices,[],faces);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(m);bm.free();m.update()
for f in m.polygons:f.use_smooth=True
m.normals_split_custom_set([normals[l.vertex_index]for l in m.loops]);uv=m.uv_layers.new(name='Original annular seam atlas')
for f,old,coords in zip(m.polygons,faces,UV):
 assert set(f.vertices)==set(old);mapping=dict(zip(old,coords))
 for li in f.loop_indices:uv.data[li].uv=mapping[m.loops[li].vertex_index]
M=P['material_baseline'];m.materials.append(material('Representative copper-looking finish - chemistry unconfirmed',M['linear_basecolor'],M['metallic'],M['roughness']));o=bpy.data.objects.new('JE591002 related annular exterior - unmounted candidate',m);parts.objects.link(o);datum=bpy.data.objects.new('Gasket isolated inspection datum - not motorcycle world',None);parts.objects.link(datum);o.parent=datum;bpy.context.view_layer.update();m.calc_loop_triangles();assert min(t.area for t in m.loop_triangles)>0;geometry=[check_mesh(o)];glb=H/'exhaust-header-gasket-v1-geometry.glb';export(glb,[datum,o]);studio(s,stage,Vector((0,0,0)));s.camera.data.clip_start=.0001
for q in stage.objects:
 if q.type=='MESH':q.hide_render=True
 if q.type=='LIGHT':q.data.energy*=.004
source=H/'exhaust-header-gasket-v1-geometry.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True,relative_remap=False);report={'component_id':P['component_id'],'revision':P['revision'],'source_sha256':sha(source),'export_sha256':sha(glb),'geometry':geometry,'shape':shape,'triangles':len(m.loop_triangles),'zero_area_triangles':0,'collection':parts.name,'root':datum.name,'datum_world_matrix':[list(q)for q in datum.matrix_world],'frame_role':P['frame_role'],'source_analytic_normals':True,'all_dimensions_estimated':True,'art_accepted':False};(H/'geometry-report.json').write_text(json.dumps(report,indent=2)+'\n');(O/'geometry-source-check.json').write_text(json.dumps(report,indent=2)+'\n');print('ISOLATED_GASKET_GEOMETRY',json.dumps(report),flush=True)
