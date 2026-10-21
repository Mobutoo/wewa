"""Reproduce the limited 2D strict crossing diagnostic; no mesh mutation."""
from pathlib import Path
import json, hashlib
import numpy as np
from formed_profile import outline
H=Path(__file__).resolve().parent
R=H.parents[2]
P=json.loads((H/'parameters.json').read_text())
p=outline(P)
v=np.roll(p,-1,axis=0)-np.roll(p,1,axis=0)
n=np.column_stack([v[:,1],-v[:,0]])
n/=np.linalg.norm(n,axis=1,keepdims=True)
def cross(a,b):return a[...,0]*b[...,1]-a[...,1]*b[...,0]
rows=[]
for d in [0,.00045,.001,.002,.00255,.003,.00345]:
 q=p+d*n;end=np.roll(q,-1,axis=0);hits=[]
 for i in range(len(q)):
  js=np.arange(i+2,len(q))
  if i==0:js=js[js!=len(q)-1]
  a,b=q[i],end[i];c,e=q[js],end[js]
  good=(cross(b-a,c-a)*cross(b-a,e-a)<0)&(cross(e-c,a-c)*cross(e-c,b-c)<0)
  hits.extend([[i,int(j)]for j in js[good]])
 assert not hits,(d,hits)
 rows.append({'outward_YZ_offset_m':d,'nonadjacent_strict_segment_crossings':hits})
result={'profile_sha256':hashlib.sha256((H/'formed_profile.py').read_bytes()).hexdigest(),'contour_points':len(p),'method':'Float64 strict nonadjacent segment crossings, averaged contour-tangent outward normals, seven offsets only. Collinear/touching cases and unsampled 3D surface are not certified.','rows':rows,'maximum_offset_m':.00345,'art_accepted':False}
print(json.dumps(result,indent=2))
