"""Replace only v1 metal mesh after final native macro detected stair chamfer."""
from pathlib import Path
import bpy,bmesh,json,hashlib,sys,array
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-spark-plug-v2';P=json.loads((H/'parameters-v2.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for k in ['base','cap','head']:assert sha(R/P[k+'_source'])==P[k+'_sha256']
sys.path.insert(0,str(H));from body_geometry_v2 import body_geometry
sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import mesh_object,check_mesh,tree_world,export
bpy.ops.wm.open_mainfile(filepath=str(R/P['base_source']));s=bpy.context.scene;source=bpy.data.collections['WEWA_ENGINE_SPARK_PLUG_EXTERIOR'];body=bpy.data.objects['Plug metal body rounded hex - hidden insertion plain'];objects=[o for o in source.objects if o.type=='MESH'];other=[o for o in objects if o!=body];datum=body.parent
def signature(o):
 m=o.data;m.calc_loop_triangles();positions=array.array('f',[0.]*(len(m.vertices)*3));m.vertices.foreach_get('co',positions);normals=array.array('f',[0.]*(len(m.loops)*3));m.corner_normals.foreach_get('vector',normals);j={'positions_sha256':hashlib.sha256(positions.tobytes()).hexdigest(),'corner_normals_sha256':hashlib.sha256(normals.tobytes()).hexdigest(),'triangles':[list(t.vertices)for t in m.loop_triangles],'smooth':[f.use_smooth for f in m.polygons],'sharp':[e.use_edge_sharp for e in m.edges],'UV_layers':{uv.name:[list(q.uv)for q in uv.data]for uv in m.uv_layers},'matrix_world':[list(r)for r in o.matrix_world],'matrix_basis':[list(r)for r in o.matrix_basis],'parent':o.parent.name if o.parent else None,'materials':[{n:(list(v.default_value)if hasattr(v.default_value,'__len__')else v.default_value)for n in ['Base Color','Metallic','Roughness']if(v:=mat.node_tree.nodes['Principled BSDF'].inputs.get(n))is not None}for mat in m.materials]};return hashlib.sha256(json.dumps(j,sort_keys=True).encode()).hexdigest()
protected={o.name:signature(o)for o in other};datum_before=[list(r)for r in datum.matrix_world];material_before=[m.name for m in body.data.materials];bodymatrix_before=[list(r)for r in body.matrix_world];oldtree=tree_world(body);oldverts=[body.matrix_world@v.co for v in body.data.vertices];old_volume=check_mesh(body)['signed_volume_m3'];contour={tuple(v.co[1:])for v in body.data.vertices if abs(v.co.x-P['reference_hex_ring_x_m'])<1e-8 and Vector(v.co[1:]).length>.0079};assert len(contour)==222,len(contour)
verts,faces,flat,sharp,analytic=body_geometry(list(contour),P);temp=mesh_object('Analytic metal body temporary',verts,faces,source,body.data.materials[0]);newmesh=temp.data;oldmesh=body.data;oldname=oldmesh.name;body.data=newmesh;bpy.data.objects.remove(temp,do_unlink=True);bpy.data.meshes.remove(oldmesh);newmesh.name=oldname
for i in flat:newmesh.polygons[i].use_smooth=False
for f in newmesh.polygons:
 if abs(abs(f.normal.x)-1)<1e-7:f.use_smooth=False
explicit={tuple(sorted(pair))for pair in sharp};bm=bmesh.new();bm.from_mesh(newmesh);bm.verts.ensure_lookup_table()
for e in bm.edges:
 pair=tuple(sorted(v.index for v in e.verts))
 if pair in explicit or(len(e.link_faces)==2 and e.calc_face_angle(0)>.30):e.smooth=False
bm.to_mesh(newmesh);bm.free();newmesh.update();bpy.context.view_layer.update();newmesh.calc_loop_triangles();assert all(t.area>0 for t in newmesh.loop_triangles)
assert protected=={o.name:signature(o)for o in other};assert datum_before==[list(r)for r in datum.matrix_world];assert bodymatrix_before==[list(r)for r in body.matrix_world];assert material_before==[m.name for m in body.data.materials]
guides=bpy.data.collections['SPARK_PLUG_IMMUTABLE_HEAD_GUIDE'];guides.hide_viewport=False;head=next(o for o in guides.objects if o.type=='MESH');capguides=bpy.data.collections.new('SPARK_PLUG_V2_IMMUTABLE_CAP_GUIDE');s.collection.children.link(capguides)
capbuild=json.loads((H.parent/'engine-spark-cap/build-report.json').read_text())
with bpy.data.libraries.load(str(R/P['cap_source']),link=True)as(a,l):l.objects=['Spark cap inherited unchanged provisional plug datum']+[r['name']for r in capbuild['geometry']]
for o in l.objects:capguides.objects.link(o)
capobjects=[o for o in l.objects if o.type=='MESH'];capguides.hide_viewport=False;bpy.context.view_layer.update();interfaces=[]
for a in objects:
 for b in [head]+capobjects:interfaces.append({'a':a.name,'b':b.name,'pairs':len(tree_world(a).overlap(tree_world(b)))})
for a in other:interfaces.append({'a':body.name,'b':a.name,'pairs':len(tree_world(body).overlap(tree_world(a)))})
assert not any(r['pairs']for r in interfaces),interfaces
newtree=tree_world(body);newverts=[body.matrix_world@v.co for v in body.data.vertices];distances={'old_vertices_to_new_surface_sample_max_m':max(newtree.find_nearest(v)[3]for v in oldverts),'new_vertices_to_old_surface_sample_max_m':max(oldtree.find_nearest(v)[3]for v in newverts)}
equations={}
for label,ids in analytic['boundary_vertex_indices'].items():
 if 'intersection'not in label:continue
 errors=[]
 for i in ids:
  v=newmesh.vertices[i].co;r=(v.y*v.y+v.z*v.z)**.5;target=P['lower_cone_start_x_m']+(r-P['lower_cone_start_radius_m'])*P['lower_cone_dx_dr']if label.startswith('lower')else P['upper_cone_end_x_m']+(r-P['upper_cone_end_radius_m'])*P['upper_cone_dx_dr'];errors.append(abs(v.x-target))
 equations[label+'_maximum_actual_vertex_cone_residual_m']=max(errors)
assert max(equations.values())<5e-9,equations
geometry=[check_mesh(o)for o in objects];guides.hide_render=True;guides.hide_viewport=True;capguides.hide_render=True;capguides.hide_viewport=True;export(H/'engine-spark-plug-v2-inspection.glb',[datum]+objects);bpy.ops.wm.save_as_mainfile(filepath=str(H/'engine-spark-plug-v2.blend'),compress=True)
for k in ['base','cap','head']:assert sha(R/P[k+'_source'])==P[k+'_sha256']
report={'component_id':P['component_id'],'revision':P['revision'],'source_sha256':sha(H/'engine-spark-plug-v2.blend'),'export_sha256':sha(H/'engine-spark-plug-v2-inspection.glb'),'base_source_sha256':P['base_sha256'],'geometry':geometry,'protected_three_parts_before_after_sha256':protected,'protected_three_parts_exact_in_source':True,'datum_world_matrix_unchanged':datum_before,'metal_material_names_unchanged':material_before,'analytic_boundary':analytic,'actual_boundary_equation_residuals':equations,'body_geometry_change_sampled':distances,'body_volume_before_m3':old_volume,'body_volume_after_m3':next(r['signed_volume_m3']for r in geometry if r['name']==body.name),'surface_interfaces':interfaces,'cap_source_sha256':P['cap_sha256'],'head_source_sha256':P['head_sha256'],'scope':'Bounded metal chamfer topology correction only. Three other physical volumes, allmaterials and root/world pose preserved. Hidden thread/electrode still omitted.','remaining_dimensions_estimated':True,'exact_RDC_identity_confirmed':False,'art_accepted':False,'physical_iphone_tested':False};(H/'build-report-v2.json').write_text(json.dumps(report,indent=2)+'\n');(O/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');print('ANALYTIC_PLUG_V2',json.dumps({k:v for k,v in report.items()if k!='analytic_boundary'}))
