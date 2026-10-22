import bpy,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
O=Path(__file__).resolve().parent;R=O.parents[2]
bpy.ops.wm.open_mainfile(filepath=str(O/'context-material-linked.blend'));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();parts=list(bpy.data.collections['CURRENT_RDC_PASSENGER_SUPPORT_V5'].objects)
def tree(obs):
 vs=[];fs=[]
 for ob,M in obs:
  ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();base=len(vs);vs.extend(M@p.co for p in me.vertices);fs.extend(tuple(base+i for i in t.vertices)for t in me.loop_triangles);ev.to_mesh_clear()
 return BVHTree.FromPolygons(vs,fs,all_triangles=True),vs
structure=[];sns=[];skins=[]
for ins in dg.object_instances:
 if not ins.is_instance or ins.object.type!='MESH'or ins.object.hide_render:continue
 target=sns if ins.parent and ins.parent.original.name.startswith('SNS diagnostic')else skins if ins.object.name in ['LEFT_COVER_OUTER_SKIN','RIGHT_COVER_OUTER_SKIN']else structure;target.append((ins.object.original,ins.matrix_world.copy()))
assert len(structure)>=30 and len(sns)==28 and len(skins)==2
E,_=tree(structure);N,_=tree(sns);K,_=tree(skins);rows=[];pair=[]
for ob in parts:
 B,pv=tree([(ob,ob.matrix_world)]);ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();rows.append({'key':ob.name,'structure_case_exhaust_crossings':len(B.overlap(E)),'both_SNS_crossings':len(B.overlap(N)),'cover_skin_cut_crossings':len(B.overlap(K)),'vertices':len(me.vertices),'triangles':len(me.loop_triangles),'matrix_world':[list(r)for r in ob.matrix_world],'proper_determinant':ob.matrix_world.to_3x3().determinant(),'mesh_linked':bool(ob.data.library),'materials_linked':all(m.library for m in ob.data.materials)});ev.to_mesh_clear()
for side in ['LH','RH']:
 obs=[ob for ob in parts if ob.name.startswith(side)]
 for i,a in enumerate(obs):
  A,_=tree([(a,a.matrix_world)])
  for b in obs[i+1:]:B,_=tree([(b,b.matrix_world)]);pair.append({'a':a.name,'b':b.name,'crossings':len(A.overlap(B))})
assert len(parts)==8 and all(not r['structure_case_exhaust_crossings']and not r['both_SNS_crossings']and r['mesh_linked']and r['materials_linked']for r in rows)and all(not p['crossings']for p in pair)
(O/'collision-and-native-check.json').write_text(json.dumps({'parts':rows,'internal_pairs':pair,'structure_mesh_instances':len(structure),'SNS_mesh_instances':len(sns),'skin_mesh_instances':len(skins),'scope':'Actual complete native v5 reopened, old6 unchanged plus two changed stems. Skin intersections near concealed emergence retained as G5 limits, distinct from structure/SNS/part crossings.'},indent=2))
pins=json.loads((R/'assets-src/moto-components/passenger-support-current-rdc-v4/main-input-pins.json').read_text());A=R/'assets-src/moto-components/passenger-support-current-rdc-v4';checks=[{'path':r['path'],'unchanged':hashlib.sha256((A/r['path']).read_bytes()).hexdigest()==r['sha256']}for r in pins['files']];assert all(r['unchanged']for r in checks);(O/'v4-inputs-unchanged.json').write_text(json.dumps(checks,indent=2));print('V5_NATIVE_AUDIT',len(rows),[(r['key'],r['cover_skin_cut_crossings'])for r in rows if r['cover_skin_cut_crossings']])
