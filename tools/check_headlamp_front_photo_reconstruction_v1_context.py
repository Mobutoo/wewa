from pathlib import Path
import bpy,json,math,hashlib
from mathutils import Matrix,Vector,Euler
from mathutils.bvhtree import BVHTree
R=Path('/workspace/wewa');O=R/'creative/reviews/headlamp-front-photo-reconstruction-v1';O.mkdir(parents=True,exist_ok=True)
p=R/'creative/reviews/whole-exterior-coverage-v20/linked-parents-check.json';inventory=json.loads(p.read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
def load(row):
 p=R/row['source'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
 with bpy.data.libraries.load(str(p),link=True) as (a,b):
  # Old selection wrappers exist in assembly only; these two rows use native collections.
  assert row['collection'] in a.collections,row['collection'];b.collections=[row['collection']]
 col=b.collections[0];bpy.context.scene.collection.children.link(col)
 rot=Euler(tuple(math.radians(x) for x in row['rotation_degrees']),'XYZ').to_matrix().to_4x4()
 pose=Matrix.Translation(Vector(row['translation_m']))@rot@Matrix.Diagonal(Vector((*row['scale'],1)))
 bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();result=[]
 for o in col.all_objects:
  if o.type!='MESH' or o.hide_render:continue
  ev=o.evaluated_get(deps);m=ev.to_mesh();v=[pose@o.matrix_world@p.co for p in m.vertices];pol=[list(p.vertices) for p in m.polygons]
  result.append({'name':o.name,'bvh':BVHTree.FromPolygons(v,pol),'min':[min(p[i] for p in v) for i in range(3)],'max':[max(p[i] for p in v) for i in range(3)]});ev.to_mesh_clear()
 return result

objects=[]
keys=['outer-glass-envelope-context','headlamp-housing-v2','headlamp-cowl','headlamp-front-protector-v2']
for key in keys:
 row=(json.loads((O/'integration-fragment.json').read_text())['replacements'][0] if key=='outer-glass-envelope-context' else next(r for r in inventory['parents'] if r['key']==key))
 for ob in load(row):ob['parent']=key;objects.append(ob)
results=[]
for x,z in [(.04,-.12),(.04,-.10),(.04,-.14),(-.04,-.12),(-.04,-.10),(-.04,-.14),(.02,-.075),(.055,-.12)]:
 hits=[]
 for ob in objects:
  loc,normal,face,dist=ob['bvh'].ray_cast(Vector((x,-.30,z)),Vector((0,1,0)))
  if loc is not None:hits.append({'parent':ob['parent'],'object':ob['name'],'hit_world_m':list(loc),'distance_m':dist,'front_normal_dot':normal.dot(Vector((0,-1,0))),'transparent_glazing':'VISIBLE_GLAZING' in ob['name']})
 hits.sort(key=lambda h:h['distance_m']);opaque=[h for h in hits if not h['transparent_glazing']]
 field=next((h for h in hits if 'ESTIMATED_CONCAVE' in h['object']),None)
 shell=next((h for h in hits if h['parent'] in ['headlamp-housing-v2','headlamp-cowl']),None)
 results.append({'origin':[x,-.30,z],'direction':[0,1,0],'ordered_hits':hits,'field_hit':field is not None,'field_before_housing_or_cowl':field is not None and(shell is None or field['distance_m']<shell['distance_m']),'first_opaque':opaque[0] if opaque else None})
contacts=[]
new=[o for o in objects if o['parent']=='outer-glass-envelope-context']
for a in new:
 for b in objects:
  if b['parent']!='outer-glass-envelope-context':
   pairs=a['bvh'].overlap(b['bvh']);contacts.append({'new':a['name'],'context':b['name'],'triangle_intersections':len(pairs)})
for i,a in enumerate(new):
 for b in new[i+1:]:
  if True:
   contacts.append({'new':a['name'],'other':b['name'],'triangle_intersections':len(a['bvh'].overlap(b['bvh']))})
report={'scope':'Actual evaluated source triangles and unchanged v20 housing/cowl/guard poses. Overlap tests surface crossings only, not physical fit certification.','rays':results,'contacts':contacts,'bounds':[{'name':o['name'],'parent':o['parent'],'min':o['min'],'max':o['max']} for o in objects],'all_field_hits_before_shell':all(x['field_before_housing_or_cowl'] for x in results),'exact_OEM':False}
(O/'context-ray-contact-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
