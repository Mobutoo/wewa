"""One integral manifold exterior, annular before union, no hidden mechanism."""
from pathlib import Path
import bpy,bmesh,json,hashlib,math,sys
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-intake-manifold-v1'
assert not (H/'preflight-manifest.json').exists(), 'Frozen revision must stay immutable; author a separate revision'
P=json.loads((H/'parameters.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for k in ['insulator','head']:assert sha(R/P[k+'_source'])==P[k+'_sha256']
sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import material,csg,check_mesh,tree_world,export,studio,box
sys.path.insert(0,str(H.parent/'clutch-control'));from topology_cleanup_v2 import clean_evaluated
sys.path.insert(0,str(H));from section_geometry import curve,rounded_plate,through_bore,hollow_neck,cast_side_feature
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
def collection(name):c=bpy.data.collections.new(name);s.collection.children.link(c);return c
parts=collection('WEWA_ENGINE_INTAKE_MANIFOLD');construction=collection('INTAKE_MANIFOLD_RETAINED_CONSTRUCTION');guides=collection('INTAKE_MANIFOLD_IMMUTABLE_GUIDES');stage=collection('INTAKE_MANIFOLD_STUDIO_NOT_EXPORTED')
M=P['material_estimated'];mat=material('Original estimated cast metal - grain pending',M['linear_basecolor'],M['metallic'],M['roughness'])
contour=curve(P['base_outline_controls_uv_m'],P['outline_samples_per_span']);base=rounded_plate('Asymmetric cast flange with authored edge rounds',contour,P['working_base_thickness_m'],P['working_outer_base_edge_round_m'],construction,mat)
half=P['working_bolt_pitch_m']/2;holes=[through_bore('Through manifold mouth in base',P['working_inner_radius_m'],P['working_base_thickness_m'],P['working_entry_round_m'],(0,0),construction,192)]
for sign in [-1,1]:holes.append(through_bore('Manifold bolt ear '+str(sign),P['working_bolt_bore_radius_m'],P['working_base_thickness_m'],P['working_entry_round_m'],(sign*half,0),construction,128))
bpy.context.view_layer.update();pierced,base_ops=csg(base,[],holes,construction,mat,R,'Retained pierced flange before annular union')
neck,profile=hollow_neck(P,construction,mat);boss=cast_side_feature(P,construction,mat)
bpy.context.view_layer.update();body,union_ops=csg(pierced,[neck,boss],[],parts,mat,R,'Cast intake manifold hollow exterior - conditional UG5')
cleanup=clean_evaluated(body,construction);body.modifiers.clear();body.hide_set(False);body.select_set(True);bpy.context.view_layer.objects.active=body;bpy.ops.mesh.customdata_custom_splitnormals_clear();m=body.data;m.update()
for face in m.polygons:
    zz=[m.vertices[i].co.z for i in face.vertices]
    face.use_smooth=not any(max(abs(z-level)for z in zz)<1e-8 for level in [0,P['working_base_thickness_m'],P['working_neck_top_z_m']])
bm=bmesh.new();bm.from_mesh(m)
for edge in bm.edges:
    if len(edge.link_faces)==2 and edge.calc_face_angle()>math.radians(45):edge.smooth=False
bm.to_mesh(m);bm.free();m.update();m.calc_loop_triangles();assert all(t.area>0 for t in m.loop_triangles)
with bpy.data.libraries.load(str(R/P['insulator_source']),link=True)as(a,l):l.objects=['Intake insulator provisional rear seating datum','Intake insulating spacer exterior - conditional UG5']
for obj in l.objects:guides.objects.link(obj)
insulator=next(obj for obj in l.objects if obj.type=='MESH');is_root=insulator.parent
with bpy.data.libraries.load(str(R/P['head_source']),link=True)as(a,l):l.objects=['Engine head base provisional datum','Engine UG5 head hollow exterior casting - editable candidate']
for obj in l.objects:guides.objects.link(obj)
head=next(obj for obj in l.objects if obj.type=='MESH');guides.hide_viewport=False;bpy.context.view_layer.update()
datum=bpy.data.objects.new('Intake manifold provisional base datum',None);parts.objects.link(datum);datum.matrix_world=is_root.matrix_world@Matrix.Translation((0,0,.004+P['working_joint_gap_after_insulator_front_m']));body.parent=datum;bpy.context.view_layer.update()
interfaces=[{'guide':g.name,'pairs':len(tree_world(body).overlap(tree_world(g)))}for g in [insulator,head]];assert not any(x['pairs']for x in interfaces),interfaces
geometry=[check_mesh(body)];construction.hide_render=True;construction.hide_viewport=True;guides.hide_render=True;guides.hide_viewport=True
glb=H/'engine-intake-manifold-v1-geometry.glb';export(glb,[datum,body]);target=body.matrix_world@Vector((0,0,.020));studio(s,stage,target)
for obj in stage.objects:
    if obj.type=='MESH':obj.hide_render=True
    if obj.type=='LIGHT':obj.data.energy*=.02
s.camera.data.clip_start=.0005;file=H/'engine-intake-manifold-v1-geometry.blend';bpy.ops.wm.save_as_mainfile(filepath=str(file),compress=True)
for lib in bpy.data.libraries:
    if lib.parent is None:lib.filepath=bpy.path.relpath(bpy.path.abspath(lib.filepath),start=str(H))
bpy.ops.wm.save_as_mainfile(filepath=str(file),compress=True,relative_remap=False)
clean_ops=lambda x:{k:v for k,v in x.items()if k not in ['vertices','triangles']}
report={'component_id':P['component_id'],'revision':P['revision'],'source_sha256':sha(file),'export_sha256':sha(glb),'geometry':geometry,'collection':parts.name,'root':datum.name,
        'authored_neck_profile_z_r_m':profile,'base_CSG':clean_ops(base_ops),'annular_union_CSG':clean_ops(union_ops),'cleanup':cleanup,'surface_interfaces':interfaces,
        'source_inputs_sha256':{k:P[k+'_sha256']for k in ['insulator','head']},'datum_world_matrix':[list(v)for v in datum.matrix_world],
        'annular_neck_built_hollow_before_union':True,'majority_material_void_cut_used':False,'global_post_CSG_bevel':False,
        'side_boss_has_unproven_functional_opening':False,'reverse_or_neck_digits_certified':False,'material_grain_pending':True,'all_dimensions_estimated':True,'art_accepted':False}
(H/'geometry-report.json').write_text(json.dumps(report,indent=2)+'\n');(O/'geometry-source-check.json').write_text(json.dumps(report,indent=2)+'\n')
for k in ['insulator','head']:assert sha(R/P[k+'_source'])==P[k+'_sha256']
print('INTAKE_MANIFOLD_GEOMETRY',report['source_sha256'],report['export_sha256'],geometry)
