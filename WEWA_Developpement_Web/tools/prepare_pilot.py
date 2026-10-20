"""Prepare georeferenced, untextured blockout cells. Not a game or final city.
Usage: python tools/prepare_pilot.py --source /path/Kit_Kinshasa_3D --out ./generated
Requires Shapely >=2.1 and pyproj. No network requests.
"""
import argparse, hashlib, json, math, re, struct
from pathlib import Path
from collections import Counter, defaultdict
import shapely
from shapely.geometry import shape, box, mapping
from shapely.geometry.polygon import orient
from shapely.ops import transform, unary_union
from pyproj import Transformer

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':')), encoding='utf8')

def polygons(g):
    if g.geom_type == 'Polygon': yield g
    elif hasattr(g, 'geoms'):
        for c in g.geoms: yield from polygons(c)

def scalar(value):
    # Complex values are deliberately not guessed.
    m=re.fullmatch(r'\s*(\d+(?:\.\d+)?)\s*(m)?\s*', str(value or ''))
    return float(m.group(1)) if m else None

def height(props):
    h=scalar(props.get('height'))
    if h and 1 <= h <= 300: return h, 'osm_height'
    n=scalar(props.get('building:levels'))
    if n and 0 < n <= 100: return n*3, 'estimated_levels_times_3m'
    return 6.0, 'placeholder_6m'

def glb(path, triangles, name, color):
    pos=[];norm=[]
    for tri in triangles:
        a,b,c=tri; u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
        n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        l=math.sqrt(sum(x*x for x in n))
        if l < 1e-8: continue
        for p in tri: pos.extend(p);norm.extend(x/l for x in n)
    if not pos: return 0
    positions=struct.pack('<'+'f'*len(pos),*pos); normals=struct.pack('<'+'f'*len(norm),*norm)
    binary=positions+normals;count=len(pos)//3
    model={'asset':{'version':'2.0','generator':'WEWA preproduction blockout 1.0','copyright':'© OpenStreetMap contributors; derived data ODbL; see CREDITS.txt'},
      'scene':0,'scenes':[{'nodes':[0]}], 'nodes':[{'mesh':0,'name':name}],
      'meshes':[{'primitives':[{'attributes':{'POSITION':0,'NORMAL':1},'material':0,'mode':4}]}],
      'materials':[{'name':'provisional_untextured','pbrMetallicRoughness':{'baseColorFactor':color,'metallicFactor':0,'roughnessFactor':1}}],
      'buffers':[{'byteLength':len(binary)}],
      'bufferViews':[{'buffer':0,'byteOffset':0,'byteLength':len(positions),'target':34962},{'buffer':0,'byteOffset':len(positions),'byteLength':len(normals),'target':34962}],
      'accessors':[{'bufferView':0,'componentType':5126,'count':count,'type':'VEC3','min':[min(pos[i::3]) for i in range(3)],'max':[max(pos[i::3]) for i in range(3)]},{'bufferView':1,'componentType':5126,'count':count,'type':'VEC3'}]}
    data=json.dumps(model,separators=(',',':')).encode(); data+=b' '*((-len(data))%4)
    binary+=b'\0'*((-len(binary))%4)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(struct.pack('<4sII',b'glTF',2,12+8+len(data)+8+len(binary))+struct.pack('<I4s',len(data),b'JSON')+data+struct.pack('<I4s',len(binary),b'BIN\0')+binary)
    return count//3

def build(source, output, bbox, cell_size):
    source=Path(source);output=Path(output);output.mkdir(parents=True,exist_ok=True)
    project=Transformer.from_crs(4326,32733,always_xy=True)
    ox,oy=project.transform(15.307,-4.310)
    def local(x,y,z=None): return (x-ox,y-oy)
    crop=box(*bbox);bounds=transform(local,transform(project.transform,crop)).bounds
    def metric(g): return transform(local,transform(project.transform,g))
    def xyz(p,h): return (float(p[0]),h,float(-p[1])) # right-handed glTF Y-up
    cells=defaultdict(lambda:{'b':[],'r':[],'metadata':[]});counts=Counter(); roads=[];features=[]
    for f in json.loads((source/'geodata/batiments.geojson').read_text())['features']:
        g=shape(f['geometry'])
        if not crop.intersects(g): continue
        if not g.is_valid: g=shapely.make_valid(g);counts['repaired_geometries']+=1
        g=metric(g.intersection(crop));props=f['properties'];h,method=height(props)
        if not g.is_empty:
            counts['building_features']+=1;counts[method]+=1
            features.append({'type':'Feature','geometry':mapping(g),'properties':{'source_id':f.get('id'),'height_m':h,'height_method':method,'name':props.get('name'),'building':props.get('building'),'building:part':props.get('building:part')}})
        for poly in polygons(g):
            if poly.area < .1: continue
            poly=orient(poly,sign=1.0);rp=poly.representative_point();key=(math.floor(rp.x/cell_size),math.floor(rp.y/cell_size));c=cells[key]
            c['metadata'].append({'id':f.get('id'),'bounds_en':list(poly.bounds),'height_m':h,'height_method':method,'holes':len(poly.interiors)})
            counts['polygon_parts']+=1;counts['interior_rings']+=len(poly.interiors)
            for t in shapely.constrained_delaunay_triangles(poly).geoms:
                pts=list(orient(t,sign=1).exterior.coords)[:3]
                c['b'].append([xyz(p,h) for p in pts]);c['b'].append([xyz(p,0) for p in reversed(pts)])
            for ring in [poly.exterior,*poly.interiors]:
                xy=list(ring.coords)
                for a,b in zip(xy,xy[1:]):
                    c['b'].extend([[xyz(a,0),xyz(b,0),xyz(b,h)],[xyz(a,0),xyz(b,h),xyz(a,h)]])
    drive={'trunk','primary','secondary','tertiary','trunk_link','primary_link','secondary_link','tertiary_link','residential','unclassified','living_street','service'}
    ribbons=[]
    for f in json.loads((source/'geodata/routes.geojson').read_text())['features']:
        props=f['properties']; g=shape(f['geometry'])
        if props.get('highway') not in drive or not crop.intersects(g):continue
        g=metric(g.intersection(crop))
        if g.is_empty:continue
        width=scalar(props.get('width'));method='osm_width'
        if not width or not 2<=width<=40:
            lanes=scalar(props.get('lanes'));width=lanes*3.2 if lanes and lanes<=10 else (10 if props['highway'] in {'trunk','primary','secondary'} else 6);method='design_width_estimate'
        roads.append({'type':'Feature','geometry':mapping(g),'properties':{'source_id':f.get('id'),'name':props.get('name'),'highway':props.get('highway'),'width_m':width,'width_method':method,'oneway':props.get('oneway'),'layer':props.get('layer'),'bridge':props.get('bridge'),'tunnel':props.get('tunnel')}})
        if props.get('bridge') in (None,'no') and props.get('tunnel') in (None,'no') and props.get('layer') in (None,'0'):
            ribbons.append(g.buffer(width/2,cap_style=2,join_style=2))
        else:counts['grade_separated_roads_not_meshed']+=1
    roads_surface=unary_union(ribbons).intersection(metric(crop))
    for ix in range(math.floor(bounds[0]/cell_size),math.floor(bounds[2]/cell_size)+1):
        for iz in range(math.floor(bounds[1]/cell_size),math.floor(bounds[3]/cell_size)+1):
            part=roads_surface.intersection(box(ix*cell_size,iz*cell_size,(ix+1)*cell_size,(iz+1)*cell_size))
            for poly in polygons(part):
                if poly.area < .01:continue
                for t in shapely.constrained_delaunay_triangles(poly).geoms:
                    cells[(ix,iz)]['r'].append([xyz(p,.03) for p in list(orient(t,sign=1).exterior.coords)[:3]])
    manifest=[]
    for (ix,iz),c in sorted(cells.items()):
        key=f'{ix}_{iz}';files=[]
        for kind,color in [('b',[.64,.62,.55,1]),('r',[.16,.18,.19,1])]:
            path=output/'cells'/f'{key}_{kind}.glb';n=glb(path,c[kind],key,color)
            if n:files.append({'path':str(path.relative_to(output)),'triangles':n,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        write_json(output/'cells'/f'{key}.json',{'buildings':c['metadata'],'note':'Cell ownership by representative point. Use actual GLB bounds for visibility; buildings may extend beyond nominal cell.'})
        manifest.append({'id':key,'grid_east_north':[ix,iz],'files':files,'metadata':f'cells/{key}.json'})
    counts['road_features']=len(roads);counts['cells']=len(manifest)
    counts['road_building_overlap_m2']=round(sum(shape(f['geometry']).intersection(roads_surface).area for f in features),2)
    common={'type':'FeatureCollection','coordinate_system':'LOCAL_EN_METRES_NOT_RFC7946_GEOJSON','origin_wgs84':[15.307,-4.310],'utm_origin':[ox,oy],'projection':'EPSG:32733'}
    write_json(output/'building_footprints.local.json',{**common,'features':features})
    write_json(output/'road_centerlines.local.json',{**common,'features':roads})
    write_json(output/'world_manifest.json',{'schema_version':1,'status':'blockout_only','bbox_wgs84':bbox,'origin_wgs84':[15.307,-4.310],'origin_utm':[ox,oy],'crs':'EPSG:32733','glb_axes':'X east, Y up, Z south; metres','terrain':'flat provisional','cell_m':cell_size,'counts':dict(counts),'cells':manifest,'limits':['Heights mostly placeholders; no facade textures or verified roof types','Ground flat; no terrain integration, sidewalk, traffic lane graph or gameplay','OSM overlaps and building parts preserved for audit; not deduplicated','Road widths estimated; crossings merged only for provisional ground surfaces','No browser import or performance benchmark performed']})
    print(json.dumps(dict(counts),ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True)
    p.add_argument('--bbox',nargs=4,type=float,default=[15.300,-4.317,15.315,-4.302]);p.add_argument('--cell',type=float,default=128)
    a=p.parse_args()
    if a.cell<=0 or a.bbox[0]>=a.bbox[2] or a.bbox[1]>=a.bbox[3]:p.error('Invalid cell or bbox')
    build(a.source,a.out,a.bbox,a.cell)
