"""Only placement and own guide update; the refused housing's local shape is protected."""
from pathlib import Path
import bpy,json,hashlib,sys,array
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/ignition-connector-v2'
P=json.loads((H/'parameters-v2.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not(H/'preflight-manifest-v2.json').exists()
for k in ['original_geometry_source','original_geometry_report','pigtail_source','pigtail_report','pigtail_parameters','baseline_shape_parameters']:
    assert sha(R/P[k])==P[k+'_sha256']
B=json.loads((R/P['original_geometry_report']).read_text())
PB=json.loads((R/P['pigtail_report']).read_text());assert PB['conditional_interfaces_passed']
bpy.ops.wm.open_mainfile(filepath=str(R/P['original_geometry_source']))
sys.path.insert(0,str(H.parent/'throttle-control'))
from control_geometry import mesh_object,check_mesh,tree_world,export
o=bpy.data.objects[B['geometry'][0]['name']];root=o.parent
def signature():
    m=o.data;m.calc_loop_triangles();r={}
    for name,seq,key,n in [('positions',m.vertices,'co',3),('corner_normals',m.corner_normals,'vector',3),('UV',m.uv_layers.active.data,'uv',2)]:
        a=array.array('f',[0.]*(len(seq)*n));seq.foreach_get(key,a);r[name]=hashlib.sha256(a.tobytes()).hexdigest()
    r['indices']=hashlib.sha256(array.array('I',[i for t in m.loop_triangles for i in t.vertices]).tobytes()).hexdigest()
    r['object_matrix_basis']=[list(v)for v in o.matrix_basis]
    r['object_parent_inverse']=[list(v)for v in o.matrix_parent_inverse]
    r['material_constants']=[list(o.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value),o.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value,o.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value]
    return r
before=signature()
G=bpy.data.collections['CONNECTOR_OWN_WORLD_SNAPSHOTS_NOT_EXPORTED'];G.hide_viewport=False
with bpy.data.libraries.load(str(R/P['pigtail_source']),link=False)as(a,l):l.objects=[P['pigtail_object']]
wire=l.objects[0];G.objects.link(wire);bpy.context.view_layer.update()
ev=wire.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles()
vs=[wire.matrix_world@v.co for v in m.vertices];fs=[list(t.vertices)for t in m.loop_triangles];ev.to_mesh_clear()
end=sum(vs[-96:-48],Vector())/48;prev=sum(vs[-192:-144],Vector())/48;T=(end-prev).normalized()
old_guide=next(g for g in G.objects if g!=wire and g.get('snapshot_group')=='pigtail')
old_mesh=old_guide.data;new_mesh=bpy.data.meshes.new('Actual revisedpigtail3 world snapshot')
new_mesh.from_pydata(vs,[],fs);new_mesh.update()
for f in new_mesh.polygons:f.use_smooth=True
new_mesh.materials.append(old_mesh.materials[0]);old_guide.data=new_mesh
bpy.data.objects.remove(wire,do_unlink=True)
Z=-T;Y=(Vector((0,0,1))-Z*Z.z).normalized();X=Y.cross(Z).normalized()
origin=end+T*(P['working_wireentry_Z_m']+P['working_wireentry_gap_m'])
M=Matrix(((X.x,Y.x,Z.x,origin.x),(X.y,Y.y,Z.y,origin.y),(X.z,Y.z,Z.z,origin.z),(0,0,0,1)))
root.matrix_world=M;bpy.context.view_layer.update();assert signature()==before
deviation=max(((root.matrix_world@v.co)-(M@v.co)).length for v in o.data.vertices)

# Add only the visor snapshots already evaluated in the revised cable source.
with bpy.data.libraries.load(str(R/P['pigtail_source']),link=False)as(a,l):l.collections=['CABLES_V3_OWN_WORLD_SNAPSHOTS_NOT_EXPORTED']
temp=l.collections[0];bpy.context.scene.collection.children.link(temp);temp.hide_viewport=False
bpy.context.view_layer.update();visor_rows=[]
for g in temp.all_objects:
    if g.get('snapshot_group')!='visor':continue
    ev=g.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles()
    visor_rows.append((g['source_object'],[list(g.matrix_world@v.co)for v in m.vertices],[list(t.vertices)for t in m.loop_triangles]));ev.to_mesh_clear()
for g in list(temp.all_objects):bpy.data.objects.remove(g,do_unlink=True)
bpy.data.collections.remove(temp)
guide_mat=old_guide.data.materials[0]
for name,vertices,faces in visor_rows:
    g=mesh_object('GUIDE '+name,vertices,faces,G,guide_mat);g['source_object']=name;g['snapshot_group']='visor'
bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
bpy.context.view_layer.update();geom=check_mesh(o);assert geom==B['geometry'][0]
tree=tree_world(o);rows=[{'guide':g['source_object'],'group':g['snapshot_group'],'surface_crossing_pairs':len(tree.overlap(tree_world(g)))}for g in G.objects]
passed=not any(r['surface_crossing_pairs']for r in rows)
entry=root.matrix_world@Vector((0,0,P['working_wireentry_Z_m']))
G.hide_render=True;G.hide_viewport=True
source=H/'ignition-connector-v2-geometry.blend';glb=H/'ignition-connector-v2-geometry.glb'
export(glb,[root,o]);bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
report={**B,'revision':P['revision'],'source_sha256':sha(source),'export_sha256':sha(glb),
        'original_local_geometry_source_sha256':P['original_geometry_source_sha256'],
        'original_local_geometry_export_sha256':B['export_sha256'],
        'source_local_geometry_normals_UV_indices_child_matrices_material_identical':True,
        'protected_local_signatures':before,'geometry':[geom],
        'conditional_root_world_matrix':[list(v)for v in root.matrix_world],
        'target_root_world_matrix':[list(v)for v in M],
        'saved_root_vs_target_max_vertex_deviation_m':deviation,
        'pigtail_source_sha256':P['pigtail_source_sha256'],'pigtail_export_sha256':PB['export_sha256'],
        'pigtail_free_end_world_m':list(end),'pigtail_actual_last_tangent_world':list(T),
        'actual_wireentry_centre_world_m':list(entry),'actual_entry_centre_to_wire_end_distance_m':(entry-end).length,
        'conditional_surface_checks':rows,'conditional_interfaces_passed':passed,
        'lineage':'Originalclosedhousinggeometry retained exactly; only conditionalrootpose and ownpigtail/visorsnapshot updates. OriginalCSG/cleanup are historical, not repeated here.',
        'pose_and_route_are_artistic_estimates':True,'installed_fit_received':False,'art_accepted':False}
bpy.ops.wm.open_mainfile(filepath=str(source))
report['source_libraries']=len(bpy.data.libraries)
report['source_file_images']=len([i for i in bpy.data.images if i.source=='FILE'and i.filepath])
assert report['source_libraries']==report['source_file_images']==0
for k in ['original_geometry_source','original_geometry_report','pigtail_source','pigtail_report','pigtail_parameters','baseline_shape_parameters']:assert sha(R/P[k])==P[k+'_sha256']
(H/'geometry-report-v2.json').write_text(json.dumps(report,indent=2)+'\n')
(O/'geometry-source-check.json').write_text(json.dumps(report,indent=2)+'\n')
(O/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n')
print('CONNECTOR_POSE_V2',json.dumps({k:report[k]for k in['source_sha256','export_sha256','conditional_interfaces_passed','actual_entry_centre_to_wire_end_distance_m','saved_root_vs_target_max_vertex_deviation_m']}),flush=True)
assert passed,{'crossings':[r for r in rows if r['surface_crossing_pairs']]}
