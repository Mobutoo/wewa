"""Original smooth raised annular envelope; hidden core/actual crush section unknown."""
import math
from mathutils import Vector

def build(P):
 profile=[]
 for row in P['front_profile_bezier_rz_m']:
  a,b,c,d=[Vector(q)for q in row]
  for j in range(P['samples_per_bezier']):
   t=j/P['samples_per_bezier'];point=(1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d;derivative=3*(1-t)**2*(b-a)+6*(1-t)*t*(c-b)+3*t*t*(d-c);assert derivative.length>0;profile.append((point.x,point.y,derivative.x,derivative.y))
 N=P['angular_vertices'];vertices=[];normals=[];faces=[];UV=[];length=[0.]
 for a,b in zip(profile,profile[1:]):length.append(length[-1]+math.dist(a[:2],b[:2]))
 total=length[-1]+math.dist(profile[-1][:2],profile[0][:2]);vcoords=[q/total for q in length]
 for r,z,dr,dz in profile:
  for j in range(N):
   angle=math.tau*j/N;c,s=math.cos(angle),math.sin(angle);vertices.append((r*c,r*s,z));normals.append(tuple(Vector((-dz*c,-dz*s,dr)).normalized()))
 for i in range(len(profile)):
  k=(i+1)%len(profile);v0=vcoords[i];v1=vcoords[k]if k else 1
  for j in range(N):
   nj=(j+1)%N;a=i*N+j;b=i*N+nj;c=k*N+nj;d=k*N+j;faces.extend([(a,d,c),(a,c,b)]);UV.extend([[(j/N,v0),(j/N,v1),((j+1)/N,v1)],[(j/N,v0),((j+1)/N,v1),((j+1)/N,v0)]])
 report={'profile_stations':len(profile),'angular_vertices':N,'working_profile_closed_length_m':total,'profile_method':'Seven explicit smooth cubic Bezier spans, front raised annular region and estimated closed rear exterior envelope','no_hidden_core_or_composition_certified':True,'source_analytic_normals':True,'isolated_uninstalled_frame':True,'all_dimensions_estimated':True}
 return vertices,faces,normals,UV,report
