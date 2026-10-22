"""OBB separating-axis refinement of conservative AABB pairs; still no triangle collision claim."""
from pathlib import Path
import json,math,itertools
D=Path(__file__).resolve().parent;R=D.parents[2];N=R/'creative/research/powertrain-native-assembly-evidence-v1';j=json.loads((D/'report.json').read_text());sources={e['id']:e for f in ['native-coordinate-read.json','intake-native-coordinate-read.json']for e in json.loads((N/f).read_text())['parents']}
dot=lambda a,b:sum(x*y for x,y in zip(a,b));sub=lambda a,b:[x-y for x,y in zip(a,b)];norm=lambda a:math.sqrt(dot(a,a));cross=lambda a,b:[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
boxes={}
for k,t in j['transforms'].items():
 b=sources[k]['component_bounds_m'];c=[(b['min'][i]+b['max'][i])/2 for i in range(3)];boxes[k]=dict(centre=[dot(t['R'][i],c)+t['t'][i]for i in range(3)],half=[(b['max'][i]-b['min'][i])/2 for i in range(3)],axes=[[t['R'][i][d]for i in range(3)]for d in range(3)])
rows=[]
for pair in j['aabb_possible_overlaps']:
 a,b=boxes[pair['a']],boxes[pair['b']];axes=[*a['axes'],*b['axes'],*[cross(x,y)for x in a['axes']for y in b['axes']]];tested=[]
 for ax in axes:
  size=norm(ax)
  if size<1e-10:continue
  ax=[x/size for x in ax];gap=abs(dot(sub(a['centre'],b['centre']),ax))-sum(h*abs(dot(v,ax))for h,v in zip(a['half'],a['axes']))-sum(h*abs(dot(v,ax))for h,v in zip(b['half'],b['axes']));tested.append((gap,ax))
 gap,ax=max(tested,key=lambda x:x[0]);rows.append(dict(a=pair['a'],b=pair['b'],verdict='SEPARATED_SOURCE_BOUND_BOXES'if gap>1e-9 else'BOUND_BOX_CONTACT_OR_OVERLAP_ONLY',maximum_axis_separation_m=gap,separating_or_least_overlap_axis_world=ax,note='Positive separation proves disjoint geometry contained in these bounds; overlapping boxes do not prove material/triangle collision.'))
sl=sources['engine-intake-sleeve']['component_bounds_m'];lower=sources['carburettor-lower-body-v2']['component_bounds_m'];bowl=sources['carburettor-float-bowl-v2']['component_bounds_m'];extra=[dict(id='FULL_SLEEVE_PROJECTIONS',status='REVIEW_GAPS_ARE_NOT_WHOLE_BODY_CLEARANCE',sleeve_native_Z_minmax_m=[sl['min'][2],sl['max'][2]],placed_axial_station_minmax_m=[.0195+sl['min'][2],.0195+sl['max'][2]],rear_extension_beyond_manifold_mouth_m=-(.0195+sl['min'][2]),front_extension_past_carb_neck_m=.0195+sl['max'][2]-.039,note='Rear/front appendages extend beyond the nominal35mm mouth planes. Two2mm gaps describe mouth centres/planes only. Full bounds require spatial review; no blanket collision-free claim.'),dict(id='LOWER_BOWL_ACTUAL_BOUND_GAP',status='PRESERVED_NATIVE_SECTION_UNQUALIFIED',positive_separation_along_common_local_X_m=bowl['min'][0]-lower['max'][0],nominal_mouth_control_station_difference_m=.003,note='Common rotation preserves actual bound separation ~0.314mm versus3mm nominal control stations. Neither equals measured gasket or fit clearance.')]
(D/'obb-refinement-and-full-envelope.json').write_text(json.dumps(dict(scope='Numeric bounds-only refinement, no whole scene/mesh loaded',aabb_pairs=len(rows),separated_by_OBB=sum(x['verdict']=='SEPARATED_SOURCE_BOUND_BOXES'for x in rows),remaining_bound_contacts_or_overlaps=sum(x['verdict']!='SEPARATED_SOURCE_BOUND_BOXES'for x in rows),pairs=rows,additional_findings=extra),indent=2)+'\n')
(D/'native-bounds-input-snapshot.json').write_text(json.dumps(dict(parents=[dict(id=k,native=sources[k]['native'],native_sha256=sources[k]['sha256'],bounds_source_world_m=sources[k]['component_bounds_m'])for k in j['transforms']],source_ports= json.loads((N/'intake-mouths-world.json').read_text())),indent=2)+'\n')
print(json.dumps(dict(OBB_separated=sum(x['verdict']=='SEPARATED_SOURCE_BOUND_BOXES'for x in rows),remaining_pairs=[(x['a'],x['b'])for x in rows if x['verdict']!='SEPARATED_SOURCE_BOUND_BOXES'],extra=extra)))
