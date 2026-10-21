"""Explicit surface-edge construction domain, no bevel or Boolean.
The inner surface boundary is offset in the actual curved midsurface metric.
"""
import json,math,hashlib
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon,box
from shapely.validation import explain_validity
HERE=Path(__file__).resolve().parent;j=json.loads((HERE/'outline-v1.json').read_text());old=json.loads((HERE.parents[2]/'creative/reviews/instrument-visor-shell-study-v1/source-geometry-check.json').read_text());O=np.array(j['working_planar_outline_m']);V=np.array(old['frame']['up_V']);N=np.array(old['frame']['front_N']);U=np.array(old['frame']['U']);origin=np.array(old['frame']['origin_m']);k=.040/.125**2;r=.00025
# The fitted needle tips are below the native reading resolution. A tiny
# source fillet compatible with the rolled edge stays inside that uncertainty.
rounded=Polygon(O).buffer(-.0004,quad_segs=16).buffer(.0004,quad_segs=16).simplify(1e-7,preserve_topology=True)
assert rounded.is_valid and rounded.geom_type=='Polygon'
O=np.array(list(rounded.exterior.coords)[:-1])
if sum(O[i-1,0]*p[1]-p[0]*O[i-1,1]for i,p in enumerate(O))<0:O=O[::-1]
native=np.array(j['sampled_native_curve_px']);lo=native.min(0);hi=native.max(0);cx=(hi[0]+lo[0])/2
native_rounded=Polygon([(x/.250*(hi[0]-lo[0])+cx,hi[1]-t/.285*(hi[1]-lo[1]))for x,t in O])
from shapely.geometry import Point
annotation=json.loads((HERE.parents[2]/'creative/research/instrument-visor/bare-front-native-contour.json').read_text())
native_error=max(Point(*p).distance(native_rounded.boundary)for p in annotation['points_px'])
assert native_error<3
(HERE/'outline-rounded-v3.json').write_text(json.dumps({'original_outline_sha256':hashlib.sha256((HERE/'outline-v1.json').read_bytes()).hexdigest(),'working_planar_outline_m':O.tolist(),'tiny_tip_source_fillet_working_m':.0004,'source_curve_simplification_m':1e-7,'manual_native_points_max_distance_px':native_error,'manual_working_bound_px':3,'status':'Estimated source tip regularisation inside native uncertainty, not an OEM radius. Main C2 curve retained with small source circular G1 tip transitions. Buffer-arc sampling simplified by0.1um to remove redundant microscopic corners, far below native uncertainty.'},indent=2)+'\n')

def surface(p):return origin+U*p[0]+V*p[1]-N*k*p[0]**2

def normal(x):
 v=N+U*2*k*x;return v/np.linalg.norm(v)
C=[]
for i,p in enumerate(O):
 tangent=surface(O[(i+1)%len(O)])-surface(O[i-1]);tangent/=np.linalg.norm(tangent);inward=np.cross(normal(p[0]),tangent);inward/=np.linalg.norm(inward);fx=U-N*2*k*p[0];delta=np.array([np.dot(inward,fx)/np.dot(fx,fx),np.dot(inward,V)])*r;C.append(p+delta)
C=np.array(C);poly=Polygon(C);assert poly.is_valid,explain_validity(poly);verts=[];faces=[];keys={};covered=0;small=math.inf

def index(p):
 key=(round(p[0],12),round(p[1],12))
 if key not in keys:keys[key]=len(verts);verts.append([float(p[0]),float(p[1])])
 return keys[key]
loX,loY,hiX,hiY=poly.bounds;step=.004;phaseX=.00117;phaseY=.00191
for ix in range(math.floor((loX-phaseX)/step),math.ceil((hiX-phaseX)/step)):
 for iy in range(math.floor((loY-phaseY)/step),math.ceil((hiY-phaseY)/step)):
  cell=poly.intersection(box(phaseX+ix*step,phaseY+iy*step,phaseX+(ix+1)*step,phaseY+(iy+1)*step))
  if cell.is_empty:continue
  for t in shapely.get_parts(shapely.constrained_delaunay_triangles(cell)):
   if t.area<=0:continue
   covered+=t.area;small=min(small,t.area);ids=[index(p)for p in list(t.exterior.coords)[:-1]];assert len(ids)==3;cross=(verts[ids[1]][0]-verts[ids[0]][0])*(verts[ids[2]][1]-verts[ids[0]][1])-(verts[ids[1]][1]-verts[ids[0]][1])*(verts[ids[2]][0]-verts[ids[0]][0]);faces.append(ids if cross>0 else list(reversed(ids)))
from collections import Counter
edges=Counter(tuple(sorted((a,b)))for f in faces for a,b in zip(f,f[1:]+f[:1]));boundary=[e for e,n in edges.items()if n==1];assert set(edges.values())<={1,2};assert abs(covered-poly.area)<1e-11;degree=Counter(i for e in boundary for i in e);assert set(degree.values())=={2};assert len(verts)-len(edges)+len(faces)==1
# Every clipped core-boundary vertex maps back to its original outline station.
A=C;B=np.roll(C,-1,axis=0);AB=B-A;ab2=np.sum(AB*AB,axis=1);map_rows={};maximum=0.
for i in degree:
 p=np.array(verts[i]);t=np.clip(np.sum((p-A)*AB,axis=1)/ab2,0,1);q=A+AB*t[:,None];d2=np.sum((q-p)**2,axis=1);segment=int(np.argmin(d2));lam=float(t[segment]);err=math.sqrt(d2[segment]);maximum=max(maximum,err);assert err<1e-9;outer=O[segment]*(1-lam)+O[(segment+1)%len(O)]*lam;map_rows[str(i)]={'outer_original_2D_m':outer.tolist(),'inner_core_2D_m':verts[i],'source_segment':segment,'segment_fraction':lam}
out={'schema':1,'outline_sha256':hashlib.sha256((HERE/'outline-v1.json').read_bytes()).hexdigest(),'baseline_source_sha256':old['source_sha256'],'edge_radius_working_estimated_m':r,'grid_spacing_m':step,'vertices_2D_m':verts,'triangles':faces,'boundary_edges':boundary,'boundary_station_map':map_rows,'inner_offset_contour_m':C.tolist(),'planar_area_m2':poly.area,'triangulated_area_m2':covered,'area_difference_m2':covered-poly.area,'minimum_triangle_area_m2':small,'vertices':len(verts),'triangles_count':len(faces),'boundary_vertices':len(degree),'Euler_disk':1,'core_boundary_projection_error_max_m':maximum,'scope':'Inner chart grid for an explicitly rolled finite perimeter. No arbitrary UV/tangent repair and no global bevel. Radius/section remain estimated.','art_accepted':False};(HERE/'rounded-planar-grid-v3.json').write_text(json.dumps(out,indent=2)+'\n');print('VISOR_ROUNDED_CORE_GRID',len(verts),len(faces),len(boundary),small,maximum)
