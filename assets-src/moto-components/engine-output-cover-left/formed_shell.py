"""Original concave formed-wall builder with constrained interior topology.
A CDT grid is checked against the actual outline before bending: never warp one n-gon.
"""
import math
from collections import Counter
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

def smooth_curve(points,steps=7):
 pts=[Vector(p) for p in points];out=[]
 for i in range(len(pts)):
  a,b,c,d=[pts[(i+k)%len(pts)] for k in [-1,0,1,2]]
  for j in range(steps):
   t=j/steps;out.append((2*b+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)*.5)
 return out

def inside(p,outline):
 odd=False;x,y=p
 for i,a in enumerate(outline):
  b=outline[(i+1)%len(outline)]
  if (a.y>y)!=(b.y>y) and x<(b.x-a.x)*(y-a.y)/(b.y-a.y)+a.x:odd=not odd
 return odd

def edge_distance(p,outline):
 best=1e9
 for i,a in enumerate(outline):
  b=outline[(i+1)%len(outline)];ab=b-a;t=max(0,min(1,(p-a).dot(ab)/ab.length_squared));best=min(best,(p-(a+t*ab)).length)
 return best

def cdt_slab(outline,thickness,pitch=.0009):
 n=len(outline);area=.5*sum(outline[i].x*outline[(i+1)%n].y-outline[(i+1)%n].x*outline[i].y for i in range(n));constraints=list(range(n))
 if area<0:constraints.reverse()
 points=list(outline);x=min(p.x for p in outline)+pitch*.31
 while x<max(p.x for p in outline):
  y=min(p.y for p in outline)+pitch*.47
  while y<max(p.y for p in outline):
   p=Vector((x,y))
   if inside(p,outline) and edge_distance(p,outline)>pitch*.18:points.append(p)
   y+=pitch
  x+=pitch
 coords,edges,cap,*_=delaunay_2d_cdt(points,[],[constraints],1,1e-8,False)
 cap=[f for f in cap if inside(sum((coords[i] for i in f),Vector((0,0)))/len(f),outline)]
 actual=sum(abs(sum(coords[f[j]].x*coords[f[(j+1)%len(f)]].y-coords[f[(j+1)%len(f)]].x*coords[f[j]].y for j in range(len(f))))/2 for f in cap)
 assert abs(actual-abs(area))<1e-8,('CDT changed outline area',actual,abs(area))
 used=sorted({i for f in cap for i in f});mapping={old:new for new,old in enumerate(used)};coords=[coords[i] for i in used];cap=[tuple(mapping[i] for i in f) for f in cap];n=len(coords)
 verts=[(p.x,p.y,w) for w in [-thickness/2,thickness/2] for p in coords];faces=[tuple(reversed(f)) for f in cap]+[tuple(i+n for i in f) for f in cap]
 counts=Counter(tuple(sorted((f[j],f[(j+1)%len(f)]))) for f in cap for j in range(len(f)))
 for (a,b),count in counts.items():
  if count==1:faces.append((a,b,b+n,a+n))
 return verts,faces,{'outline_area_m2':abs(area),'triangulated_area_m2':actual,'area_delta_m2':actual-abs(area),'interior_pitch_m':pitch,'vertices_2d':n,'front_faces':len(cap),'concave_outline_preserved':True}
