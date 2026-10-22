# Parent SHA256 a677152b88df0d9b6f2aa4d12c1ba11715032395d9be2b8a8c5bf2c3893e6ed0; ellipse width initialized across photo plane, thickness across depth.
"""Open source exterior skins; centripetal controls and arc-sampled transported ellipse frames."""
import math,numpy as np
from mathutils import Vector
def skin_mesh(name,controls,rx,ry,helpers,twist=0.):
 C=[Vector(p)for p in controls];path=[]
 for k in range(len(C)-1):
  b,c=C[k],C[k+1];a=C[k-1]if k else 2*b-c;d=C[k+2]if k+2<len(C)else 2*c-b;t0=0.;t1=(b-a).length**.5;t2=t1+(c-b).length**.5;t3=t2+(d-c).length**.5
  for j in range(48):
   t=t1+(t2-t1)*j/48;A1=(t1-t)/(t1-t0)*a+(t-t0)/(t1-t0)*b;A2=(t2-t)/(t2-t1)*b+(t-t1)/(t2-t1)*c;A3=(t3-t)/(t3-t2)*c+(t-t2)/(t3-t2)*d;B1=(t2-t)/(t2-t0)*A1+(t-t0)/(t2-t0)*A2;B2=(t3-t)/(t3-t1)*A2+(t-t1)/(t3-t1)*A3;path.append((t2-t)/(t2-t1)*B1+(t-t1)/(t2-t1)*B2)
 path.append(C[-1]);dense=np.array([tuple(v)for v in path]);arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(dense,axis=0),axis=1))];uniform=np.linspace(0,float(arc[-1]),math.ceil(float(arc[-1])/.0003)+1);path=[Vector(v)for v in np.column_stack([np.interp(uniform,arc,dense[:,i])for i in range(3)])];N=48;v=[];f=[];prev=None
 for i,p in enumerate(path):
  t=(path[min(i+1,len(path)-1)]-path[max(0,i-1)]).normalized();n=t.cross(Vector((0,0,1)))if prev is None else prev.copy();n-=t*n.dot(t);n.normalize();b=t.cross(n).normalized();prev=n.copy();a=twist*math.sin(2*math.pi*i/(len(path)-1));nn=math.cos(a)*n+math.sin(a)*b;bb=-math.sin(a)*n+math.cos(a)*b
  for j in range(N):theta=2*math.pi*j/N;v.append(tuple(p+rx*math.cos(theta)*nn+ry*math.sin(theta)*bb))
 for i in range(len(path)-1):
  for j in range(N):a=i*N+j;b=i*N+(j+1)%N;f.append((a,b,b+N,a+N))
 ob=helpers['mesh_object'](name,v,f);audit=helpers['clean_audit'](ob,expected_boundary=2*N);return ob,audit
