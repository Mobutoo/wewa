"""Exact linked component collection composition; no source mesh edits."""
import bpy,hashlib,json,sys,math
from pathlib import Path
from mathutils import Vector,Quaternion
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/rear-sns-rest-assembly-v2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();M=O/'exact-inputs-v2.json';j=json.loads(M.read_text())
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;rows=[]
for q in j['inputs']:
 path=R/q['source'];assert sha(path)==q['source_sha256'] and sha(R/q['GLB'])==q['GLB_sha256']
 with bpy.data.libraries.load(str(path),link=True) as (fr,to):
  assert q['collection'] in fr.collections;to.collections=[q['collection']]
 c=to.collections[0];s.collection.children.link(c);root=next(a for a in c.all_objects if a.name==q['root']);assert root.library is not None
 bpy.context.view_layer.update();obs=[]
 for ob in c.all_objects:
  if ob.type!='MESH':continue
  mesh=ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh();mesh.calc_loop_triangles();verts=[ob.matrix_world@v.co for v in mesh.vertices];bbox=[[min(v[k]for v in verts),max(v[k]for v in verts)]for k in range(3)]
  obs.append({'object':ob.name,'data_library':ob.data.library.filepath if ob.data.library else None,'world_matrix':[list(a)for a in ob.matrix_world],'vertices':len(mesh.vertices),'triangles':len(mesh.loop_triangles),'actual_world_bbox_m':bbox,'first_vertex_world_m':list(verts[0])});ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
 rows.append({**q,'objects':obs,'root_world_matrix':[list(a)for a in root.matrix_world]})
for lib in bpy.data.libraries:lib.filepath=bpy.path.relpath(bpy.path.abspath(lib.filepath),start=str(H))
w=bpy.data.worlds.new('SNS neutral studio world');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.13,.13,.13,1);w.node_tree.nodes['Background'].inputs[1].default_value=.4;s.world=w
for name,eye,power,size in [('Broad key',(.45,-.55,.6),65,.5),('Soft fill',(-.4,-.2,.1),30,.45),('Rim',(.2,.4,.45),55,.35)]:
 l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=size;o=bpy.data.objects.new(name,l);s.collection.objects.link(o);o.location=eye;o.rotation_euler=(Vector((0,0,.055))-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('SNS review camera',bpy.data.cameras.new('SNS review lens'));s.collection.objects.link(cam);s.camera=cam;cam.data.clip_start=.001;cam.data.clip_end=20;cam.data.dof.use_dof=False;cam.data.sensor_fit='HORIZONTAL';cam.data.sensor_width=36
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=12;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=1;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0;s.view_settings.gamma=1
layer=s.view_layers[0];layer.use_pass_normal=True;layer.use_pass_diffuse_color=True;layer.cycles.denoising_store_passes=True
source=H/'rear-sns-rest-assembly-v2.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),relative_remap=False)
libs=[]
for lib in bpy.data.libraries:
 assert lib.filepath.startswith('//');p=Path(bpy.path.abspath(lib.filepath));assert p.exists();libs.append({'relative_path':lib.filepath,'sha256':sha(p)})
report={'schema':1,'source_sha256':sha(source),'input_manifest_sha256':sha(M),'linked_libraries':libs,'input_geometry':rows,'geometry_edited':False,'materials_edited':False,'runtime_GLButility':'merge_exact_glbs_v1.mjs is independent from Blender linked source generation','installed_transform':None,'static_only':True,'art_accepted':False};(O/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('LINKED_EXACT_SNS',len(rows),source)
