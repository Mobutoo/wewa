"""Conforming interior grid clipped to original nonconvex outline, before bending."""
import json,math,hashlib
from pathlib import Path
import shapely
from shapely.geometry import Polygon,box
HERE=Path(__file__).resolve().parent;j=json.loads((HERE/'outline-v1.json').read_text());poly=Polygon(j['working_planar_outline_m']);assert poly.is_valid;verts=[];faces=[];keys={};covered=0;small=math.inf

def index(p):
 key=(round(p[0],12),round(p[1],12))
 if key not in keys:keys[key]=len(verts);verts.append([float(p[0]),float(p[1])])
 return keys[key]
loX,loY,hiX,hiY=poly.bounds;step=.004
for ix in range(math.floor(loX/step),math.ceil(hiX/step)):
 for iy in range(math.floor(loY/step),math.ceil(hiY/step)):
  cell=poly.intersection(box(ix*step,iy*step,(ix+1)*step,(iy+1)*step))
  if cell.is_empty:continue
  for t in shapely.get_parts(shapely.constrained_delaunay_triangles(cell)):
   if t.area<=0:continue
   covered+=t.area;small=min(small,t.area);coords=list(t.exterior.coords)[:-1];assert len(coords)==3;ids=[index(p)for p in coords];cross=(verts[ids[1]][0]-verts[ids[0]][0])*(verts[ids[2]][1]-verts[ids[0]][1])-(verts[ids[1]][1]-verts[ids[0]][1])*(verts[ids[2]][0]-verts[ids[0]][0]);faces.append(ids if cross>0 else list(reversed(ids)))
from collections import Counter
edges=Counter(tuple(sorted((a,b)))for f in faces for a,b in zip(f,f[1:]+f[:1]));boundary=[e for e,n in edges.items()if n==1];assert set(edges.values())<={1,2};assert abs(covered-poly.area)<1e-11;degree=Counter(i for e in boundary for i in e);assert set(degree.values())=={2};assert len(verts)-len(edges)+len(faces)==1
out={'schema':1,'outline_sha256':hashlib.sha256((HERE/'outline-v1.json').read_bytes()).hexdigest(),'grid_spacing_m':step,'vertices_2D_m':verts,'triangles':faces,'boundary_edges':boundary,'planar_area_m2':poly.area,'triangulated_area_m2':covered,'area_difference_m2':covered-poly.area,'minimum_triangle_area_m2':small,'vertices':len(verts),'triangles_count':len(faces),'boundary_vertices':len(degree),'Euler_disk':1,'source_geometry_policy':'Constrained triangulation separately inside shared grid cells, rounded shared index keys at1pm; original curve boundary retained. No large curved n-gon; actual 3D closure/area checked in Blender later.','art_accepted':False};(HERE/'planar-grid-v1.json').write_text(json.dumps(out,indent=2)+'\n');print('VISOR_PLANAR_GRID',len(verts),len(faces),len(boundary),small)
