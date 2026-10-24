"""Independently measure saved source geometry and preserve unaffected assemblies."""
import bpy,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REV=ROOT/'creative/reviews/under-tank-layout-v3'
def bounds(name):
 ob=bpy.data.objects[name];points=[o.matrix_world@v.co for o in [ob,*ob.children_recursive] if o.type=='MESH' for v in o.data.vertices]
 return {'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)]}
fixed=['PARENT [front-tyre]','PARENT [rear-tyre]','PARENT [chaincase-upper]','PARENT [chaincase-lower]','PARENT [headlamp-housing-v2]','PARENT [fuel-tank-shell]','PARENT [seat-envelope]','PARENT [engine-head-v3]','COMPLETION [central-crankcase]']
rows=[]
for stage,path in [('before','visual-proportions-v2/motorcycle-proportions.blend'),('after','under-tank-layout-v3/motorcycle-layout.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets-src/moto-components'/path));bpy.context.view_layer.update()
 tank=bounds('PARENT [fuel-tank-shell]');cover=bounds('PARENT [sidecover-LH]');bowl=bounds('PARENT [carburettor-float-bowl-v2]');shoulder=bounds('PROPORTIONS [upper-rear-crankcase-shoulder]')
 rows.append({'stage':stage,'tank_sidecover_profile_overlap_m':tank['max'][1]-cover['min'][1],'float_bowl_to_upper_casting_vertical_envelope_gap_m':bowl['min'][2]-shoulder['max'][2],'carb_float_bowl':bowl,'sidecover':cover,'fixed':{n:bounds(n) for n in fixed}})
assert rows[0]['fixed']==rows[1]['fixed']
assert abs(rows[1]['tank_sidecover_profile_overlap_m']-rows[0]['tank_sidecover_profile_overlap_m']-.075)<1e-6
assert abs(rows[1]['float_bowl_to_upper_casting_vertical_envelope_gap_m']-rows[0]['float_bowl_to_upper_casting_vertical_envelope_gap_m']+.035)<1e-6
fitted=json.loads((REV/'composition-check.json').read_text())['fitted_connections']
(REV/'measured-check.json').write_text(json.dumps({'measurements':rows,'unaffected_groups_unchanged':True,'fitted_source_bounds':{r['name']:bounds(r['name']) for r in fitted},'scope':'Profile overlap and vertical envelope gap only; not a physical clearance measurement.','tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n')
print('LAYOUT_MEASURED',[(r['stage'],r['tank_sidecover_profile_overlap_m'],r['float_bowl_to_upper_casting_vertical_envelope_gap_m']) for r in rows])
