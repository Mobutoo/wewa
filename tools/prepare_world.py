"""Prepare a versioned gameplay derivative; source geographic files stay unchanged."""
from pathlib import Path
import json, math, heapq, hashlib
from shapely.geometry import LineString, Point, shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'WEWA_Developpement_Web/data/pilot'
OUTPUT = ROOT / 'app/public/world'
OUTPUT.mkdir(parents=True, exist_ok=True)
roads = json.loads((SOURCE/'road_centerlines.local.json').read_text())['features']
roads = [f for f in roads if str(f['properties'].get('layer') or '0') == '0' and not f['properties'].get('bridge') and not f['properties'].get('tunnel')]
lines = [shape(f['geometry']) for f in roads]
parts = unary_union(lines)
nodes, indices, segments = [], {}, []
def node(p):
    # Conversion from local EN to GLB X east, Z south. Sources are untouched.
    key = (round(p[0],2), round(-p[1],2))
    if key not in indices:
        indices[key] = len(nodes); nodes.append(list(key))
    return indices[key]
for line in parts.geoms:
    coords = list(line.coords)
    mid = line.interpolate(.5, normalized=True)
    owner = min(range(len(lines)), key=lambda i: lines[i].distance(mid))
    props = roads[owner]['properties']
    for a,b in zip(coords,coords[1:]):
        ai,bi=node(a),node(b)
        if ai == bi: continue
        segments.append({'a':ai,'b':bi,'name':props.get('name') or 'Rue de Gombe','width':props.get('width_m',6),'source_id':props['source_id'],'oneway':props.get('oneway')})
adj={i:[] for i in range(len(nodes))}
for segment in segments:
    a,b=segment['a'],segment['b']; length=math.dist(nodes[a],nodes[b])
    penalty=(1 if segment['name']!='Rue de Gombe' else 4)*(1 if segment['width']>=5 else 2)
    adj[a].append((b,length*penalty));adj[b].append((a,length*penalty))
def nearest(x,z,street=None):
    allowed={s[k] for s in segments if street is None or street in s['name'] for k in ['a','b']}
    return min(allowed,key=lambda i:math.dist(nodes[i],(x,z)))
def path(a,b):
    q=[(0,a)];dist={a:0};prev={}
    while q:
        cost,u=heapq.heappop(q)
        if u==b:break
        if cost!=dist[u]:continue
        for v,w in adj[u]:
            if cost+w < dist.get(v,math.inf):dist[v]=cost+w;prev[v]=u;heapq.heappush(q,(cost+w,v))
    if b not in dist: raise ValueError('Route is not connected')
    result=[b]
    while result[-1]!=a:result.append(prev[result[-1]])
    return list(reversed(result))
anchors=[nearest(140,-680,'Boulevard du 30 Juin'),nearest(600,-800,'Boulevard du 30 Juin'),nearest(660,-580,'Colonel Ebeya'),nearest(220,-445,'Colonel Ebeya')]
route=[]
for a,b in zip(anchors,anchors[1:]+anchors[:1]):route.extend(path(a,b)[:-1])
route_points=[nodes[i] for i in route]+[nodes[route[0]]]
total=sum(math.dist(a,b) for a,b in zip(route_points,route_points[1:]))
def along(distance):
    distance%=total
    for a,b in zip(route_points,route_points[1:]):
        length=math.dist(a,b)
        if distance<=length:
            t=distance/length
            return [round(a[0]+(b[0]-a[0])*t,2),round(a[1]+(b[1]-a[1])*t,2)]
        distance-=length
    return route_points[0]
footprints=json.loads((SOURCE/'building_footprints.local.json').read_text())['features']
buildings=[]
for f in footprints:
    props=f['properties'];geom=f['geometry']
    polygons=geom['coordinates'] if geom['type']=='MultiPolygon' else [geom['coordinates']]
    for polygon in polygons:
        rings=[[[round(x,2),round(-y,2)] for x,y in ring] for ring in polygon]
        buildings.append({'id':props['source_id'],'rings':rings,'height':props['height_m'],'estimate':props['height_method']})
manifest=json.loads((SOURCE/'world_manifest.json').read_text())
# Copy existing, traced GLBs instead of rebuilding the imported city.
import shutil
for source in (SOURCE/'cells').glob('*.glb'):
    (OUTPUT/'cells').mkdir(exist_ok=True);shutil.copy2(source,OUTPUT/'cells'/source.name)
data={'version':1,'source':'OpenStreetMap / supplied Gombe pilot','axes':'X east, Y up, Z south; metres','nodes':nodes,'segments':segments,'route':route_points,'route_length':round(total,2),'spawn':along(0),'parcels':[{'id':f'parcel-{i}','point':along(d)} for i,d in enumerate([34,79,131,258,352,449,570,710,870])],'depots':[{'id':'depot-1','point':along(185),'label':'Chez Mado'},{'id':'depot-2','point':along(610),'label':'Relais du quartier'}],'buildings':buildings,'cells':manifest['cells'],'origin':manifest['origin_wgs84']}
(OUTPUT/'gombe.json').write_text(json.dumps(data,separators=(',',':'),ensure_ascii=False))
report={'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.glob('*.json')},'route_length_m':round(total,2),'route_nodes':len(route_points),'segments':len(segments),'source_buildings':len(buildings),'adaptations':['Coordinates transformed from EN to X/Z; rounded to centimetres in gameplay derivative','At-grade road intersections split into a prototype graph; full direction and priority rules remain to be reviewed','Mission locations and route are fictional gameplay placements on sourced road geometry'],'physical_geography_review':'pending user review','initial_anchor_points':anchors}
(ROOT/'WEWA_Developpement_Web/validation/gameplay-route.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='source_sha256'}))
