"""One visible rear closure with small bore; main casing/shield/internals separate."""
from pathlib import Path
import bpy,bmesh,json,hashlib,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/exhaust-silencer-end-v1';assert not(H/'preflight-manifest.json').exists();P=json.loads((H/'parameters.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(R/P['body_source'])==P['body_sha256']and sha(R/P['body_interfaces'])==P['body_interfaces_sha256'];sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import material,check_mesh,export,studio
sys.path.insert(0,str(H));from annular_geometry import build
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;parts=bpy.data.collections.new('WEWA_EXHAUST_SILENCER_END');guides=bpy.data.collections.new('SILENCER_END_IMMUTABLE_GUIDES');stage=bpy.data.collections.new('SILENCER_END_STUDIO_NOT_EXPORTED')
for c in [parts,guides,stage]:s.collection.children.link(c)
verts,faces,normals,UV,origin,shape=build(P);m=bpy.data.meshes.new('Authored annular rear closure with small outlet');m.from_pydata(verts,[],faces);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(m);bm.free();m.update()
for f in m.polygons:f.use_smooth=True
m.normals_split_custom_set([normals[l.vertex_index]for l in m.loops]);uv=m.uv_layers.new(name='Authored shell seam atlas')
for f,coords in zip(m.polygons,UV):
 for i,xy in zip(f.loop_indices,coords):uv.data[i].uv=xy
M=P['material_baseline'];m.materials.append(material('Original dark silencer rear closure coating - estimated baseline',M['linear_basecolor'],M['metallic'],M['roughness']));o=bpy.data.objects.new('Rear silencer closure with small bore - conditional RDC',m);parts.objects.link(o);datum=bpy.data.objects.new('Silencer rear closure conditional front datum',None);parts.objects.link(datum);datum.location=origin;o.parent=datum;bpy.context.view_layer.update();m.calc_loop_triangles();assert all(t.area>0 for t in m.loop_triangles);geometry=[check_mesh(o)]
with bpy.data.libraries.load(str(R/P['body_source']),link=True)as(a,l):l.collections=['WEWA_EXHAUST_SILENCER_BODY']
for c in l.collections:guides.children.link(c)
bpy.context.view_layer.update()
def tree(q):
 assert not q.modifiers;mesh=q.data;mesh.calc_loop_triangles();return BVHTree.FromPolygons([q.matrix_world@v.co for v in mesh.vertices],[tuple(t.vertices)for t in mesh.loop_triangles],all_triangles=True)
interface=[{'name':q.name,'surface_crossing_pairs':len(tree(o).overlap(tree(q)))}for q in guides.all_objects if q.type=='MESH'];assert all(q['surface_crossing_pairs']==0 for q in interface)
guides.hide_render=True;guides.hide_viewport=True;glb=H/'exhaust-silencer-end-v1-geometry.glb';export(glb,[datum,o]);target=Vector(tuple((min((o.matrix_world@v.co)[i]for v in m.vertices)+max((o.matrix_world@v.co)[i]for v in m.vertices))/2 for i in range(3)));studio(s,stage,target);s.camera.location=target+Vector((-.9,-.8,.35));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler()
for obj in stage.objects:
 if obj.type=='MESH':obj.hide_render=True
 if obj.type=='LIGHT':obj.data.energy*=.06
s.camera.data.clip_start=.001
for lib in bpy.data.libraries:
 if lib.parent is None:lib.filepath=bpy.path.relpath(bpy.path.abspath(lib.filepath),start=str(H))
source=H/'exhaust-silencer-end-v1-geometry.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True,relative_remap=False);report={'component_id':P['component_id'],'revision':P['revision'],'source_sha256':sha(source),'export_sha256':sha(glb),'geometry':geometry,'shape':shape,'collection':parts.name,'root':datum.name,'datum_world_matrix':[list(r)for r in datum.matrix_world],'body_source_sha256':P['body_sha256'],'candidate_guide_surface_tests':interface,'source_analytic_normals':True,'all_dimensions_estimated':True,'main_shell_heatshield_supports_or_hidden_internals_fabricated':False,'art_accepted':False};(H/'geometry-report.json').write_text(json.dumps(report,indent=2)+'\n');(O/'geometry-source-check.json').write_text(json.dumps(report,indent=2)+'\n');assert sha(R/P['body_source'])==P['body_sha256'];print('SILENCER_END_CLOSURE',json.dumps(report),flush=True)
