import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/wewa');O=Path(__file__).resolve().parent
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.open_mainfile(filepath=str(O/'context-material-linked.blend'));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();parts=[ob for ob in s.objects if ob.type=='MESH'and ob.get('side')];P=Matrix(((0,1,0,0),(0,0,1,0),(1,0,0,0),(0,0,0,1)))

def soup(obs):
 vs=[];fs=[]
 for ob,m in obs:
  ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();base=len(vs);vs.extend(m@v.co for v in me.vertices);fs.extend(tuple(base+i for i in t.vertices)for t in me.loop_triangles);ev.to_mesh_clear()
 return vs,fs

def tree(obs):
 v,f=soup(obs);return BVHTree.FromPolygons(v,f,all_triangles=True),v,f

env=[];sns=[];snsroots=[]
for ob in s.objects:
 if ob.name.startswith('SNS diagnostic'):
  snsroots.append({'name':ob.name,'matrix_world':[list(v)for v in ob.matrix_world],'determinant':ob.matrix_world.to_3x3().determinant(),'native_Y_transverse_world':list(ob.matrix_world.to_3x3()@Vector((0,1,0))),'native_Z_longitudinal_world':list(ob.matrix_world.to_3x3()@Vector((0,0,1)))})
for ins in dg.object_instances:
 if not ins.is_instance or ins.object.type!='MESH'or ins.object.hide_render:continue
 target=sns if ins.parent and ins.parent.original.name.startswith('SNS diagnostic')else env;target.append((ins.object.original,ins.matrix_world.copy()))
EB,_,_=tree(env);SB,_,_=tree(sns);scan=[];choices={};chosenposes={}
for side in ['LH','RH']:
 sub=[o for o in parts if o['side']==side];anchor=Vector((-.006 if side=='LH'else .004,.239,.0195));locals={}
 for ob in sub:
  if ob['source_part']=='stay':local=Matrix.Identity(4)
  else:local=P.copy();local.translation=(anchor.x,.239,.0075 if ob['source_part']=='peg'else .0335)
  locals[ob.name]=local
 best=[]
 for clock in [75,90,105]:
  q=Matrix.Rotation(math.radians(clock),3,'X')@Matrix(((0,0,1),(-2**-.5,-2**-.5,0),(2**-.5,-2**-.5,0)))
  if side=='RH':q=q@Matrix(((-1,0,0),(0,1,0),(0,0,-1)))
  F=Matrix.Translation(anchor)@Matrix.Rotation(math.radians(-75 if side=='LH'else 75),4,'Y')@Matrix.Translation(-anchor)
  for x in ([.09,.12,.15]if side=='LH'else[-.105,-.14,-.18]):
   for y in [.62,.65]:
    for z in [-.555,-.535]:
     H=Vector((x,y,z));M=q.to_4x4();M.translation=H-q@anchor;ms={o.name:M@(Matrix.Identity(4)if o['source_part']=='stay'else F)@locals[o.name]for o in sub};PB,pv,_=tree([(o,ms[o.name])for o in sub]);ne=len(PB.overlap(EB));ns=len(PB.overlap(SB));row={'side':side,'clock_deg':clock,'hinge':list(H),'fold_deg':-75 if side=='LH'else 75,'frame_surface_intersections':ne,'sns_surface_intersections':ns};scan.append(row)
     if ne==0 and ns==0:
      # Closest surface gap diagnostic; source point sample, no minimum-distance certification.
      nearE=min(EB.find_nearest(p)[3]for p in pv[::max(1,len(pv)//3000)]);nearS=min(SB.find_nearest(p)[3]for p in pv[::max(1,len(pv)//3000)]);row['sampled_frame_distance_m']=nearE;row['sampled_sns_distance_m']=nearS
      # Prefer moderate source-to-source proximity and minimal change of main hinge guess.
      penalty=(H-Vector((.1 if side=='LH'else-.1,.65,-.555))).length+abs(clock-90)*.0002;row['selection_penalty']=penalty;best.append((penalty,row,ms))
 if not best:raise RuntimeError('No clean candidate '+side)
 _,row,ms=min(best,key=lambda t:t[0]);choices[side]=row;chosenposes.update(ms)
 for ob in sub:ob.matrix_world=ms[ob.name]
(O/'bounded-placement-scan-v3.json').write_text(json.dumps({'candidates':scan,'chosen':choices,'SNS_roots':snsroots,'scope':'Actual complete triangle surface intersections, proper rotations, no geometric deformation. Context donor envelope; no installed fit.'},indent=2))
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();checks=[]
for ob in parts:
 PB,pv,_=tree([(ob,ob.matrix_world)]);checks.append({'name':ob.name,'side':ob['side'],'part':ob['source_part'],'frame_surface_intersections':len(PB.overlap(EB)),'sns_surface_intersections':len(PB.overlap(SB)),'matrix_world':[list(r)for r in ob.matrix_world],'sampled_nearest_frame_m':min(EB.find_nearest(p)[3]for p in pv[::max(1,len(pv)//5000)]),'sampled_nearest_sns_m':min(SB.find_nearest(p)[3]for p in pv[::max(1,len(pv)//5000)])})
assert all(r['frame_surface_intersections']==0 and r['sns_surface_intersections']==0 for r in checks)
(O/'collision-audit-v3.json').write_text(json.dumps({'parts':checks,'chosen':choices,'SNS_roots':snsroots,'scope':'No surface triangle crossings against entire linked chassis including battery and both actual SNS; not solid-containment or mechanical mounting certification'},indent=2))
fragment=json.loads((O/'integration-fragment.json').read_text());byname={r['key']:r for r in fragment['additions']}
for ob in parts:byname[ob.name]['matrix_world']=[list(r)for r in ob.matrix_world]
fragment['status']='v3 clean rigid donor context; geometry surfaces clear, visual review pending';fragment['hinges_world_m']={k:r['hinge']for k,r in choices.items()};fragment['chosen_pose_hypotheses']=choices;fragment['bounds']={'LH_hinge_X_m':[.075,.17],'RH_hinge_X_m':[-.20,-.075],'hinge_Y_m':[.59,.71],'hinge_Z_m':[-.595,-.515],'clock_search_deg':[75,105],'method':'Depth not calibrated in RDC photos. Widened outboard donor envelope tested against actual estimated frame/battery/SNS; not a measured mounting station.'};fragment['notes']+=['Earlier clock75 alone and XY-only grid remain rejected. Independent RHS stay crosses estimated battery when forced inboard.','New v3 selects clean donor context, retaining all native source shape/gaps; fixing roles and exact RDC applicability remain unresolved.'];(O/'integration-fragment-v3.json').write_text(json.dumps(fragment,indent=2))
# Reopenable linked scene; pair collection contains only six local wrappers with linked original data.
bpy.ops.wm.save_as_mainfile(filepath=str(O/'context-material-linked-v3.blend'),compress=True,relative_remap=False)
bpy.ops.object.select_all(action='DESELECT')
for ob in parts:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(O/'passenger-pair-material-v3.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_animations=False,export_cameras=False,export_lights=False)
rows=[]
for ob in parts:
 ev=ob.evaluated_get(dg);me=ev.to_mesh();pts=[ob.matrix_world@v.co for v in me.vertices];rows.append({'name':ob.name,'bounds':[[min(v[i]for v in pts)for i in range(3)],[max(v[i]for v in pts)for i in range(3)]],'matrix_world':[list(r)for r in ob.matrix_world]});ev.to_mesh_clear()
(O/'native-evaluated-world-v3.json').write_text(json.dumps(rows,indent=2))
gray=bpy.data.materials.new('Passenger v3 neutral gray');gray.use_nodes=True;gray.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.25,.25,.25,1);gray.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.45
for ob in parts:
 ob.data=ob.data.copy()
 for i in range(len(ob.data.materials)):ob.data.materials[i]=gray
bpy.ops.export_scene.gltf(filepath=str(O/'passenger-pair-gray-v3.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_animations=False,export_cameras=False,export_lights=False)
s.view_layers[0].material_override=gray;bpy.ops.wm.save_as_mainfile(filepath=str(O/'context-gray-linked-v3.blend'),compress=True,relative_remap=False);print('CLEAN_V3',json.dumps(choices))
