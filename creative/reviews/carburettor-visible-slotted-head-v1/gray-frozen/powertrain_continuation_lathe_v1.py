"""Original solid revolved profile with explicit axis poles and bounded corner rounding."""
import math
from mathutils import Vector
from powertrain_completion_common import mesh_object
from powertrain_continuation_loft_v4 import recalc

def solid_profile(name,profile,n=192,q=.00012):
 assert profile[0][0]==profile[-1][0]==0
 p=[Vector(v)for v in profile];corners=[]
 for i,b in enumerate(p[1:-1],1):
  a,c=p[i-1],p[i+1];s=min(q,(b-a).length*.22,(c-b).length*.22);corners.append((b-(b-a).normalized()*s,b,b+(c-b).normalized()*s))
 curve=[]
 # Straight axis-face segments close naturally via triangle fans, never a giant Ngon.
 for i,(a,b,c)in enumerate(corners):
  for j in range(5):
   t=j/5;curve.append((1-t)**2*a+2*(1-t)*t*b+t*t*c)
  if i<len(corners)-1:
   for j in range(5):curve.append(c.lerp(corners[i+1][0],j/5))
  else:curve.append(c)
 V=[(0,0,profile[0][1])];F=[]
 for r,z in curve:
  assert r>0
  for j in range(n):a=math.tau*(j+.0137)/n;V.append((r*math.cos(a),r*math.sin(a),z))
 for j in range(n):F.append((0,1+j,1+(j+1)%n))
 for k in range(len(curve)-1):
  for j in range(n):F.append((1+k*n+j,1+k*n+(j+1)%n,1+(k+1)*n+(j+1)%n,1+(k+1)*n+j))
 pole=len(V);V.append((0,0,profile[-1][1]));base=1+(len(curve)-1)*n
 for j in range(n):F.append((base+j,pole,base+(j+1)%n))
 ob=mesh_object(name,V,F);recalc(ob);return ob
