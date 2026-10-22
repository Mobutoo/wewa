import bpy,json,hashlib
from pathlib import Path
R=Path('/workspace/wewa');D=Path(__file__).resolve().parent;rows=[]
for rel in ['assets-src/moto-components/cockpit-cables/cockpit-cables-v3.blend','assets-src/moto-components/p29-lower-front-sheath-observed-a-v1/sheath-material.blend']:
 p=R/rel;bpy.ops.wm.open_mainfile(filepath=str(p));objects=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or ('sheath'not in o.name.lower()):continue
  pts=[o.matrix_world@v.co for v in o.data.vertices];objects.append({'name':o.name,'vertices':len(pts),'bounds':[[min(v[k]for v in pts)for k in range(3)],[max(v[k]for v in pts)for k in range(3)]],'matrix_world':[list(row)for row in o.matrix_world],'properties':{k:str(v)for k,v in o.items()}})
 rows.append({'source':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'objects':objects})
(D/'native-comparison.json').write_text(json.dumps({'sources':rows,'historical_B_to_observed_B_mapping_proven':False,'reason':'Old labelled curves have no demonstrated source-pixel/endpoint bijection to the higher currentRDC hub run; labels do not establish brake/speedometer function. NewA explicitly covers lower current run, newB source trace independently read from other upper hub-side run.','newB_not_historical_replacement_or_pair_copy':True,'old_source_unchanged':True},indent=2)+'\n')
