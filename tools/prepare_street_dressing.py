"""Place original Blender modules on immutable source footprints; authored dressing only."""
from pathlib import Path
import json,math,hashlib
from shapely.geometry import Polygon,Point,LineString
ROOT=Path(__file__).resolve().parents[1];public=ROOT/'app/public';w=json.loads((public/'world/gombe.json').read_text());kit=json.loads((public/'models/street-kit/manifest.json').read_text());assets={a['id']:a for a in kit['assets']}
route=w['route'];points=[route[0]];length=0
for a,b in zip(route,route[1:]):
 d=math.dist(a,b)
 if length+d>220:
  t=(220-length)/d;points.append([a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t]);break
 points.append(b);length+=d
corridor=LineString(points);polygons=[Polygon(b['rings'][0],b['rings'][1:]) for b in w['buildings']];families=['aged_office','tropical_apartment','retail_shutter','workshop','compound_gate','louvered_office'];facades=[];props=[];colliders=[]
def append_prop(asset,x,z,yaw,reason):
 if any(p.contains(Point(x,z)) for p in polygons):return
 placement={'asset':asset,'x':round(x,3),'y':0,'z':round(z,3),'yaw':round(yaw,6),'provenance':reason};props.append(placement)
 if asset in ['bench_wood','litter_bin','electrical_cabinet','concrete_planter','vendor_stall','wood_crate','portable_barrier','rail_fence_2m']:
  width,_,depth=assets[asset]['dimensions_m'];dx,dz=width/2,depth/2;ring=[[round(x+math.cos(yaw)*a+math.sin(yaw)*b,3),round(z-math.sin(yaw)*a+math.cos(yaw)*b,3)] for a,b in [(-dx,-dz),(dx,-dz),(dx,dz),(-dx,dz),(-dx,-dz)]];colliders.append({'id':f'dressing-{len(props)}','rings':[ring],'reason':reason})
for b,polygon in zip(w['buildings'],polygons):
 if corridor.distance(polygon)>65:continue
 family=families[int(hashlib.sha256(b['id'].encode()).hexdigest()[:6],16)%6];ring=b['rings'][0]
 for edge,(a,z) in enumerate(zip(ring,ring[1:])):
  d=math.dist(a,z)
  if d<3.4:continue
  dx,dz=(z[0]-a[0])/d,(z[1]-a[1])/d;nx,nz=dz,-dx;mid=Point((a[0]+z[0])/2,(a[1]+z[1])/2)
  if polygon.contains(Point(mid.x+nx*.15,mid.y+nz*.15)):nx,nz=-nx,-nz
  street=corridor.interpolate(corridor.project(mid))
  if (street.x-mid.x)*nx+(street.y-mid.y)*nz<1 or mid.distance(street)>72:continue
  columns=min(24,int(d/3.4));margin=(d-columns*3.4)/2
  for floor in range(min(40,int(b['height']/3))):
   for col in range(columns):
    offset=margin+(col+.5)*3.4;x=a[0]+dx*offset+nx*.10;zz=a[1]+dz*offset+nz*.10
    if corridor.distance(Point(x,zz))<1.6:continue
    facades.append({'asset':f'facade_{family}_{"ground" if floor==0 else "upper"}','x':round(x,3),'y':floor*3,'z':round(zz,3),'yaw':round(math.atan2(nx,nz),6),'source_id':b['id'],'source_edge':edge,'height_status':b['estimate'],'provenance':'Fictional bay fitted to source footprint; footprint and source height unchanged'})
# Curbs follow the source width, interrupted wherever another source road crosses them.
segments=[(s,LineString([w['nodes'][s['a']],w['nodes'][s['b']]])) for s in w['segments']]
for s in range(1,220):
 p=corridor.interpolate(s);p2=corridor.interpolate(s+.1);yaw=math.atan2(p2.x-p.x,p2.y-p.y);owner,line=min(segments,key=lambda e:e[1].distance(p));width=owner['width']
 for sign in [-1,1]:
  x=p.x+math.cos(yaw)*sign*(width/2+.15);z=p.y-math.sin(yaw)*sign*(width/2+.15)
  if any(e['source_id']!=owner['source_id'] and l.distance(Point(x,z))<e['width']/2+.5 for e,l in segments if l.distance(p)<20):continue
  append_prop('curb_1m',x,z,yaw+math.pi/2,'Source road-edge curb, original decorative geometry')
# Named furniture positions are deterministic; they do not alter the source roads.
cycle=['street_lamp','drain_grate_1m','rail_fence_2m','litter_bin','market_umbrella','vendor_stall','wood_crate','electrical_cabinet','bench_wood','concrete_planter','utility_pole','blank_signpost','bollard','open_drain_1m','shop_awning','portable_barrier','concrete_marker','paving_patch_1m','curb_corner']
for i in range(38):
 s=8+i*5.5;p=corridor.interpolate(s);p2=corridor.interpolate(s+.1);yaw=math.atan2(p2.x-p.x,p2.y-p.y);owner,_=min(segments,key=lambda e:e[1].distance(p));sign=1 if i%2 else -1;offset=owner['width']/2+(2.5 if cycle[i%len(cycle)] in ['vendor_stall','market_umbrella','bench_wood'] else 1.2);x=p.x+math.cos(yaw)*offset*sign;z=p.y-math.sin(yaw)*offset*sign
 if any(l.distance(Point(x,z))<e['width']/2+.5 for e,l in segments if l.distance(p)<20):continue
 append_prop(cycle[i%len(cycle)],x,z,yaw,'Fictional street furnishing outside source carriageways')
data={'version':1,'status':'authored_geometry_art_and_local_review_required','corridor_length_m':220,'source_footprints_unchanged':True,'library':'/models/street-kit/street-kit.glb','facades':facades,'props':props,'colliders':colliders}
(public/'world/dressing.json').write_text(json.dumps(data,separators=(',',':'),ensure_ascii=False));report={k:v for k,v in data.items() if k not in ['facades','props','colliders']};report.update(facade_instances=len(facades),prop_instances=len(props),colliders=len(colliders),unique_assets=sorted(set(p['asset'] for p in facades+props)))
(ROOT/'WEWA_Developpement_Web/validation/street-dressing.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
