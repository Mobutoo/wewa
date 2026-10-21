"""Strict2D original/inset boundary crossings at actual sampled bevel offsets only."""
from pathlib import Path
import json,hashlib,numpy as np
from profile_shape import shape,normal2,inside
H=Path(__file__).resolve().parent;P=json.loads((H/'parameters.json').read_text());loops=shape(P);norms=[normal2(a)for a in loops];cross=lambda a,b:a[...,0]*b[...,1]-a[...,1]*b[...,0];rows=[]
sets=[('bevel',float(d),[a-d*n for a,n in zip(loops,norms)])for d in np.linspace(0,P['edge_radius_m_estimated'],7)]
caps=[a-P['edge_radius_m_estimated']*n for a,n in zip(loops,norms)]
sets += [('contour_band',float(d),[a-d*normal2(a)for a in caps])for d in list(np.arange(.0001,.00175,.0001))+[.00175]]
for kind,d,polys in sets:
 for j,q in enumerate(polys):
  e=np.roll(q,-1,axis=0);hits=[]
  for i in range(len(q)):
   js=np.arange(i+2,len(q));js=js[js!=len(q)-1]if i==0 else js;a,b=q[i],e[i];c,f=q[js],e[js];good=(cross(b-a,c-a)*cross(b-a,f-a)<0)&(cross(f-c,a-c)*cross(f-c,b-c)<0);hits.extend([[i,int(k)]for k in js[good]])
  assert not hits,(d,j,hits);rows.append({'family':kind,'loop':j,'domain_inset_m':float(d),'strict_nonadjacent_crossings':hits})
print(json.dumps({'profile_sha256':hashlib.sha256((H/'profile_shape.py').read_bytes()).hexdigest(),'rows':rows,'scope':'Actual seven bevel offsets and eighteen constraintband offsets, perloop strict crossings only; excludes adjacent/collinear/touching/crossloop cases, not complete3D selfintersection/formability proof.','art_accepted':False},indent=2))
