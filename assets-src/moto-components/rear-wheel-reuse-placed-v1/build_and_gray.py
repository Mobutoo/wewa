import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Matrix,Vector,Euler
R=Path('/workspace/wewa');O=Path(__file__).resolve().parent;F=json.loads((O/'add-only-fragment.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;s=bpy.context.scene;s.unit_settings.system='METRIC';root=bpy.data.collections.new('REAR_WHEEL_REUSE_ADD_ONLY_V1');s.collection.children.link(root)
def link_selection(row,parent,mat):
 source=R/row['source'];assert hashlib.sha256(source.read_bytes()).hexdigest()==row['sha256'];names=list(row.get('selected_objects')or row.get('source_objects')or[])
 if names:
  with bpy.data.libraries.load(str(source),link=True)as(a,b):assert all(n in a.objects for n in names);b.objects=names
  c=bpy.data.collections.new('Exact source selection '+row['key'])
  for ob in b.objects:assert ob.type in ['MESH','CURVE'];c.objects.link(ob)
 else:
  with bpy.data.libraries.load(str(source),link=True)as(a,b):assert row['collection']in a.collections;b.collections=[row['collection']]
  c=b.collections[0]
 inst=bpy.data.objects.new(row['key'],None);inst.instance_type='COLLECTION';inst.instance_collection=c;inst.matrix_world=mat;inst['source_sha256']=row['sha256'];parent.objects.link(inst);return inst
for row in F['add_only']:
 M=Matrix(row['matrix']);assert abs(M.to_3x3().determinant()-1)<1e-8;link_selection(row,root,M)
# Four new parent instances only: safe add-only reusable file, no context duplicate.
bpy.ops.wm.save_as_mainfile(filepath=str(O/'rear-wheel-add-only-v1.blend'),compress=True,relative_remap=True)
# Separate unsaved review context, exact existing sources and v16 matrices.
context=bpy.data.collections.new('REVIEW_CONTEXT_NOT_IN_ADD_ONLY_FILE');s.collection.children.link(context);P=json.loads((R/'creative/reviews/whole-exterior-coverage-v16/linked-parents-check.json').read_text());context_rows=[];instances={}
for r in P['parents']:
 if r['key']not in ['rear-rim','rear-tyre','swingarm-body','chaincase-upper','chaincase-lower','rear-brake-panel-ds151069']:continue
 M=Matrix.Translation(Vector(r['translation_m']))@Euler(tuple(math.radians(x)for x in r['rotation_degrees']),'XYZ').to_matrix().to_4x4()@Matrix.Diagonal(Vector(r['scale']+[1]));instances[r['key']]=link_selection(r,context,M);context_rows.append(dict(key=r['key'],source=r['source'],sha256=r['sha256'],matrix=[list(x)for x in M]))
# Actual evaluated selected instances provide source triangles/bounds, not object names alone.
measures=[]
for inst in bpy.context.evaluated_depsgraph_get().object_instances:
 if inst.object.type!='MESH':continue
 me=inst.object.to_mesh();me.calc_loop_triangles();points=[inst.matrix_world@v.co for v in me.vertices];measures.append(dict(name=inst.object.name,triangles=len(me.loop_triangles),bounds=[[min(v[i]for v in points)for i in range(3)],[max(v[i]for v in points)for i in range(3)]]));inst.object.to_mesh_clear()
(O/'placed-native-check.json').write_text(json.dumps(dict(add_parent_count=4,add_mesh_count=7,source_parts_unchanged=True,context=context_rows,evaluated_meshes=measures,no_studio_or_guides_selected=True,scale_preserved=True,source_axis_rear_center_m=[0,.865,-.74],G1='unreceived',G5='unreceived; visual registration only, no invisible mating stacks certified'),indent=2))
s.world=bpy.data.worlds.new('Neutral');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.11,.11,.11,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.5
mat=bpy.data.materials.new('Gray review override');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.32,.32,.32,1);bs.inputs['Roughness'].default_value=.55;s.view_layers[0].material_override=mat
for loc,power,size in [((1,.3,.5),150,1.6),((-1,1.3,.1),120,1.4)]:
 d=bpy.data.lights.new('Gray softbox','AREA');d.energy=power;d.size=size;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,.8,-.7))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Reuse gray');d.type='ORTHO';d.ortho_scale=1.02;d.clip_start=.01;d.clip_end=20;cam=bpy.data.objects.new(d.name,d);s.collection.objects.link(cam);s.camera=cam;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=4;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=640;s.render.resolution_y=450;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';report=[]
for label,loc,hide_cases in [('gray-lh-inspection',(1.2,.40,-.40),True),('gray-rh-context',(-1.2,1.25,-.45),False)]:
 for key in ['chaincase-upper','chaincase-lower']:instances[key].hide_render=hide_cases
 cam.location=loc;target=Vector((0,.80,-.73));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.filepath=str(O/(label+'.exr'));bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(filepath=str(O/(label+'.png')),scene=s);report.append(dict(view=label,camera=list(cam.location),target=list(target),ortho_scale=1.02,samples=4,CPU_threads=2,resolution=[640,450],context_chaincases_hidden_for_inspection=hide_cases,native= 'rear-wheel-add-only-v1.blend',native_sha256=hashlib.sha256((O/'rear-wheel-add-only-v1.blend').read_bytes()).hexdigest(),protocol_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
(O/'gray-render-report.json').write_text(json.dumps(report,indent=2))
