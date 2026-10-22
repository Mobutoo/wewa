from pathlib import Path
import json,math
O=Path(__file__).resolve().parent;S=json.loads((O/'spec.json').read_text());T=json.loads((O/'observed-traces.json').read_text());rows=[]
def distance(p,a,b):
 v=[b[i]-a[i]for i in range(2)];w=[p[i]-a[i]for i in range(2)];den=sum(t*t for t in v)
 u=max(0,min(1,sum(v[i]*w[i]for i in range(2))/den)) if den else 0
 return math.dist(p,[a[i]+u*v[i]for i in range(2)])
for r in T:
 q=S[r['side']];k=q['scale_m_per_px'];u,v=q['rear_axle_px'];sign=1 if r['side']=='LH'else-1
 px=[[u+sign*(p[1]-.865)/k,v-(p[2]+.74)/k]for p in r['actual_sweep_centres_m']];poly=[p[:2]for p in r['pixel_depth_samples']];errors=[min(distance(p,a,b)for a,b in zip(poly,poly[1:]))for p in px]
 rows.append({'key':r['name'],'maximum_rounded_centreline_deviation_from_observed_working_polyline_px':max(errors),'RMS_deviation_px':(sum(e*e for e in errors)/len(errors))**.5,'source_point_uncertainty_px':6,'pixel_span':[min(p[0]for p in px),max(p[0]for p in px)],'warning':'Mapping is working WB/profile projection, not calibrated lens/3D/photo-fit proof.'})
(O/'trace-projection-check.json').write_text(json.dumps({'traces':rows,'all_within_trace_point_allowance':all(r['maximum_rounded_centreline_deviation_from_observed_working_polyline_px']<=6 for r in rows)},indent=2));print([(r['key'],round(r['maximum_rounded_centreline_deviation_from_observed_working_polyline_px'],3))for r in rows])
