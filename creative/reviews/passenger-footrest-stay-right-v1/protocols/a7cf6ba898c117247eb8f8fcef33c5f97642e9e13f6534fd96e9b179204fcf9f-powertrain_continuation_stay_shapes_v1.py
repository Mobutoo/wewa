"""Original formed tubular stay envelopes; explicit smooth toes and finite sheet sections."""
import math
from mathutils import Vector
from powertrain_completion_common import mesh_object
from powertrain_continuation_loft_v4 import recalc

def smooth(t):
 t=max(0,min(1,t));return t*t*t*(10+t*(-15+6*t))
def arm(name,controls,clock):
 p=list(map(Vector,controls));cs=[]
 for i in range(181):
  t=i/180;cs.append((1-t)**3*p[0]+3*(1-t)**2*t*p[1]+3*(1-t)*t*t*p[2]+t**3*p[3])
 lengths=[0]
 for a,b in zip(cs,cs[1:]):lengths.append(lengths[-1]+(b-a).length)
 n=64;V=[];F=[];last=None
 for i,c in enumerate(cs):
  tangent=(cs[min(i+1,180)]-cs[max(0,i-1)]).normalized();depth=Vector((0,0,1)) if last is None else last
  depth=(depth-tangent*depth.dot(tangent)).normalized();last=depth.copy();width=depth.cross(tangent).normalized();b=smooth((lengths[i]-(lengths[-1]-.040))/.030);a=math.radians(clock)*b
  w=width*math.cos(a)+depth*math.sin(a);d=-width*math.sin(a)+depth*math.cos(a)
  for j in range(n):
   q=math.tau*j/n;f=1-.08*math.cos(4*q)*b;V.append(tuple(c+w*((.007+.003*b)*math.cos(q)*f)+d*((.007-.0054*b)*math.sin(q)*f)))
 end=cs[-1];axis=tangent.copy();hole=end+axis*.001;holeaxis=d.copy()
 for k in range(1,48):
  phi=math.pi/2*k/48;co=end+axis*(.010*math.sin(phi));rr=math.cos(phi)
  for j in range(n):
   q=math.tau*j/n;f=1-.08*math.cos(4*q)*rr*rr;V.append(tuple(co+w*(.010*rr*math.cos(q)*f)+d*(.0016*rr*math.sin(q)*f)))
 count=len(V)//n
 for k in range(count-1):
  for j in range(n):F.append((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j))
 root=len(V);V.append(tuple(cs[0]));toe=len(V);V.append(tuple(end+axis*.010))
 for j in range(n):F.extend([(root,(j+1)%n,j),((count-1)*n+j,(count-1)*n+(j+1)%n,toe)])
 ob=mesh_object(name,V,F);recalc(ob);return ob,hole,holeaxis

def extrude(name,polygon,axis,low,high):
 # Polygon coordinates occupy the other two axes in increasing order.
 other=[k for k in range(3)if k!=axis];V=[];N=len(polygon)
 for level in [low,high]:
  for p in polygon:
   v=[0,0,0];v[axis]=level;v[other[0]]=p[0];v[other[1]]=p[1];V.append(v)
 F=[tuple(reversed(range(N))),tuple(N+i for i in range(N))]
 for i in range(N):j=(i+1)%N;F.append((i,j,N+j,N+i))
 ob=mesh_object(name,V,F);recalc(ob);return ob

def eye(name,cy):
 N=128;profile=[(.012,-.0085),(.0115,-.009),(.00565,-.009),(.00525,-.0085)]
 for k in range(1,220):profile.append((.00525,-.0085+.017*k/220))
 profile +=[(.00525,.0085),(.00565,.009),(.0115,.009),(.012,.0085)]
 V=[];F=[]
 for k,(r,z) in enumerate(profile):
  for j in range(N):
   a=math.tau*(j+.0137)/N;window=smooth((z+.0085)/.001)*smooth((.0085-z)/.001);rr=r-(.00035*(.5+.5*math.cos(math.tau*(z+.0085)/.00125-a))*window if 3<=k<len(profile)-3 else 0)
   V.append((rr*math.cos(a),cy+rr*math.sin(a),z))
 for k in range(len(profile)):
  for j in range(N):F.append((k*N+j,k*N+(j+1)%N,((k+1)%len(profile))*N+(j+1)%N,((k+1)%len(profile))*N+j))
 ob=mesh_object(name,V,F);recalc(ob);return ob
