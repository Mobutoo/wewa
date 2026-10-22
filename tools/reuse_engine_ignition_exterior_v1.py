"""Recover original already documented plug/cap sources in their inherited compatible head-v3 datums."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];N='engine-ignition-exterior-reuse-v1';H=R/'assets-src/moto-components'/N;O=R/'creative/reviews'/N
for p in [H,O]:p.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';rows=[];points=[]
inputs=[('head-context','assets-src/moto-components/engine-head/engine-head-v3.blend','WEWA_ENGINE_HEAD',None),('engine-spark-plug-visible','assets-src/moto-components/engine-spark-cap/portable-source-v2/engine-spark-plug-v2-context-portable.blend','WEWA_ENGINE_SPARK_PLUG_EXTERIOR','assets-src/moto-components/engine-spark-plug/engine-spark-plug-v2-inspection.glb'),('engine-spark-cap-visible','assets-src/moto-components/engine-spark-cap/portable-source-v2/engine-spark-cap-v2-portable.blend','WEWA_ENGINE_SPARK_CAP','assets-src/moto-components/engine-spark-cap/engine-spark-cap-v2-inspection.glb')]
catalog=json.loads((R/'tools/motorcycle-lab/catalog.json').read_text())['assets']
for key in ['engine-filter-cap-v2','engine-tappet-cap','engine-ohc-cover','engine-ohc-stub']:
 row=catalog[key];inputs.append((key,'assets-src/moto-components/'+row['source'],row['collection'],'assets-src/moto-components/'+row['files'][0]))
for key,src,name,glb in inputs:
 with bpy.data.libraries.load(str(R/src),link=True)as(a,b):assert name in a.collections;b.collections=[name]
 col=b.collections[0];inst=bpy.data.objects.new(key,None);s.collection.objects.link(inst);inst.instance_type='COLLECTION';inst.instance_collection=col
 for ob in col.all_objects:
  if ob.type=='MESH'and not ob.hide_render:points.extend(ob.matrix_world@Vector(p)for p in ob.bound_box)
 if glb:rows.append(dict(key=key,source=src,sha256=sha(R/src),collection=name,selected_objects=[],translation_m=[0,0,0],rotation_degrees=[0,0,0],scale=[1,1,1],placement_status='Exact historical plug/cap datum, already provisionally aligned to unchanged head-v3; no new scale or deformation',glb=glb,glb_sha256=sha(R/glb)))
(O/'add-only-fragment.json').write_text(json.dumps(dict(additions=rows,scope='Six original documented engine exterior source groups missing from the global composition; no HT cable, hidden resistor or electrodes invented'),indent=2)+'\n')
bpy.context.view_layer.update();points=[]
for it in bpy.context.evaluated_depsgraph_get().object_instances:
 if it.is_instance and it.object.type=='MESH'and not it.object.hide_render:points.extend(it.matrix_world@Vector(p)for p in it.object.bound_box)
print('INSTANCE_BOUND_POINTS',len(points),flush=True);assert points
center=Vector([.5*(min(v[i]for v in points)+max(v[i]for v in points))for i in range(3)]);s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=800;s.render.resolution_y=600;s.world=bpy.data.worlds.new('Neutral');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.5
for name,offset,power in [('Key',(.4,-.4,.4),25),('Fill',(-.3,.1,.4),15)]:
 l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=.3;o=bpy.data.objects.new(name,l);s.collection.objects.link(o);o.location=center+Vector(offset);o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);s.camera=c;c.location=center+Vector((.4,-.5,.2));c.rotation_euler=(center-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=.3;c.data.clip_start=.001;c.data.clip_end=10;s.render.image_settings.file_format='PNG';s.render.filepath=str(O/'recovered-ignition-context.png');bpy.context.preferences.filepaths.save_version=0
for lib in bpy.data.libraries:lib.filepath=bpy.path.relpath(lib.filepath,start=str(H))
bpy.ops.wm.save_as_mainfile(filepath=str(H/'linked-ignition-context.blend'),compress=True);bpy.ops.render.render(write_still=True);(O/'render-report.json').write_text(json.dumps(dict(source_sha256=sha(H/'linked-ignition-context.blend'),samples=16,resolution=[800,600],png_sha256=sha(O/'recovered-ignition-context.png'),scope='New context proof only; original isolated96 source proofs unchanged',art_accepted=False),indent=2)+'\n')
