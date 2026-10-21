"""Bounded monotone variable shell sections; no inferred internal silencer."""
import math,bisect
from mathutils import Vector

def pchip(x,y):
 h=[b-a for a,b in zip(x,x[1:])];d=[(b-a)/q for a,b,q in zip(y,y[1:],h)];m=[0.]*len(x)
 for i in range(1,len(x)-1):
  if d[i-1]*d[i]>0:
   a=2*h[i]+h[i-1];b=h[i]+2*h[i-1];m[i]=(a+b)/(a/d[i-1]+b/d[i])
 # Working end sections have zero slope; not a measured rolled joint.
 def evaluate(v):
  k=min(len(x)-2,max(0,bisect.bisect_right(x,v)-1));q=h[k];t=(v-x[k])/q;a,b=y[k:k+2];c,e=m[k:k+2];f=(2*t**3-3*t*t+1)*a+(t**3-2*t*t+t)*q*c+(-2*t**3+3*t*t)*b+(t**3-t*t)*q*e;df=((6*t*t-6*t)*a+(3*t*t-4*t+1)*q*c+(-6*t*t+6*t)*b+(3*t*t-2*t)*q*e)/q
  return f,df
 return evaluate

def build(P):
 rows=P['working_sections_world'];Y=[q['y_m']for q in rows];functions=[pchip(Y,[q[k]for q in rows])for k in ['rx_m','rz_m','centre_z_m']];N=P['circumferential_vertices'];t=P['working_section_wall_m'];rr=P['working_mouth_edge_round_m'];assert 0<rr<t/2;origin=Vector(P['working_front_centre_world_m']);x=origin.x;front,rear=Y[0],Y[-1];samples=[]
 def section(y):return [f(y)for f in functions]
 def curve_sub(a,b,depth):
  va=section(a);vb=section(b);err=0
  for frac in [.25,.5,.75]:
   c=section(a+(b-a)*frac)
   for k in range(3):err=max(err,abs(c[k][0]-((1-frac)*va[k][0]+frac*vb[k][0])))
  if b-a>P['max_station_step_m']or err>P['max_section_linear_error_m']:
   assert depth<24;mid=(a+b)/2;curve_sub(a,mid,depth+1);curve_sub(mid,b,depth+1)
  else:samples.append(a)
 for a,b in zip(Y,Y[1:]):curve_sub(a,b,0)
 samples.append(rear);profile=[]
 for j in range(17):
  a=math.pi*j/32;profile.append((front+rr*(1-math.cos(a)),-rr+rr*math.sin(a),math.sin(a),math.cos(a)))
 profile +=[(y,0,1,0)for y in samples if front+rr<y<rear-rr];profile.append((rear-rr,0,1,0))
 for j in range(1,17):
  a=math.pi*j/32;profile.append((rear-rr+rr*math.sin(a),-rr+rr*math.cos(a),math.cos(a),-math.sin(a)))
 profile.append((rear,-t+rr,0,-1))
 for j in range(1,17):
  a=math.pi*j/32;profile.append((rear-rr+rr*math.cos(a),-t+rr-rr*math.sin(a),-math.sin(a),-math.cos(a)))
 profile +=[(y,-t,-1,0)for y in reversed(samples)if front+rr<y<rear-rr];profile.append((front+rr,-t,-1,0))
 for j in range(1,17):
  a=math.pi*j/32;profile.append((front+rr-rr*math.sin(a),-t+rr-rr*math.cos(a),-math.cos(a),math.sin(a)))
 vertices=[];normals=[];faces=[];UV=[];vcoords=[0.]
 for i,(y,offset,dy,dr)in enumerate(profile):
  if i:vcoords.append(vcoords[-1]+math.hypot(y-profile[i-1][0],offset-profile[i-1][1]))
  (rx,dx),(rz,dz),(cz,dc)=section(y);rx+=offset;rz+=offset;assert rx>0 and rz>0
  for j in range(N):
   a=math.tau*j/N;c,s=math.cos(a),math.sin(a);point=Vector((x+rx*c,y,cz+rz*s));across=Vector((-rx*s,0,rz*c));along=Vector(((dx*dy+dr)*c,dy,dc*dy+(dz*dy+dr)*s));normal=along.cross(across).normalized();assert normal.length>.9;vertices.append(tuple(point-origin));normals.append(tuple(normal))
 total=vcoords[-1]+abs(profile[-1][1]-profile[0][1]);vcoords=[q/total for q in vcoords]
 for i in range(len(profile)):
  ni=(i+1)%len(profile);v0=vcoords[i];v1=vcoords[ni]if ni else 1.
  for j in range(N):
   nj=(j+1)%N;a=i*N+j;b=i*N+nj;c=ni*N+nj;d=ni*N+j;u0=j/N;u1=(j+1)/N;faces.extend([(a,d,c),(a,c,b)]);UV.extend([[(u0,v0),(u0,v1),(u1,v1)],[(u0,v0),(u1,v1),(u1,v0)]])
 report={'longitudinal_samples':len(samples),'wall_profile_stations':len(profile),'circumferential_vertices':N,'section_interpolation':'Monotone piecewise cubic Hermite with declared zero end slopes; no overshoot of listed scalar sections','working_section_wall_m':t,'wall_is_cross_section_difference_not_measured_normal_thickness':True,'two_open_lumens':True,'body_inner_baffles_or_catalyst':False,'authored_analytic_source_normals':True,'all_sections_and_axes_estimated':True,'camera_or_wheelbase_metric_inversion_used':False}
 return vertices,faces,normals,UV,origin,report
