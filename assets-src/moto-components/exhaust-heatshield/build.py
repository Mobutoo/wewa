"""One observable formed heatshield; two fasteners remain separate unmade units."""
from pathlib import Path
import bpy,bmesh,json,hashlib,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/exhaust-heatshield-v1';P=json.loads((H/'parameters.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert not(H/'preflight-manifest.json').exists()
for k in ['body_source','body_parameters','body_geometry_helper']:assert sha(R/P[k])==P[k+'_sha256']
sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import material,check_mesh,export,studio
sys.path.insert(0,str(H));from panel_geometry import build
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;parts=bpy.data.collections.new('WEWA_EXHAUST_HEATSHIELD');guides=bpy.data.collections.new('HEATSHIELD_IMMUTABLE_GUIDES');stage=bpy.data.collections.new('HEATSHIELD_STUDIO_NOT_EXPORTED')
for c in [parts,guides,stage]:s.collection.children.link(c)
verts,faces,normals,UV,origin,shape=build(P,json.loads((R/P['body_parameters']).read_text()),R);m=bpy.data.meshes.new('Formed asymmetric thin sheet with two pierced pressed seats');m.from_pydata(verts,[],faces);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(m);bm.free();m.update()
for f in m.polygons:f.use_smooth=True
# Analytic domain normals; explicit swept rim uses its own actual geometric normals.
limit=shape['skin_vertices_per_face']*2;source_normals=[normals[i]if i<limit else tuple(v.normal)for i,v in enumerate(m.vertices)];m.normals_split_custom_set([source_normals[l.vertex_index]for l in m.loops]);uv=m.uv_layers.new(name='Original panel parameter atlas')
for f,original,coords in zip(m.polygons,faces,UV):
 mapping=dict(zip(original,coords))
 assert set(f.vertices)==set(original)
 for li in f.loop_indices:uv.data[li].uv=mapping[m.loops[li].vertex_index]
M=P['material_baseline'];m.materials.append(material('Representative bright formed metal - estimated optical baseline',M['linear_basecolor'],M['metallic'],M['roughness']));o=bpy.data.objects.new('Formed heatshield with two dished true holes - conditional PF591045',m);parts.objects.link(o);datum=bpy.data.objects.new('Heatshield conditional body-conformal datum',None);parts.objects.link(datum);datum.location=origin;o.parent=datum;bpy.context.view_layer.update();m.calc_loop_triangles();areas=[t.area for t in m.loop_triangles];assert min(areas)>0;geometry=[check_mesh(o)]
with bpy.data.libraries.load(str(R/P['body_source']),link=True)as(a,l):l.collections=['WEWA_EXHAUST_SILENCER_BODY']
for c in l.collections:guides.children.link(c)
bpy.context.view_layer.update()
def tree(q):
 assert not q.modifiers;mesh=q.data;mesh.calc_loop_triangles();return BVHTree.FromPolygons([q.matrix_world@v.co for v in mesh.vertices],[tuple(t.vertices)for t in mesh.loop_triangles],all_triangles=True)
interface=[{'name':q.name,'surface_crossing_pairs':len(tree(o).overlap(tree(q)))}for q in guides.all_objects if q.type=='MESH'];assert all(q['surface_crossing_pairs']==0 for q in interface),interface
guides.hide_render=True;guides.hide_viewport=True;glb=H/'exhaust-heatshield-v1-geometry.glb';export(glb,[datum,o]);target=datum.location;studio(s,stage,target);s.camera.location=target+Vector((-.7,-.3,.2));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler()
for obj in stage.objects:
 if obj.type=='MESH':obj.hide_render=True
 if obj.type=='LIGHT':obj.data.energy*=.12
s.camera.data.clip_start=.001
for lib in bpy.data.libraries:
 if lib.parent is None:lib.filepath=bpy.path.relpath(bpy.path.abspath(lib.filepath),start=str(H))
source=H/'exhaust-heatshield-v1-geometry.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True,relative_remap=False);report={'component_id':P['component_id'],'revision':P['revision'],'source_sha256':sha(source),'export_sha256':sha(glb),'geometry':geometry,'shape':shape,'triangles':len(m.loop_triangles),'zero_area_triangles':sum(a==0 for a in areas),'collection':parts.name,'root':datum.name,'datum_world_matrix':[list(r)for r in datum.matrix_world],'body_source_sha256':P['body_source_sha256'],'candidate_guide_surface_tests':interface,'normals':'Analytic skin source normals, actual swept rim vertex normals; no arbitrary tangent repair','all_dimensions_estimated':True,'art_accepted':False};(H/'geometry-report.json').write_text(json.dumps(report,indent=2)+'\n');(O/'geometry-source-check.json').write_text(json.dumps(report,indent=2)+'\n');print('HEATSHIELD_GEOMETRY',json.dumps(report),flush=True)
