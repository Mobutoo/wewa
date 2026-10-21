"""Float64 triangle distances with conservative AABB candidates, sampled bound only.
Adapted method (plane inclusion plus clamped edges) from the independent
engine-spark-cap/topology_stage_v2.py local test; this file adds bounded global
candidates and exact unchanged-face exclusion, not a float32 BVH distance.
"""
import json,sys,hashlib,time
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from rtree import index
p=Path(sys.argv[1]);d=json.loads(p.read_text());out=Path(sys.argv[2]);t0=time.monotonic()
a=np.asarray(d['raw_vertices'],dtype=np.float64);af=np.asarray(d['raw_triangles'],dtype=np.int64);b=np.asarray(d['vertices'],dtype=np.float64);bf=np.asarray(d['triangles'],dtype=np.int64)
class Surface:
 def __init__(self,v,f):
  self.v=v;self.f=f;self.tri=v[f];self.kd=cKDTree(v);prop=index.Property();prop.dimension=3;lo=self.tri.min(axis=1);hi=self.tri.max(axis=1);self.box=index.Index(((i,tuple(np.r_[x,y]),None)for i,(x,y)in enumerate(zip(lo,hi))),properties=prop);self.max_candidates=0
 def distance(self,p):
  # A nearest vertex is on the target surface and therefore a valid distance upper bound.
  bound=self.kd.query(p)[0]+1e-11;ids=list(self.box.intersection(tuple(np.r_[p-bound,p+bound])));assert ids
  self.max_candidates=max(self.max_candidates,len(ids));tri=self.tri[ids];aa=tri[:,0];bb=tri[:,1];cc=tri[:,2];n=np.cross(bb-aa,cc-aa);ln=np.linalg.norm(n,axis=1);valid=ln>1e-30;n[valid]/=ln[valid,None];signed=np.einsum('ij,ij->i',p-aa,n);q=p-signed[:,None]*n;inside=valid.copy()
  best=np.full(len(tri),np.inf)
  for u,v in[(aa,bb),(bb,cc),(cc,aa)]:
   edge=v-u;inside&=np.einsum('ij,ij->i',np.cross(edge,q-u),n)>=-1e-24;den=np.einsum('ij,ij->i',edge,edge);t=np.zeros(len(tri));ok=den>0;t[ok]=np.clip(np.einsum('ij,ij->i',p-u,edge)[ok]/den[ok],0,1);best=np.minimum(best,np.linalg.norm(p-u-t[:,None]*edge,axis=1))
  best[inside]=np.minimum(best[inside],np.abs(signed[inside]));return float(best.min())
sa=Surface(a,af);sb=Surface(b,bf)
# Identical vertex positions and triangles are known coincident, without numerical nearest queries.
labels={}
def lab(v):
 k=tuple(v)
 if k not in labels:labels[k]=len(labels)
 return labels[k]
al=np.asarray([lab(v)for v in a]);bl=np.asarray([lab(v)for v in b]);ak={tuple(sorted(row))for row in al[af]};bk={tuple(sorted(row))for row in bl[bf]};aset=set(al);bset=set(bl)
self_checks=[]
for name,v,f,surf in[('before',a,af,sa),('after',b,bf,sb)]:
 ids=np.linspace(0,len(f)-1,96,dtype=int);q=v[f[ids]].mean(axis=1);err=max(surf.distance(x)for x in q);self_checks.append({'surface':name,'triangle_centroids':len(q),'maximum_self_distance_m':err});assert err<1e-11,(name,err)
def compare(name,v,f,vl,otherlabels,otherfaces,surf):
 missing=sorted({int(i)for i in range(len(v))if int(vl[i])not in otherlabels});changed=[i for i,tri in enumerate(vl[f])if tuple(sorted(tri))not in otherfaces];maximum=0.;worst=None;n=0
 for kind,points in[('vertex',v[missing]),('triangle_centroid',v[f[changed]].mean(axis=1))]:
  for q in points:
   dist=surf.distance(q);n+=1
   if dist>maximum:maximum=dist;worst={'kind':kind,'point_m':q.tolist(),'distance_m':dist}
   if n%10000==0:print(name,n,'max_m',maximum,flush=True)
 return{'vertices_on_source_surface':len(v),'vertex_positions_proved_exactly_shared':len(v)-len(missing),'changed_vertices_distance_sampled':len(missing),'triangles':len(f),'exact_shared_triangles_proved_coincident':len(f)-len(changed),'changed_triangle_centroids_distance_sampled':len(changed),'maximum_sampled_closest_surface_distance_m':maximum,'worst_sample':worst,'maximum_conservative_AABB_candidates':surf.max_candidates}
r={'input_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'method':'Float64 normalized plane inclusion and clamped projections onto all three triangle edges. Candidate triangle AABBs intersect cube bounded by exact nearest-vertex distance +1e-11m. All exactly shared positions/faces proven coincident; all other vertices and changed triangle centroids sampled. No float32 nearest BVH used.','dependencies':{'numpy':np.__version__,'scipy':__import__('scipy').__version__,'rtree':__import__('rtree').__version__},'identity_tests':self_checks,'before_to_after':compare('before_to_after',a,af,al,bset,bk,sb),'after_to_before':compare('after_to_before',b,bf,bl,aset,ak,sa),'sampling_is_not_a_global_Hausdorff_proof':True,'source_simplification':d['source_simplification'],'elapsed_s':time.monotonic()-t0,'passed':False}
r['passed']=max(r[k]['maximum_sampled_closest_surface_distance_m']for k in['before_to_after','after_to_before'])<=1e-6 and d['source_simplification']['volume_relative_change']<1e-5;out.write_text(json.dumps(r,indent=2)+'\n');assert r['passed'],r;print('WEWA_BODY_FLOAT64_SURFACE_PASS',r['elapsed_s'],flush=True)
