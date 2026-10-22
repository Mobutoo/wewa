"""Bounded front axle length revision and rigid reuse of the documented front cam lever."""
import bpy,json,hashlib,math,re
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];N='front-wheel-exterior-completion-v2';H=R/'assets-src/moto-components'/N;O=R/'creative/reviews'/N;D=R/'creative/research'/N
for p in [H,O,D,O/'raw']:p.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# New isolated axial-envelope variant; retain original head/thread profile parameters.
old=R/'tools/front_completion_axle.py';text=old.read_text();mapping={'.205':'.225','.2045':'.2245','.185':'.205','.184':'.204','.18':'.20'}
# .18 in documented uncertainty interval must remain180mm.
text=re.sub(r'(?<![\w.])\.(?:2045|205|185|184|18)(?!\d)',lambda m:mapping[m[0]],text).replace("[.20,.24]","[.18,.24]")
text=text.replace("key='front-completion-p24-axle-v1'", "key='front-axle-envelope-v2'")
exec(compile(text,str(old)+' [225mm new revision]','exec'))
AH=R/'assets-src/moto-components/front-axle-envelope-v2';AO=R/'creative/reviews/front-axle-envelope-v2'
o=bpy.context.active_object;o.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.42,.43,.45,1);o.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value=.8;o.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.27
bpy.ops.wm.save_as_mainfile(filepath=str(AH/'axle-material.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(AH/'axle-material.glb'),export_format='GLB',use_selection=True,export_apply=True,export_tangents=False)
# Context and evaluated cam GLB are collocated in the new axle delivery H/O.
# Use the real visible source object, not the retained hidden reduced inspection object.
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';rows=[]
def link(key,src,names,M):
 with bpy.data.libraries.load(str(R/src),link=True)as(a,b):assert all(n in a.objects for n in names);b.objects=list(names)
 col=bpy.data.collections.new('CONTEXT ['+key+']')
 for ob in b.objects:col.objects.link(ob)
 inst=bpy.data.objects.new('FRONT_CONTEXT ['+key+']',None);s.collection.objects.link(inst);inst.instance_type='COLLECTION';inst.instance_collection=col;inst.matrix_world=M
 rows.append(dict(key=key,source=src,sha256=sha(R/src),selected_objects=names,collection=col.name,translation_m=list(inst.location),rotation_degrees=[math.degrees(v)for v in inst.rotation_euler],scale=list(inst.scale),matrix_world=[list(r)for r in M],placement_status='Bounded source-derived visible exterior placement; no certified mechanical fit'))
 return b.objects
I=Matrix.Identity(4);P=I.copy();P.translation=Vector((0,-.42,-1.03));link('front-brake-panel-context','assets-src/moto-components/front-brake-plate/front-brake-plate-v2.blend',['Front brake panel - editable casting'],P)
A=Matrix.Rotation(-math.pi/2,4,'Y');A.translation=Vector((.1125,-.42,-.74));link('front-axle-exterior-completion','assets-src/moto-components/front-axle-envelope-v2/axle-material.blend',['DJ151041_RELATED_EXTERNAL_AXLE_ESTIMATED'],A)
L=Matrix.Rotation(math.pi,4,'X');L.translation=Vector((.055,-.45,-.675));objs=link('front-brake-cam-lever-visible','assets-src/moto-components/front-brake-lever/front-brake-lever-v1.blend',['Front brake lever - editable candidate'],L)
# Export exact evaluated source object in its ORIGINAL frame to preserve the independent parent pose.
es=bpy.data.scenes.new('Exact lever export');oldscene=bpy.context.window.scene;bpy.context.window.scene=es
for ob in objs:es.collection.objects.link(ob)
bpy.ops.object.select_all(action='DESELECT')
for ob in objs:ob.select_set(True);bpy.context.view_layer.objects.active=ob
bpy.ops.export_scene.gltf(filepath=str(H/'front-cam-lever.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_tangents=False)
bpy.context.window.scene=oldscene
deps=bpy.context.evaluated_depsgraph_get();lever=objs[0].evaluated_get(deps);lm=lever.to_mesh();lever_min=min((L@lever.matrix_world@v.co).x for v in lm.vertices);lever.to_mesh_clear();panel_max=.052000106;assert lever_min>panel_max,(lever_min,panel_max);(D/'axial-clearance-check.json').write_text(json.dumps(dict(lever_min_x_m=lever_min,panel_global_max_x_m=panel_max,conservative_clearance_m=lever_min-panel_max,scope='Actual evaluated lever outward of maximum frozen panel plane; shaft/fasteners remain separate unresolved interfaces'),indent=2)+'\n')
adds=[r for r in rows if not r['key'].endswith('-context')];(O/'add-only-fragment.json').write_text(json.dumps(dict(additions=adds,glb_routes={adds[0]['key']:'assets-src/moto-components/front-axle-envelope-v2/axle-material.glb',adds[1]['key']:str((H/'front-cam-lever.glb').relative_to(R))}),indent=2)+'\n')
(D/'G0-G2-plan.json').write_text(json.dumps(dict(base_generator=str(old.relative_to(R)),base_generator_sha256=sha(old),new_axle_length_m=.225,length_bounds_m=[.18,.24],reason='Display shaft spans existing fork175mm centers and outer supports;225mm is an explicit assembly estimate, not measured OEM length',unchanged='Head, diameter, estimated20mm thread and pitch; source lever geometry/materials unchanged',related_sources=['assets-src/moto-components/front-brake-lever/reference-observations.json','assets-src/moto-components/front-completion-p24-axle-v1/parameters.json'],physical_axle_photo_actually_reopened=True,cam_axis_registration='Source JA panel(-.030,.250) plus front-wheel parent; existing lever shaft sourceZ.105; pure180deg X roll turns existing eye upward',cam_and_panel_bore_radii_m=[.0057,.0057],no_internal_cam_or_shoes_invented=True,art_accepted=False,mechanical_fit_accepted=False,rows=rows),indent=2)+'\n')
s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.device='CPU';s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=800;s.render.resolution_y=600;s.view_settings.view_transform='AgX';s.world=bpy.data.worlds.new('Neutral');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
center=Vector((0,-.43,-.74))
def aim(o):o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
for name,loc,power in [('Key',(.4,-.7,-.3),35),('Fill',(-.4,-.5,-.6),20)]:
 l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=.3;o=bpy.data.objects.new(name,l);s.collection.objects.link(o);o.location=loc;aim(o)
c=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(c);s.camera=c;c.data.type='ORTHO';c.data.ortho_scale=.34;c.data.clip_start=.001;c.data.clip_end=10;c.location=(.4,-.6,-.55);aim(c)
for lib in bpy.data.libraries:lib.filepath=bpy.path.relpath(lib.filepath,start=str(H))
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(H/'linked-front-context.blend'),compress=True)
views=[]
for name,eye in [('front-quarter',(.4,-.6,-.55)),('cam-side',(.4,-.43,-.74)),('axle-reverse',(-.4,-.65,-.55))]:
 c.location=eye;aim(c);s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(O/'raw'/(name+'.exr'));bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/(name+'.png')),scene=s);views.append(dict(name=name,samples=96,png_sha256=sha(O/(name+'.png')),exr_sha256=sha(O/'raw'/(name+'.exr'))));(O/'render-report.json').write_text(json.dumps(dict(source_sha256=sha(H/'linked-front-context.blend'),views=views),indent=2)+'\n')
