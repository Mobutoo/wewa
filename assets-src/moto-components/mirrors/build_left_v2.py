"""Dedicated LH stud sampling revision: preserve all other source objects and rig."""
import bpy,bmesh,json,hashlib,sys,tempfile,subprocess,shutil
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(HERE));from stud_phase_mesh_v3 import make_stud
OUT=ROOT/'creative/reviews/mirror-left-v2';OUT.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();baseline=HERE/'mirror-left-v1.blend';old=json.loads((ROOT/'creative/reviews/mirror-left-v1/source-geometry-check.json').read_text());assert sha(baseline)==old['source_sha256'];P=json.loads((HERE/'parameters-left.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(baseline));collection=bpy.data.collections['WEWA_MIRROR_LEFT'];construction=bpy.data.collections['LH mirror editable construction'];name='LH continuous steel stem ball and cosmetic stud - candidate';stem=bpy.data.objects[name];materials=list(stem.data.materials);mount=Vector(P['mount_boss_centre_world_m']);vertices,faces,method=make_stud(mount,pitch=P['stud_thread_pitch_working_m'])
def mesh(name,verts,faces,col):
 data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(data);bm.free();ob=bpy.data.objects.new(name,data);col.objects.link(ob);return ob
def payload(ob):
 ob.data.calc_loop_triangles();return {'name':ob.name,'vertices':[list(ob.matrix_world@v.co)for v in ob.data.vertices],'triangles':[list(t.vertices)for t in ob.data.loop_triangles]}
stud=mesh('LH phase-aligned cosmetic stud construction v2 - estimated',vertices,faces,construction);rod=bpy.data.objects['LH continuous bent rod construction'];ball=bpy.data.objects['LH estimated steel articulation ball construction']
with tempfile.TemporaryDirectory(prefix='wewa-rh-stud-v3-')as t:
 inp=Path(t)/'in.json';out=Path(t)/'out.json';inp.write_text(json.dumps({'base':payload(rod),'features':[payload(stud),payload(ball)],'drills':[]}));subprocess.run([shutil.which('python'),str(HERE/'csg_worker.py'),str(inp),str(out)],check=True);result=json.loads(out.read_text())
replacement=mesh('LH replacement stem v3 construction',result['vertices'],result['triangles'],construction);stem.data=replacement.data;bpy.data.objects.remove(replacement,do_unlink=True)
for m in materials:stem.data.materials.append(m)
for f in stem.data.polygons:
 f.use_smooth=True;centre=sum((stem.data.vertices[i].co for i in f.vertices),Vector())/len(f.vertices);f.material_index=1 if centre.z<mount.z+.022 else 0
stem.data.set_sharp_from_angle(angle=.65);stem.data.update();uv=stem.data.uv_layers.new(name='Physical10mm dominant plane UV')
for f in stem.data.polygons:
 axis=max(range(3),key=lambda j:abs(f.normal[j]));sign=1 if f.normal[axis]>=0 else -1
 for li in f.loop_indices:
  co=stem.data.vertices[stem.data.loops[li].vertex_index].co;pair=(sign*co.y,co.z)if axis==0 else(-sign*co.x,co.z)if axis==1 else(sign*co.x,co.y);uv.data[li].uv=(pair[0]/.010,pair[1]/.010)
checks=[]
for ob in [stud]+[o for o in collection.all_objects if o.type=='MESH']:
 bm=bmesh.new();bm.from_mesh(ob.data);todo=set(bm.verts);count=0
 while todo:
  count+=1;stack=[todo.pop()]
  while stack:
   for edge in stack.pop().link_edges:
    for v in edge.verts:
     if v in todo:todo.remove(v);stack.append(v)
 ob.data.calc_loop_triangles();areas=[t.area for t in ob.data.loop_triangles];row={'object':ob.name,'vertices':len(bm.verts),'faces':len(bm.faces),'components':count,'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_m3':bm.calc_volume(signed=True),'triangles':len(areas),'exact_zero_area_triangles':sum(a==0 for a in areas),'minimum_triangle_area_m2':min(areas)};bm.free();assert count==1 and row['non_manifold_edges']==0 and row['volume_m3']>0 and row['exact_zero_area_triangles']==0,row;checks.append(row)
for o in construction.objects:o.hide_render=True;o.hide_set(True)
bpy.ops.object.select_all(action='DESELECT')
for o in collection.all_objects:o.select_set(True)
bpy.context.view_layer.objects.active=stem;export=HERE/'mirror-left-v2.glb';bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_apply=True,export_tangents=True);source=HERE/'mirror-left-v2.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
report=dict(old);report.update({'phase':'full v2 candidate; LH cosmetic stud mesh phase alignment only','source_sha256':sha(source),'export_sha256':sha(export),'prior_source_sha256':old['source_sha256'],'prior_export_sha256':old['export_sha256'],'geometry':[c for c in checks if c['object']!=stud.name],'new_stud_closed_geometry':checks[0],'change':{'only_changed_body':name,'sampling_method':method,'retained_original_rod_and_ball_objects':[rod.name,ball.name],'profile_and_dimensions_changed':False,'nine_other_source_bodies_or_transforms_edited':False,'materials_and_images_edited':False,'normals':'Intentional sharp slope boundaries derived from source mesh at existing threshold0.65rad; smooth within each patch. No global bevel.','limits':'Diameter, pitch, hand, crest/root form and mating fit remain estimated cosmetic geometry, not OEM qualification.'},'CSG_v2':{k:v for k,v in result.items()if k not in ['vertices','triangles']}});report.pop('inherited_CSG_from_v1_no_CSG_reexecuted',None);(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');P['source_revision']='mirror-left-v2';P['stud_sampling_v2']=method;P['unchanged_baseline']='mirror-left-v1';(HERE/'parameters-left-v2.json').write_text(json.dumps(P,indent=2)+'\n');assert sha(baseline)==old['source_sha256'];print('LH_STUD_V2_BUILD',report['source_sha256'],report['export_sha256'],checks[0])
