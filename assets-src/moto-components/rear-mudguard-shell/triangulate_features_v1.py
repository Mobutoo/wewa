"""Blender native constrained chart triangulation; source stage, no mesh repair."""
import numpy as np,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
H=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();a=json.loads((H/'feature-domain-preparation-v1.json').read_text());assert a['chart_input_sha256']==sha(H/'feature-domain-input-v1.npz');d=np.load(H/'feature-domain-input-v1.npz');loops=[d['loop_'+str(i)]for i in range(6)];points=[];edges=[]
for l in loops:
 j=len(points);points.extend(l);edges.extend((j+i,j+(i+1)%len(l))for i in range(len(l)))
constraint_count=len(points);points.extend(d['interior_points']);unique=[];seen=set()
for p in points:
 k=tuple(np.round(p,11))
 if k not in seen:seen.add(k);unique.append(Vector(p))
assert len(seen)>=constraint_count
print('REAR_SHELL_CDT',len(unique),flush=True);xy,_,faces,*_=delaunay_2d_cdt(unique,edges,[list(range(len(loops[0])))],1,1e-9,False);xy=np.array([a[:]for a in xy]);F=np.asarray(faces,np.int64);assert F.shape[1]==3
def inside(q,a):
 r=np.zeros(len(q),bool)
 for p,b in zip(a,np.roll(a,-1,axis=0)):
  if p[1]==b[1]:continue
  r^=((p[1]>q[:,1])!=(b[1]>q[:,1]))&(q[:,0]<(b[0]-p[0])*(q[:,1]-p[1])/(b[1]-p[1])+p[0])
 return r
q=xy[F].mean(1);keep=inside(q,loops[0])
for l in loops[1:]:keep&=~inside(q,l)
F=F[keep];tri=xy[F];area=(tri[:,1,0]-tri[:,0,0])*(tri[:,2,1]-tri[:,0,1])-(tri[:,1,1]-tri[:,0,1])*(tri[:,2,0]-tri[:,0,0]);assert (abs(area)>1e-20).all();F[area<0]=F[area<0,::-1];polyarea=lambda l:abs(np.sum(l[:,0]*np.roll(l[:,1],-1)-l[:,1]*np.roll(l[:,0],-1)))/2;expected=polyarea(loops[0])-sum(polyarea(l)for l in loops[1:]);actual=abs(area).sum()/2;assert abs(actual-expected)<1e-8,(actual,expected)
used=np.unique(F);remap=np.full(len(xy),-1,np.int64);remap[used]=np.arange(len(used));xy=xy[used];F=remap[F];lookup={tuple(np.round(p,9)):i for i,p in enumerate(xy)};boundary=[]
for l in loops:
 ids=[]
 for p in l:
  k=tuple(np.round(p,9))
  if k in lookup:i=lookup[k]
  else:
   ds=np.linalg.norm(xy-p,axis=1);i=int(ds.argmin());assert ds[i]<2e-8
  ids.append(i)
 boundary.append(np.array(ids,np.int64))
# Check that every intended constraint edge survived before a 3D surface exists.
from collections import Counter
E=Counter(tuple(sorted((int(a),int(b))))for f in F for a,b in zip(f,np.roll(f,-1)));actualbound={e for e,n in E.items()if n==1};intendedbound={tuple(sorted((int(a),int(b))))for l in boundary for a,b in zip(l,np.roll(l,-1))};assert actualbound==intendedbound,(len(actualbound),len(intendedbound),len(actualbound-intendedbound));assert all(n in [1,2]for n in E.values())
np.savez_compressed(H/'feature-domain-triangulated-v1.npz',points=xy,triangles=F,**{'boundary_'+str(i):l for i,l in enumerate(boundary)});r={**a,'triangulate_recipe_sha256':sha(Path(__file__)),'triangulated_chart_sha256':sha(H/'feature-domain-triangulated-v1.npz'),'vertices':len(xy),'triangles':len(F),'area_m2_chart':float(actual),'expected_area_m2_chart':float(expected),'all_constrained_boundary_edges_preserved':True,'no_postexport_buffer_repair':True,'art_accepted':False};(H/'feature-domain-triangulation-v1.json').write_text(json.dumps(r,indent=2)+'\n');print('REAR_SHELL_DOMAIN_READY',json.dumps(r))
