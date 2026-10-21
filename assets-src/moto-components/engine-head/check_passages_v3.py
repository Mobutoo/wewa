"""Read-only evaluated casting holes/seat access, not certified engine gas flow."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];source=H/'engine-head-v3.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(source);P=json.loads((H/'parameters-v3.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(source));body=bpy.data.objects['Engine UG5 head hollow exterior casting - editable candidate'];tree=BVHTree.FromPolygons([v.co for v in body.data.vertices],[tuple(p.vertices)for p in body.data.polygons]);rows=[]
def probe(label,start,direction,length):
 a=Vector(start);d=Vector(direction).normalized();hit,n,idx,dist=tree.ray_cast(a,d,length);row={'label':label,'start_local_m':list(a),'direction_local':list(d),'tested_length_m':length,'first_surface_distance_m':dist,'clear':hit is None};rows.append(row);assert hit is None,row
for i,(x,y)in enumerate(P['stud_centres_xy_working_m']):
 for dx in[-.0015,0,.0015]:
  if i==0:probe('fourth upper access only lower connection unknown'+str(dx),(x+dx,y,.131),(0,0,-1),.104)
  else:probe('observed lower bore'+str(i+1)+' offset'+str(dx),(x+dx,y,-.010),(0,0,1),.135)
for i,(point,axis)in enumerate(zip(P['tappet_port_centres_local_m'],P['tappet_port_axes_local'])):
 p=Vector(point);a=Vector(axis);probe('tappet'+str(i+1)+' axial access',p+a*.043,-a,.070)
probe('OHC opening to upper casting space',(.090,0,.078),(-1,0,0),.068)
import math
for index in range(48):
 a=math.tau*index/48;probe('bearing seat clearance'+str(index),(.008,.0105*math.cos(a),.078+.0105*math.sin(a)),(1,0,0),.019)
probe('shared upper fork bore',(-.030,0,.131),(1,0,0),.060)
for i,sign in enumerate([-1,1]):
 axis=Vector((0,sign*.18,1)).normalized();centre=Vector((0,sign*.016,.016));probe('valve-port visible entrance'+str(i+1),centre-axis*.029,axis,.050)
for i,point in enumerate(P['intake_exhaust_seat_centres_local_m']):
 axis=Vector((0,-1 if i==0 else 1,0));probe('gas port exterior access'+str(i+1),Vector(point)+axis*.023,-axis,.052)
a=Vector((-1,0,.35)).normalized();probe('spark plug visible entry',Vector(P['spark_plug_seat_centre_working_m'])+a*.055,-a,.080)
for aperture in P['underside_v2']['new_apertures']:
 x,y=aperture['centre_xy_working_m'];probe('underside mouth'+aperture['id']+' visible depth',(x,y,-.003),(0,0,1),.019)
for y in[-.030,0,.030]:probe('elongated timing mouth at y'+str(y),(.055,y,-.003),(0,0,1),.019)
assert sha(source)==before;report={'component_id':'MOTO-ENGINE-HEAD-001','source_sha256':before,'actual_local_mesh_rays':rows,'scope':'Visible passage access/holes in simplified original casting candidate. Does not certify valves, cam clearance, real gas paths or OEM dimensions.','source_modified':False,'all_dimensions_estimated':True,'art_accepted':False};(R/'creative/reviews/engine-head-v3/passage-check.json').write_text(json.dumps(report,indent=2)+'\n');print('HEAD_PASSAGES',len(rows),'clear')
