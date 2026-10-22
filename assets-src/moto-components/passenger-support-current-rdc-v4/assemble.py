import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=Path(__file__).resolve().parent;R=O.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda n,d:(O/n).write_text(json.dumps(d,indent=2)+'\n')
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;s=bpy.context.scene;s.unit_settings.system='METRIC'
ctx=R/'assets-src/moto-components/chassis-interior-completion-v1/kit-linked-v2.blend'
with bpy.data.libraries.load(str(ctx),link=True)as(a,b):b.objects=[n for n in a.objects if n.startswith(('COVERAGE_PARENT','OMITTED source','PROVISIONAL opposite','NEW children observed','SNS diagnostic'))]
for ob in b.objects:s.collection.objects.link(ob)
snsfile=R/'assets-src/moto-components/passenger-footrests-global-context-v2/context-material-linked-v3.blend'
with bpy.data.libraries.load(str(snsfile),link=True)as(a,b):b.objects=[n for n in a.objects if n.startswith('SNS diagnostic')]
for ob in b.objects:s.collection.objects.link(ob)
# Existing cases and exhaust in rigid v14 layout, documentary context only; main owns whole.
p=R/'assets-src/moto-components/whole-exterior-coverage-v14/whole-exterior-coverage-v14.blend';names=['COVERAGE_PARENT ['+k+']'for k in ['chaincase-upper','chaincase-lower','exhaust-silencer-body','exhaust-silencer-end','exhaust-heatshield','sidecover-LH','sidecover-RH-normalized','seat-envelope','rear-mudguard']]
with bpy.data.libraries.load(str(p),link=True)as(a,b):assert all(n in a.objects for n in names);b.objects=names
for ob in b.objects:s.collection.objects.link(ob)
group=bpy.data.collections.new('CURRENT_RDC_PASSENGER_SUPPORT_V4');s.collection.children.link(group);parts=[];rows=[]
for r in json.loads((O/'new-tube-identities.json').read_text()):r['source']=str((O/'current-rdc-observed-tubes.blend').relative_to(R));r['sha256']=sha(O/'current-rdc-observed-tubes.blend');rows.append(r)
rows+=json.loads((O/'peg-matrices.json').read_text())
for r in rows:
 with bpy.data.libraries.load(str(R/r['source']),link=True)as(a,b):b.objects=list(r['selected_objects'])
 for orig in b.objects:
  ob=orig.copy();ob.parent=None;ob.name=r['key'];group.objects.link(ob);from mathutils import Matrix;ob.matrix_world=Matrix(r['matrix_world']);ob['key']=r['key'];ob['source_file']=r['source'];ob['original_object']=r['selected_objects'][0];ob['side']=r.get('side','LH'if ob.name.startswith('LH')else'RH');ob['role']=r.get('role','tube');parts.append(ob)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
def soup(obs):
 vs=[];fs=[]
 for ob,m in obs:
  ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();base=len(vs);vs.extend(m@v.co for v in me.vertices);fs.extend(tuple(base+i for i in t.vertices)for t in me.loop_triangles);ev.to_mesh_clear()
 return vs,fs
def tree(obs):v,f=soup(obs);return BVHTree.FromPolygons(v,f,all_triangles=True),v
ctxparts=[];sns=[];snsroots=[]
for ob in s.objects:
 if ob.name.startswith('SNS diagnostic'):snsroots.append({'key':ob.name,'matrix_world':[list(r)for r in ob.matrix_world],'determinant':ob.matrix_world.to_3x3().determinant()})
for ins in dg.object_instances:
 if ins.is_instance and ins.object.type=='MESH'and not ins.object.hide_render:
  (sns if ins.parent and ins.parent.original.name.startswith('SNS diagnostic')else ctxparts).append((ins.object.original,ins.matrix_world.copy()))
assert len(ctxparts)>=30,('Incomplete frame context',len(ctxparts))
assert len(sns)>=20,('Incomplete SNS context',len(sns))
EB,_=tree(ctxparts);SB,_=tree(sns);checks=[];native=[]
for ob in parts:
 PB,pv=tree([(ob,ob.matrix_world)]);checks.append({'key':ob.name,'context_frame_case_exhaust_crossings':len(PB.overlap(EB)),'both_SNS_crossings':len(PB.overlap(SB)),'sampled_min_context_m':min(EB.find_nearest(v)[3]for v in pv[::max(1,len(pv)//5000)]),'sampled_min_SNS_m':min(SB.find_nearest(v)[3]for v in pv[::max(1,len(pv)//5000)]),'side':ob['side'],'matrix_world':[list(r)for r in ob.matrix_world]});native.append({'name':ob.name,'bounds':[[min(v[i]for v in pv)for i in range(3)],[max(v[i]for v in pv)for i in range(3)]],'matrix_world':[list(r)for r in ob.matrix_world]})
pair=[]
for side in ['LH','RH']:
 obs=[o for o in parts if o['side']==side]
 for i,a in enumerate(obs):
  A,av=tree([(a,a.matrix_world)])
  for b in obs[i+1:]:
   B,bv=tree([(b,b.matrix_world)]);pair.append({'a':a.name,'b':b.name,'surface_triangle_crossings':len(A.overlap(B)),'sampled_vertex_surface_distance_m':min(B.find_nearest(p)[3]for p in av[::max(1,len(av)//5000)])})
write('collision-audit.json',{'parts':checks,'internal_pairs':pair,'SNS_roots':snsroots,'context_mesh_instances':len(ctxparts),'SNS_mesh_instances':len(sns),'scope':'Actual evaluated triangle surface crossings and sampled distances only; no hidden mounting, solid-containment, contact or mechanical certification'})
write('native-evaluated-world.json',native)
old=json.loads((R/'assets-src/moto-components/passenger-footrests-global-context-v2/integration-fragment-v3.json').read_text())
fragment={'id':'passenger-support-current-rdc-v4','status':'observed source and initial rigid root poses ready; collision and visual review required','parents_to_remove':[r['key']for r in old['additions']],'removal_reason':'Replace both wrong-size PF donor stays and relocate their four common peg/rubber instances. Do not duplicate old v3.','convention':old['convention'],'additions':rows,'count':{'new_observed_tubes':4,'existing_common_peg_instances':2,'existing_common_rubber_instances':2,'total_mesh_instances':8,'donor_PF_stays':0},'nested':[],'main_source_collection':'CURRENT_RDC_PASSENGER_SUPPORT_V4','bounds':'spec.json','SNS_required_context':old['SNS_context_required'],'fit_qualified':False,'art_accepted':False,'source_identity':'Current RDC visible rear-sideguard/stay traces, no PF code imposed','limits':['No hidden pins, welds, brackets, endpoint continuations','Existing metal/JK geometry,22mm nominal overhang and90degree diagnostic cut unchanged','Old5mm chape gap belongs to preserved donor study; no new chape fabricated or installed pin claimed'],'source_photo_pixels_private':True}
write('integration-fragment.json',fragment)
# Small source from original/linked meshes; all 8 objects in one proper global collection.
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=12;s.cycles.use_denoising=True;s.cycles.denoising_use_gpu=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=800;s.render.resolution_y=640;s.render.resolution_percentage=100;s.view_layers[0].cycles.denoising_store_passes=True;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0;s.view_settings.gamma=1
world=bpy.data.worlds.new('Neutral uncalibrated current-RDC study');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.13,.13,.13,1);world.node_tree.nodes['Background'].inputs[1].default_value=.5;s.world=world
for name,loc,power in [('Key',(2,0,2),550),('Fill',(-2,1,1),450)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=2;ob=bpy.data.objects.new(name,data);s.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((0,.72,-.57))-ob.location).to_track_quat('-Z','Y').to_euler()
c=bpy.data.objects.new('Current RDC trace context camera',bpy.data.cameras.new('Current RDC trace context camera'));s.collection.objects.link(c);s.camera=c;c.data.type='ORTHO';c.data.ortho_scale=1.8;c.data.clip_start=.01;c.data.clip_end=30
bpy.ops.wm.save_as_mainfile(filepath=str(O/'context-material-linked.blend'),compress=True,relative_remap=False)
bpy.ops.object.select_all(action='DESELECT')
for ob in parts:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(O/'observed-support-material.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_animations=False,export_cameras=False,export_lights=False)
gray=bpy.data.materials.new('Neutral gray observed trace study');gray.use_nodes=True;gray.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.25,.25,.25,1);gray.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.45
for ob in parts:
 ob.data=ob.data.copy()
 for i in range(len(ob.data.materials)):ob.data.materials[i]=gray
bpy.ops.export_scene.gltf(filepath=str(O/'observed-support-gray.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_animations=False,export_cameras=False,export_lights=False)
s.view_layers[0].material_override=gray;bpy.ops.wm.save_as_mainfile(filepath=str(O/'context-gray-linked.blend'),compress=True,relative_remap=False)
print('FRAGMENT_AND_CONTEXT_READY',json.dumps(checks),json.dumps(pair))
