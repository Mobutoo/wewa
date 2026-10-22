"""Analytic section utilities only; component-specific controls live in each exact build script/parameters."""
import math
from mathutils import Vector

def catmull(controls,samples=16):
 pts=[Vector(v)for v in controls];result=[]
 for i in range(len(pts)-1):
  a,b,c,d=[pts[max(0,min(len(pts)-1,j))]for j in [i-1,i,i+1,i+2]]
  for j in range(samples):
   t=j/samples;result.append(.5*(2*b+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
 result.append(pts[-1]);return result

def loft_superellipse(path,count=128):
 # Each tuple: X,Y,Z,width,height,superellipse exponent. Preserve real bent profile, no generic part supplied.
 V=[];F=[]
 for k,p in enumerate(path):
  a=path[max(k-1,0)];b=path[min(k+1,len(path)-1)];t=Vector((b[0]-a[0],b[1]-a[1],b[2]-a[2])).normalized();u=Vector((-t.y,t.x,0)).normalized();v=t.cross(u).normalized();w,h,e=p[3]/2,p[4]/2,p[5]
  assert w>0 and h>0 and e>=1.5
  for i in range(count):
   angle=i*math.tau/count;c=math.cos(angle);s=math.sin(angle);q=Vector(p[:3])+u*(w*math.copysign(abs(c)**(2/e),c))+v*(h*math.copysign(abs(s)**(2/e),s));V.append(tuple(q))
 for k in range(len(path)-1):
  a=k*count;b=a+count
  for i in range(count):j=(i+1)%count;F.append((a+i,a+j,b+j,b+i))
 F.append(tuple(reversed(range(count))));F.append(tuple((len(path)-1)*count+i for i in range(count)));return V,F
