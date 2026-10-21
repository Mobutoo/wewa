"""Refine only cap outer shoulder, retain all other physical references and pose."""
from pathlib import Path
import bpy,json,hashlib,math,sys,ast,array
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-spark-cap-v2';P=json.loads((H/'parameters-v2.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for k in ['base','plug','head']:assert sha(R/P[k+'_source'])==P[k+'_sha256']
sys.path.insert(0,str(H));from shoulder_profile_v2 import shoulder_profile
sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import mesh_object,csg,check_mesh,tree_world,export
sys.path.insert(0,str(H.parent/'clutch-control'));from topology_cleanup_v2 import clean_evaluated
bpy.ops.wm.open_mainfile(filepath=str(R/P['base_source']));s=bpy.context.scene;source=bpy.data.collections['WEWA_ENGINE_SPARK_CAP'];body=bpy.data.objects['Molded spark cap body - conditional candidate'];contact=bpy.data.objects['Visible short-port metallic contact - section estimated'];datum=body.parent;before_matrix=[list(r)for r in datum.matrix_world];bodymatrix=[list(r)for r in body.matrix_world]
def fingerprint(o):
 m=o.data;m.calc_loop_triangles();verts=array.array('f',[0.]*(len(m.vertices)*3));m.vertices.foreach_get('co',verts);normals=array.array('f',[0.]*(len(m.loops)*3));m.corner_normals.foreach_get('vector',normals);data={'vertices':hashlib.sha256(verts.tobytes()).hexdigest(),'normals':hashlib.sha256(normals.tobytes()).hexdigest(),'triangles':[list(t.vertices)for t in m.loop_triangles],'UV':{u.name:[list(q.uv)for q in u.data]for u in m.uv_layers},'matrix':[list(r)for r in o.matrix_world],'materials':[{n:(list(v.default_value)if hasattr(v.default_value,'__len__')else v.default_value)for n in ['Base Color','Metallic','Roughness']if(v:=mat.node_tree.nodes['Principled BSDF'].inputs.get(n))is not None}for mat in m.materials]};return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
contact_before=fingerprint(contact);oldtree=tree_world(body);oldpoints=[v.co.copy()for v in body.data.vertices];oldmeshname=body.data.name;oldbodyvolume=check_mesh(body)['signed_volume_m3'];oldmaterial=body.data.materials[0];paint=oldmaterial.copy();paint.name='Original representative molded cap grain v2 - estimated'
construction=bpy.data.collections['SPARK_CAP_RETAINED_CONSTRUCTION'];construction.hide_viewport=False;construction.hide_render=True
# Reuse only the trusted immutable sampler definition, never execute v1 top-level.
sampler=next(n for n in ast.parse((H/'build.py').read_text()).body if isinstance(n,ast.FunctionDef)and n.name=='sectionmesh');exec(compile(ast.Module(body=[sampler],type_ignores=[]),str(H/'build.py'),'exec'),globals())
prefix=[(.024,0),(.024,.0093)]
for j in range(1,13):a=math.pi/2*j/12;prefix.append((.0243-.0003*math.cos(a),.0093+.0003*math.sin(a)))
prefix +=[(.0252,.0096),(.0255,.0094),(.0258,.009),(.051,.009)];shoulder,section=shoulder_profile(P);profile=prefix+shoulder+[(.075,.0052)]
for j in range(1,17):a=math.pi/2*j/16;profile.append((.075+.0052*math.sin(a),0 if j==16 else .0052*math.cos(a)))
main=sectionmesh('Cap2 original shoulder section construction',profile,paint,n=384,seam=True);port=bpy.data.objects['Original short transverse molded port'];longcut=bpy.data.objects['Estimated blind main plug socket'];shortcut=bpy.data.objects['Estimated short-port blind socket']
for o in [main,port,longcut,shortcut]:o.hide_set(False)
bpy.context.view_layer.update();temp,ops=csg(main,[port],[longcut,shortcut],source,paint,R,'Cap2 temporary merged envelope');cleanup=clean_evaluated(temp,construction);temp.modifiers.clear();newmesh=temp.data;oldmesh=body.data;body.data=newmesh;bpy.data.objects.remove(temp,do_unlink=True);bpy.data.meshes.remove(oldmesh);newmesh.name=oldmeshname
bpy.ops.object.select_all(action='DESELECT');body.hide_set(False);body.select_set(True);bpy.context.view_layer.objects.active=body;bpy.ops.mesh.customdata_custom_splitnormals_clear();newmesh.update()
for f in newmesh.polygons:f.use_smooth=True
bpy.context.view_layer.update();assert fingerprint(contact)==contact_before;assert before_matrix==[list(r)for r in datum.matrix_world];assert bodymatrix==[list(r)for r in body.matrix_world];newtree=tree_world(body)
def retained(v):
 x,y,z=v;r=(y*y+z*z)**.5
 return x<.051-1e-7 or x>.058+1e-7 or(.022-1e-7<x<.053+1e-7 and r<.00715)
oldretained=[body.matrix_world@v for v in oldpoints if retained(v)];newretained=[body.matrix_world@v.co for v in body.data.vertices if retained(v.co)];retention={'old_retained_vertices':len(oldretained),'new_retained_vertices':len(newretained),'old_to_new_surface_sample_max_m':max(newtree.find_nearest(v)[3]for v in oldretained),'new_to_old_surface_sample_max_m':max(oldtree.find_nearest(v)[3]for v in newretained),'region':'Outside outer shoulderX.051..058 plus original inner sockets. Sampled surface preservation, not a measured real mounting.'};assert max(retention[k]for k in ['old_to_new_surface_sample_max_m','new_to_old_surface_sample_max_m'])<1.1e-7,retention
construction.hide_render=True;construction.hide_viewport=True;bpy.data.collections['SPARK_CAP_IMMUTABLE_GUIDES'].hide_render=True;bpy.data.collections['SPARK_CAP_IMMUTABLE_GUIDES'].hide_viewport=True
# Save under the new filename before following plug2->cap1 library dependencies.
file=H/'engine-spark-cap-v2.blend';bpy.ops.wm.save_as_mainfile(filepath=str(file),compress=True);guides=bpy.data.collections.new('SPARK_CAP_V2_IMMUTABLE_GUIDES');s.collection.children.link(guides);plugreport=json.loads((H.parent/'engine-spark-plug/build-report-v2.json').read_text())
with bpy.data.libraries.load(str(R/P['plug_source']),link=True)as(a,l):l.objects=['Spark plug inherited estimated seat datum']+[r['name']for r in plugreport['geometry']]
for o in l.objects:guides.objects.link(o)
plugobjects=[o for o in l.objects if o.type=='MESH']
with bpy.data.libraries.load(str(R/P['head_source']),link=True)as(a,l):l.objects=['Engine head base provisional datum','Engine UG5 head hollow exterior casting - editable candidate']
for o in l.objects:guides.objects.link(o)
head=next(o for o in l.objects if o.type=='MESH');guides.hide_viewport=False;bpy.context.view_layer.update();objects=[body,contact];interfaces=[]
for a in objects:
 for b in plugobjects+[head]:interfaces.append({'a':a.name,'b':b.name,'pairs':len(tree_world(a).overlap(tree_world(b)))})
interfaces.append({'a':body.name,'b':contact.name,'pairs':len(tree_world(body).overlap(tree_world(contact)))})
assert not any(x['pairs']for x in interfaces),interfaces
geometry=[check_mesh(o)for o in objects];guides.hide_render=True;guides.hide_viewport=True;export(H/'engine-spark-cap-v2-geometry.glb',[datum]+objects);bpy.ops.wm.save_as_mainfile(filepath=str(file),compress=True)
for k in ['base','plug','head']:assert sha(R/P[k+'_source'])==P[k+'_sha256']
report={'component_id':P['component_id'],'revision':P['revision'],'geometry_source_sha256':sha(file),'geometry_export_sha256':sha(H/'engine-spark-cap-v2-geometry.glb'),'geometry':geometry,'source_geometry_profile':profile,'shoulder_section':section,'cleanup':cleanup,'protected_contact_fingerprint_before_after':contact_before,'protected_contact_exact':True,'datum_world_matrix_unchanged':before_matrix,'retained_body_surface_check':retention,'body_volume_before_m3':oldbodyvolume,'body_volume_after_m3':geometry[0]['signed_volume_m3'],'surface_interfaces':interfaces,'plug_source_sha256':P['plug_sha256'],'head_source_sha256':P['head_sha256'],'material_bake_pending':True,'all_dimensions_estimated':True,'art_accepted':False};(H/'geometry-report-v2.json').write_text(json.dumps(report,indent=2)+'\n');(O/'geometry-stage-check.json').write_text(json.dumps(report,indent=2)+'\n');print('CAP2_GEOMETRY',json.dumps({k:v for k,v in report.items()if k!='source_geometry_profile'}))
