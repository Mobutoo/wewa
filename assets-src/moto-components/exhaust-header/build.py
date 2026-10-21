"""One hollow exhaust-header exterior, no silencer/flange or hidden internals."""
from pathlib import Path
import bpy,bmesh,json,hashlib,sys
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/exhaust-header-v1';assert not(H/'preflight-manifest.json').exists();P=json.loads((H/'parameters.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(R/P['head_source'])==P['head_sha256']
sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import material,check_mesh,tree_world,export,studio
sys.path.insert(0,str(H));from sweep_geometry import build
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
parts=bpy.data.collections.new('WEWA_EXHAUST_HEADER');guides=bpy.data.collections.new('EXHAUST_HEADER_IMMUTABLE_GUIDES');stage=bpy.data.collections.new('EXHAUST_HEADER_STUDIO_NOT_EXPORTED')
for c in [parts,guides,stage]:s.collection.children.link(c)
verts,faces,normals,UV,origin,shape=build(P);m=bpy.data.meshes.new('Authored C1 hollow exhaust tube wall');m.from_pydata(verts,[],faces);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(m);bm.free();m.update()
for f in m.polygons:f.use_smooth=True
# Author smooth surface normals on the actual source, not post-export correction.
m.normals_split_custom_set([normals[l.vertex_index]for l in m.loops]);uv=m.uv_layers.new(name='Authored sweep seam atlas')
for f,coords in zip(m.polygons,UV):
 for i,xy in zip(f.loop_indices,coords):uv.data[i].uv=xy
M=P['material_baseline'];mat=material('Original dark coated exhaust - estimated baseline',M['linear_basecolor'],M['metallic'],M['roughness']);m.materials.append(mat);o=bpy.data.objects.new('Hollow front and lower exhaust tube - conditional RDC',m);parts.objects.link(o);datum=bpy.data.objects.new('Exhaust header conditional free mouth datum',None);parts.objects.link(datum);datum.location=origin;o.parent=datum;bpy.context.view_layer.update();m.calc_loop_triangles();assert all(t.area>0 for t in m.loop_triangles);geometry=[check_mesh(o)]
headReport=json.loads((R/P['head_report']).read_text());names=[headReport['parent_datum'],headReport['geometry'][0]['name']]
with bpy.data.libraries.load(str(R/P['head_source']),link=True)as(a,l):l.objects=names
for obj in l.objects:guides.objects.link(obj)
bpy.context.view_layer.update();head=next(q for q in l.objects if q.type=='MESH');cross=len(tree_world(o).overlap(tree_world(head)))
for ref in P['immutable_additional_guides']:
    file=R/ref['path'];assert sha(file)==ref['sha256']
    with bpy.data.libraries.load(str(file),link=True)as(a,l):l.collections=[ref['collection']]
    for c in l.collections:guides.children.link(c)
bpy.context.view_layer.update()
def retained_tree(obj):
    assert not obj.modifiers, 'This direct retained mesh check needs evaluated source without modifiers'
    mesh=obj.data;mesh.calc_loop_triangles();return BVHTree.FromPolygons([obj.matrix_world@v.co for v in mesh.vertices],[tuple(t.vertices)for t in mesh.loop_triangles],all_triangles=True)
interface=[];own_tree=retained_tree(o)
for q in list(guides.all_objects):
    if q.type=='MESH':
        print('EXHAUST_GUIDE_CHECK',q.name,flush=True);interface.append({'name':q.name,'surface_crossing_pairs':len(own_tree.overlap(retained_tree(q)))})
# Keep unresolved interface numerical facts visible instead of moving the frozen head.
guides.hide_render=True;guides.hide_viewport=True;glb=H/'exhaust-header-v1-geometry.glb';export(glb,[datum,o]);target=Vector(tuple((min((o.matrix_world@v.co)[i]for v in m.vertices)+max((o.matrix_world@v.co)[i]for v in m.vertices))/2 for i in range(3)));studio(s,stage,target);s.camera.location=target+Vector((-1.1,-1.0,.45));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler()
for obj in stage.objects:
 if obj.type=='MESH':obj.hide_render=True
 if obj.type=='LIGHT':obj.data.energy*=.06
s.camera.data.clip_start=.001;source=H/'exhaust-header-v1-geometry.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
for lib in bpy.data.libraries:
 if lib.parent is None:lib.filepath=bpy.path.relpath(bpy.path.abspath(lib.filepath),start=str(H))
bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True,relative_remap=False);report={'component_id':P['component_id'],'revision':P['revision'],'source_sha256':sha(source),'export_sha256':sha(glb),'geometry':geometry,'shape':shape,'collection':parts.name,'root':datum.name,'datum_world_matrix':[list(r)for r in datum.matrix_world],'head_source_sha256':P['head_sha256'],'head_surface_crossing_pairs':cross,'candidate_guide_surface_tests':interface,'source_analytic_normals':True,'all_dimensions_estimated':True,'silencer_flange_gasket_mounts_or_internals_fabricated':False,'art_accepted':False};(H/'geometry-report.json').write_text(json.dumps(report,indent=2)+'\n');(O/'geometry-source-check.json').write_text(json.dumps(report,indent=2)+'\n');assert sha(R/P['head_source'])==P['head_sha256'];print('EXHAUST_HEADER_GEOMETRY',json.dumps(report),flush=True)
