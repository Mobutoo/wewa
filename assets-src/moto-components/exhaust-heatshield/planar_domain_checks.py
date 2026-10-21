"""Whole triangle inclusion in a simple outer polygon minus convex circular holes.
Numeric tolerance concerns retained working coordinates, never physical OEM fit.
"""
import numpy as np

def check_planar_domain(coords,faces,outer,hole_loops,tolerance_m=2e-7):
 points=np.array([list(p)for p in coords],dtype=float);loops=[np.array([list(p)for p in outer],dtype=float)]+[points[np.array(ids,dtype=int)]for ids in hole_loops]
 def prepare(poly):
  a=poly;b=np.roll(poly,-1,axis=0);d=b-a;l2=np.sum(d*d,axis=1);assert np.all(l2>0);return a,b,d,l2,np.minimum(a,b),np.maximum(a,b),np.min(a,axis=0),np.max(a,axis=0)
 prepared=[prepare(p)for p in loops];edgea=np.concatenate([p[0]for p in prepared]);edgeb=np.concatenate([p[1]for p in prepared]);edged=edgeb-edgea;edgelen=np.linalg.norm(edged,axis=1);bmin=np.minimum(edgea,edgeb);bmax=np.maximum(edgea,edgeb)
 def classification(point,poly):
  a,b,d,l2,_,_,lo,hi=poly
  if np.any(point<lo-tolerance_m)or np.any(point>hi+tolerance_m):return False,False
  dy=b[:,1]-a[:,1];den=np.where(np.abs(dy)>1e-20,dy,1.);inside=int(np.count_nonzero(((a[:,1]>point[1])!=(b[:,1]>point[1]))&(point[0]<(b[:,0]-a[:,0])*(point[1]-a[:,1])/den+a[:,0])))%2==1
  if inside:return True,False
  t=np.clip(np.sum((point-a)*d,axis=1)/l2,0,1);boundary=float(np.min(np.linalg.norm(point-(a+d*t[:,None]),axis=1)))<=tolerance_m
  return False,boundary
 def in_domain(point):
  inside,boundary=classification(point,prepared[0])
  if not(inside or boundary):return False
  for poly in prepared[1:]:
   inside,boundary=classification(point,poly)
   if inside:
    # A numerically shifted boundary vertex can lie just inside the hole.
    a,b,d,l2,*_=poly;t=np.clip(np.sum((point-a)*d,axis=1)/l2,0,1)
    if float(np.min(np.linalg.norm(point-(a+d*t[:,None]),axis=1)))>tolerance_m:return False
  return True
 bad_vertices=[i for i,p in enumerate(points)if not in_domain(p)];assert not bad_vertices,('Retained vertices outside planar domain',bad_vertices[:8])
 unique_edges={tuple(sorted((f[k],f[(k+1)%3])))for f in faces for k in range(3)};outside_midpoints=[];proper_crossings=[]
 def cross(a,b):return a[...,0]*b[...,1]-a[...,1]*b[...,0]
 for i,j in unique_edges:
  a=points[i];b=points[j];d=b-a;length=np.linalg.norm(d)
  if not in_domain((a+b)*.5):outside_midpoints.append([i,j])
  candidates=(bmin[:,0]<=max(a[0],b[0])+tolerance_m)&(bmax[:,0]>=min(a[0],b[0])-tolerance_m)&(bmin[:,1]<=max(a[1],b[1])+tolerance_m)&(bmax[:,1]>=min(a[1],b[1])-tolerance_m)
  if not np.any(candidates)or length==0:continue
  u=edgea[candidates];v=edgeb[candidates];ed=v-u;el=edgelen[candidates];o1=cross(ed,a-u)/el;o2=cross(ed,b-u)/el;o3=cross(d,u-a)/length;o4=cross(d,v-a)/length
  proper=((o1>tolerance_m)&(o2<-tolerance_m)|(o1<-tolerance_m)&(o2>tolerance_m))&((o3>tolerance_m)&(o4<-tolerance_m)|(o3<-tolerance_m)&(o4>tolerance_m))
  if np.any(proper):proper_crossings.append([i,j])
 assert not outside_midpoints,('Retained edges leave planar domain',outside_midpoints[:8]);assert not proper_crossings,('Retained triangle edge crosses boundary',proper_crossings[:8])
 contained_holes=0
 for poly in loops[1:]:
  centre=np.mean(poly,axis=0)
  for f in faces:
   t=points[np.array(f,dtype=int)]
   if np.any(centre<np.min(t,axis=0))or np.any(centre>np.max(t,axis=0)):continue
   signed=cross(np.roll(t,-1,axis=0)-t,centre-t)
   if np.all(signed>1e-14)or np.all(signed<-1e-14):contained_holes+=1
 assert contained_holes==0,('A triangle contains an entire internal hole',contained_holes)
 return {'whole_triangle_domain_checked':True,'retained_triangle_count':len(faces),'unique_vertices_checked':len(points),'unique_edges_checked':len(unique_edges),'vertices_outside_closed_domain':len(bad_vertices),'edge_midpoints_outside_closed_domain':len(outside_midpoints),'proper_crossings_of_outer_or_hole_boundaries':len(proper_crossings),'triangles_containing_entire_hole':contained_holes,'numeric_coordinate_tolerance_m':tolerance_m,'scope':'Complete triangle boundary inclusion plus absence of an enclosed hole; no physical casting tolerance or art reception.'}
