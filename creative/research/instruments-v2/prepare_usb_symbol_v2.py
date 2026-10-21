"""Original visible rectangular/oblique motif, private photo used as a guide only."""
from pathlib import Path
import json,hashlib
from shapely.geometry import LineString,Polygon
from shapely.geometry.polygon import orient
HERE=Path(__file__).resolve().parent;plan=json.loads((HERE/'usb-shape-plan.json').read_text());t=plan['working_shape_transform'];a=t['native_anchor_px'];sx=t['x_scale_m_per_px_estimated'];sy=t['y_scale_m_per_px_estimated'];c=t['local_face_anchor_m']
def xy(p):return[c[0]+(p[0]-a[0])*sx,c[1]+(p[1]-a[1])*sy]
curves=[[[479,365],[482,364.5],[487,364.5],[489,365]],[[489,365],[489.7,365.2],[490,366],[490,367]],[[490,367],[490,372],[490,379],[490,384]],[[490,384],[490,387],[488,389],[485,390]],[[485,390],[481,390],[478,388],[478,385]],[[478,385],[478,380],[478,373],[478,368]],[[478,368],[478,366],[478,365],[479,365]]];path=[]
for seg in curves:
 for k in range(32):
  t=k/32;path.append([sum(((1-t)**3,3*t*(1-t)**2,3*t*t*(1-t),t**3)[i]*seg[i][j]for i in range(4))for j in range(2)])
path.append(path[0]);zig=[[480.5,372],[486.3,376.8],[483.5,377.4],[488,383]];rows=[]
for name,points,width in [('observed rectangular outline',path,.00038),('observed oblique interior mark',zig,.00056)]:
 p=orient(LineString([xy(p)for p in points]).buffer(width/2,quad_segs=16,cap_style='round',join_style='round'),sign=1.0);assert p.is_valid and isinstance(p,Polygon);rows.append({'name':name,'stroke_width_m_estimated':width,'metric_outline_loops':[list(map(list,list(p.exterior.coords)[:-1]))]+[list(map(list,list(h.coords)[:-1]))for h in p.interiors],'visible_area_m2':p.area})
report={'schema':1,'reference_private_path':plan['reference_private_path'],'reference_sha256':plan['reference_sha256'],'reference_native_px':[1000,600],'native_symbol_box_approx':[477,364,492,391],'native_reading_uncertainty_px':3,'rectangle_native_bezier_segments':curves,'oblique_native_points':zig,'working_native_to_local_transform':plan['working_shape_transform'],'geometry_authorship':'Original smooth curves and buffered vector strokes, no documentary raster pixels in material','symbol_meaning':'unknown','manufacturing_process':'unknown; low-contrast surface marking representation is a render estimate, not a claim of actual paint/emboss/deboss','unresolved_details':'Fine internal horizontal marks and exact stroke count are not resolved; no extra generic USB trident or connector mechanics added','parts':rows,'art_accepted':False};(HERE/'usb-symbol-v2.json').write_text(json.dumps(report,indent=2)+'\n');print('USB_SYMBOL_VECTORS',len(rows))
