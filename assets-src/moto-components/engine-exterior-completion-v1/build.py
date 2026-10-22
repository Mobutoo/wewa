"""Conditional engine comparison, exact source geometry, no hidden closures."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Matrix,Vector
R=Path('/workspace/wewa');O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
I=json.loads((O/'interfaces.json').read_text());N=json.loads((O/'native-inventory.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.render.threads_mode='FIXED';s.render.threads=2
rows=[];objects=[]
def add(path,names,M,key,status):
 names=list(names);source_names=list(names);p=R/path
 with bpy.data.libraries.load(str(p),link=False) as (a,b):
  assert all(n in a.objects for n in names);b.objects=names
 for ob in b.objects:
  s.collection.objects.link(ob);ob.matrix_world=M@ob.matrix_world;ob.hide_select=False;ob.hide_render=False;ob.hide_viewport=False;ob.hide_set(False);ob['source_key']=key;objects.append(ob)
 rows.append(dict(key=key,source=path,sha256=sha(p),objects=source_names,matrix=[list(x) for x in M],status=status))
for row in I:
 if not row['objects']:continue
 add(row['source'],[o['name'] for o in row['objects']],Matrix.Identity(4),row['collection'],'exact inherited world pose; installed variant compatibility unqualified')
# Source profile X horizontal, Y up, Z inward; world X LH, Y aft, Z up.
# Cover split planes +/- .105m are read from actual native cover bounds.
# Conditional full depth stretches only axial direction to shared centre split, explicitly estimated.
for side in ['lh','rh']:
 row=next(x for x in N if 'crankcase-'+side+'-major' in x['source']);depth=.058 if side=='lh' else .068
 M=Matrix(((0,0,(1 if side=='lh' else -1)*.105/depth,(1 if side=='lh' else -1)*.105),(1 if side=='lh' else -1,0,0,.20 if side=='lh' else .22),(0,1,0,-.65 if side=='lh' else -.635),(0,0,0,1)))
 add(row['source'],row['objects'],M,'conditional-'+side,'estimated profile registration; independent BM150 donors, pairing and OEM fit NOT established')
# Service neck uses same LH photo coordinates (181,760), origin (350,550), scale .00044.
row=next(x for x in N if 'lower-service-port' in x['source']);M=Matrix(((0,0,1,.105),(1,0,0,.20+(181-350)*.00044),(0,1,0,-.65+(550-760)*.00044),(0,0,0,1)))
add(row['source'],row['objects'],M,'conditional-service-port','same documented LH specimen projection; axial seat and installed closure unknown, no plug invented')
for ob in objects:ob.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
# Evaluate source meshes explicitly, removing studio, hidden guides and unrelated construction.
expected=[]
clean_objects=[]
for ob in objects:
 dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);me=bpy.data.meshes.new_from_object(ev,depsgraph=dg);matrix=ob.matrix_world.copy();key=ob['source_key'];original_name=ob.name;bpy.data.objects.remove(ob,do_unlink=True);ob=bpy.data.objects.new(original_name,me);s.collection.objects.link(ob);ob.matrix_world=matrix;ob['source_key']=key;clean_objects.append(ob);me.calc_loop_triangles();expected.append(dict(name=ob.name,source_key=ob['source_key'],vertices=len(me.vertices),triangles=len(me.loop_triangles),bounds=[[min((ob.matrix_world@v.co)[i] for v in me.vertices) for i in range(3)],[max((ob.matrix_world@v.co)[i] for v in me.vertices) for i in range(3)]],materials=[m.name if m else None for m in me.materials]))
objects=clean_objects
s.world=bpy.data.worlds.new('Neutral world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.11,.11,.11,1)
s.world.node_tree.nodes['Background'].inputs[1].default_value=.5
for loc,power,size in [((1,-1,1),160,2),((-1,.2,.5),100,1.6),((0,1,0),80,1)]:
 d=bpy.data.lights.new('Engine softbox','AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,.17,-.55))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Engine comparison');cam=bpy.data.objects.new(d.name,d);s.collection.objects.link(cam);s.camera=cam;d.type='ORTHO';d.ortho_scale=.70;d.clip_start=.01;d.clip_end=20
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=96;s.cycles.use_denoising=True;s.render.resolution_x=720;s.render.resolution_y=640;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.render.image_settings.file_format='PNG'
(O/'poses-and-sources.json').write_text(json.dumps(dict(parents=rows,placement_bounds=dict(profile_translation_uncertainty_m=[-.035,.035],axial_split_position_uncertainty_m=[-.02,.02],axial_depth_scale_range=[1.3,2.1],rotation_uncertainty_degrees=[-12,12],method='native cover split planes +/-0.105; profile spans constrained by cover/cylinder bounds, not measured assembled donor; provisional same-exemplar copies authorized, no OEM equivalence'),parked=[dict(source=x['source'],reason='alternative subset already in major LH wall' if 'lower-peripheral-wall' in x['source'] else 'different photograph/donor frame; installed registration not established') for x in N if 'crankcase' in x['source'] and not any(r['source']==x['source'] for r in rows)],art_accepted=False,package_complete=False),indent=2))
(O/'sourcekit-preflight.json').write_text(json.dumps(dict(objects=expected,mesh_count=len(objects),triangles=sum(r['triangles'] for r in expected),unique_source_objects=len(set((r['source'],n) for r in rows for n in r['objects'])),old_covers_retained_once=True,covers_replaced=False,explanation='Donor bodies supplement removable covers; removing them would expose an unmodelled cavity. No newer cover revision exists among audited sources.',no_generic_fill=True,no_weld=True),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'engine-exterior-completion-v1.blend'),compress=True)
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(O/'engine-exterior-completion-v1.glb'),export_format='GLB',use_selection=True,export_apply=True,export_tangents=True,export_cameras=False,export_lights=False,export_extras=True)
# Frozen engine only. Whole motorcycle rendering remains with main.
(O/'render-plan.json').write_text(json.dumps(dict(samples=96,device='CPU',threads=2,resolution=[720,640],views=['left','right','quarter'],whole_render=False),indent=2))
