import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/wewa');O=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(O/'context-material-linked-v3.blend'));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();vs=[];fs=[]
for ins in dg.object_instances:
 if not ins.is_instance or ins.object.type!='MESH'or ins.object.hide_render:continue
 if not any(t in ins.object.name.lower()for t in ['frame','seatmember','lowercradle','central curved','diagonal strut']):continue
 ev=ins.object.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();base=len(vs);vs.extend(ins.matrix_world@v.co for v in me.vertices);fs.extend(tuple(base+i for i in t.vertices)for t in me.loop_triangles);ev.to_mesh_clear()
FB=BVHTree.FromPolygons(vs,fs,all_triangles=True);parts=[o for o in s.objects if o.type=='MESH'and o.get('side')];rows=[]
for ob in parts:
 row={'name':ob.name,'side':ob['side'],'part':ob['source_part'],'linked_original_mesh_library':bpy.path.abspath(ob.data.library.filepath)if ob.data.library else None,'all_materials_original_linked':all(m.library is not None for m in ob.data.materials),'determinant':ob.matrix_world.to_3x3().determinant()}
 if ob['source_part']=='stay':
  side='left'if ob['side']=='LH'else'right';p=json.loads((R/f'assets-src/moto-components/passenger-footrest-stay-{side}-v1/parameters.json').read_text())['shape_choices'];ends={}
  for kind in ['long','short']:
   c=list(map(Vector,p[kind+'_arm_bezier_source_m']));end=c[-1]+(c[-1]-c[-2]).normalized()*.001;point=ob.matrix_world@end;n=FB.find_nearest(point);ends[kind]={'actual_source_aperture_centre_world_m':list(point),'nearest_frame_surface_m':list(n[0]),'distance_m':n[3],'role_identified':False}
  row['terminal_gaps_to_frame']=ends
 else:
  if ob['source_part']=='peg':row['actual_peg_hinge_world_m']=list(ob.matrix_world@Vector((.012,0,0)))
 rows.append(row)
assert len(parts)==6 and all(r['linked_original_mesh_library']and r['all_materials_original_linked']and abs(r['determinant']-1)<1e-5 for r in rows)
frag=json.loads((O/'integration-fragment-v3.json').read_text());sources=[]
for r in frag['additions']:
 p=R/r['source'];actual=hashlib.sha256(p.read_bytes()).hexdigest();assert actual==r['sha256'];sources.append({'path':r['source'],'sha256':actual,'unchanged':True})
libs=[{'name':l.name,'raw_filepath':l.filepath,'parent':l.parent.name if l.parent else None}for l in bpy.data.libraries]
(O/'native-reopen-v3.json').write_text(json.dumps({'parts':rows,'source_invariance':sources,'libraries':libs,'scope':'Actual native material v3 reopened and depsgraph evaluated. Linked originals unchanged, six proper transforms; terminal gaps are open and no mounting bridge invented.','fit_qualified':False},indent=2));print('NATIVE_V3_PASS',json.dumps(rows))
