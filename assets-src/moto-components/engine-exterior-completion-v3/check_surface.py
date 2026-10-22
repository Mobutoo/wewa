import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(O/'diagnostic-linked-v3.blend'));bpy.context.view_layer.update();meshes={'before':([],[]),'after':([],[]),'cylinder':([],[]),'shell':([],[])}
for inst in bpy.context.evaluated_depsgraph_get().object_instances:
 ob=inst.object
 if ob.type!='MESH' or 'head hollow' in ob.name:continue
 cylinder='cylinder finned' in ob.name
 new=ob.name.startswith('UPPER_REAR_CRANKCASE')
 me=ob.to_mesh();me.calc_loop_triangles()
 for state in ['before','after','cylinder','shell']:
  if state=='cylinder' and not cylinder:continue
  if state=='shell' and not new:continue
  if state in ['before','after'] and cylinder:continue
  if state=='before' and new:continue
  vs,ts=meshes[state];off=len(vs);vs.extend(inst.matrix_world@v.co for v in me.vertices);ts.extend(tuple(off+i for i in t.vertices) for t in me.loop_triangles)
 ob.to_mesh_clear()
trees={k:BVHTree.FromPolygons(v,t,all_triangles=True) for k,(v,t) in meshes.items()}
rows=[]
for x,y in [(0,.22),(0,.265),(0,.31),(.06,.265),(-.06,.265)]:
 row=dict(origin=[x,y,-.48],direction=[0,0,-1])
 for state in ['before','after']:
  tree=trees[state]
  loc,n,i,d=tree.ray_cast(Vector(row['origin']),Vector(row['direction']),.4);row[state]=dict(hit=loc is not None,location=list(loc) if loc else None,distance=d)
 rows.append(row)
assert all(r['after']['hit'] and r['after']['location'][2]>-.58 for r in rows)
contacts=[]
for x,y in [(0,.078),(.025,.078),(-.025,.078),(0,.09)]:
 bottom=trees['cylinder'].ray_cast(Vector((x,y,-.62)),Vector((0,0,1)),.2)[0]
 deck=trees['shell'].ray_cast(Vector((x,y,-.50)),Vector((0,0,-1)),.2)[0]
 overlap=deck.z-bottom.z if bottom and deck else None
 contacts.append(dict(x=x,y=y,cylinder_bottom=list(bottom) if bottom else None,shell_top=list(deck) if deck else None,overlap_m=overlap))
assert all(c['overlap_m'] is not None and 0<c['overlap_m']<.025 for c in contacts),contacts
(O/'cylinder-foot-contact.json').write_text(json.dumps(contacts,indent=2))
(O/'actual-before-after-surface-rays.json').write_text(json.dumps(dict(scope='Evaluated crankcase/covers, cylinder and head excluded to isolate the missing case deck',rays=rows),indent=2));print(rows)
