import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');O=Path(__file__).resolve().parent;specs=[('hub','front-completion-p21-front-material-front10-v5/carrier-material.blend',['RELATED_FOUR_HOLE_CARRIER_FRONT_ENVELOPE']),('rear-axle','front-completion-p23-rear-axle-v2/rear-axle-gray.blend',['RELATED_PF131208_AXLE_OBSERVED_MOUTH_OPEN_REVIEW_CUT']),('front-axle','front-completion-p24-axle-material-v1/material.blend',['DJ151041_RELATED_EXTERNAL_AXLE_ESTIMATED']),('adjuster-lh','front-completion-p23-lh-adjuster-front10-v1/lh-adjuster-material.blend',None),('adjuster-rh','front-completion-p23-rh-adjuster-front10-v2/rh-adjuster-material.blend',None),('rear-rim','rear-rim/rear-rim-v1.blend',None),('swingarm','swingarm/body/swingarm-body-v1.blend',['Related swingarm welded body - estimated reconstruction']),('front-plate','front-brake-plate/front-brake-plate-v2.blend',None)]
rows=[]
for key,source,names in specs:
 p=R/'assets-src/moto-components'/source;bpy.ops.wm.open_mainfile(filepath=str(p));dg=bpy.context.evaluated_depsgraph_get();objects=[bpy.data.objects[n]for n in names] if names else [o for o in bpy.context.scene.objects if o.type=='MESH'and not o.hide_render and 'Plane'not in o.name and 'FLOOR'not in o.name];items=[]
 for ob in objects:
  ev=ob.evaluated_get(dg);me=ev.to_mesh();pts=[ob.matrix_world@v.co for v in me.vertices];me.calc_loop_triangles();items.append(dict(name=ob.name,matrix_world=[list(x)for x in ob.matrix_world],bounds=[[min(v[i]for v in pts)for i in range(3)],[max(v[i]for v in pts)for i in range(3)]],triangles=len(me.loop_triangles),properties={k:str(ob[k])for k in ob.keys()}));ev.to_mesh_clear()
 rows.append(dict(key=key,source='assets-src/moto-components/'+source,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),objects=items))
(O/'native-datums.json').write_text(json.dumps(rows,indent=2))
for r in rows:print(r['key'],[(o['name'],o['bounds'])for o in r['objects']])
