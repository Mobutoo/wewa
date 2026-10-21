"""One observable candidate screw type, two conditional unchanged-shield frames."""
from pathlib import Path
import bpy,bmesh,json,hashlib,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/exhaust-heatshield-fastener-v1';P=json.loads((H/'parameters.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert not(H/'preflight-manifest.json').exists()
for k in ['shield_source','shield_interfaces','body_source']:assert sha(R/P[k])==P[k+'_sha256']
sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import material,check_mesh,export,studio
sys.path.insert(0,str(H));from fastener_geometry import build
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;parts=bpy.data.collections.new('WEWA_EXHAUST_HEATSHIELD_FASTENERS');guides=bpy.data.collections.new('SHIELD_FASTENER_IMMUTABLE_GUIDES');stage=bpy.data.collections.new('SHIELD_FASTENER_STUDIO_NOT_EXPORTED')
for c in [parts,guides,stage]:s.collection.children.link(c)
verts,faces,UV,shape=build(P);m=bpy.data.meshes.new('One original wide-bearing cosmetic-thread screw candidate');m.from_pydata(verts,[],faces);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(m);bm.free();m.update()
for f in m.polygons:f.use_smooth=True
uv=m.uv_layers.new(name='Original screw meridian atlas')
for f,old,coords in zip(m.polygons,faces,UV):
 assert set(f.vertices)==set(old);mapping=dict(zip(old,coords))
 for li in f.loop_indices:uv.data[li].uv=mapping[m.loops[li].vertex_index]
M=P['material_baseline'];m.materials.append(material('Representative bright plated screw - optical values estimated',M['linear_basecolor'],M['metallic'],M['roughness']));datum=bpy.data.objects.new('Heatshield fastener pair conditional installation datum',None);parts.objects.link(datum);frames=json.loads((R/P['shield_interfaces']).read_text())['working_hole_frames'];positions=[Vector(q['working_front_seat_centre_world_m'])-Vector((P['working_head_to_seat_free_X_gap_m'],0,0))for q in frames];datum.location=positions[0];objects=[]
for i,pos in enumerate(positions):
 o=bpy.data.objects.new('Shield fixing '+str(i+1)+' - JW591028 related, unknown drive',m);parts.objects.link(o);o.parent=datum;o.location=pos-positions[0];objects.append(o)
bpy.context.view_layer.update();m.calc_loop_triangles();assert min(t.area for t in m.loop_triangles)>0;geometry=[check_mesh(o)for o in objects]
for k,collection in [('shield_source','WEWA_EXHAUST_HEATSHIELD'),('body_source','WEWA_EXHAUST_SILENCER_BODY')]:
 with bpy.data.libraries.load(str(R/P[k]),link=True)as(a,l):l.collections=[collection]
 for c in l.collections:guides.children.link(c)
bpy.context.view_layer.update()
def tree(o):
 assert not o.modifiers;me=o.data;me.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in me.vertices],[tuple(t.vertices)for t in me.loop_triangles],all_triangles=True)
rows=[{'a':o.name,'b':q.name,'surface_pairs':len(tree(o).overlap(tree(q)))}for o in objects for q in guides.all_objects if q.type=='MESH'];assert all(q['surface_pairs']==0 for q in rows),rows
guides.hide_render=True;guides.hide_viewport=True;glb=H/'exhaust-heatshield-fastener-inspection.glb';export(glb,[datum]+objects);studio(s,stage,positions[0]);s.camera.data.clip_start=.0001
for o in stage.objects:
 if o.type=='MESH':o.hide_render=True
 if o.type=='LIGHT':o.data.energy*=.004
for lib in bpy.data.libraries:
 if lib.parent is None:lib.filepath=bpy.path.relpath(bpy.path.abspath(lib.filepath),start=str(H))
source=H/'exhaust-heatshield-fastener-v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True,relative_remap=False);report={'component_id':P['component_id'],'revision':P['revision'],'source_sha256':sha(source),'export_sha256':sha(glb),'geometry':geometry,'physical_type_count':1,'conditional_instances':2,'shape':shape,'collection':parts.name,'root':datum.name,'datum_world_matrix':[list(q)for q in datum.matrix_world],'instance_world_matrices':[{'name':o.name,'matrix':[list(q)for q in o.matrix_world]}for o in objects],'source_guide_surface_checks':rows,'shared_mesh_data':objects[0].data is objects[1].data,'triangles_per_instance':len(m.loop_triangles),'zero_area_triangles':0,'art_accepted':False};(H/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');(O/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');print('SHIELD_FASTENERS',json.dumps(report),flush=True)
