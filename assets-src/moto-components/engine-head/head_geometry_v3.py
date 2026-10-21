"""Original smooth contour/edge construction; configured independently per casting."""
import math
from mathutils import Vector

def cat(a,b,c,d,t):return .5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)
def curve(points,n=12):
 c=[Vector(p)for p in points];out=[]
 for i in range(len(c)):
  for j in range(n):out.append(cat(c[(i-1)%len(c)],c[i],c[(i+1)%len(c)],c[(i+2)%len(c)],j/n))
 return out

def configure(parameters,collection,mat,make_mesh):
 global P,construction,black,mesh_object,perimeter
 P=parameters;construction=collection;black=mat;mesh_object=make_mesh;perimeter=curve(P['fin_perimeter_controls_xy_m'])

def rounded_fin(name,z,thickness,scale=1,edge=None):
 edge=min(edge or P['fin_edge_radius_working_m'],thickness*.45);profile=[]
 outline=[p.copy()for p in perimeter]
 if abs(z-P['fin_centres_z_m'][-1])<1e-9:
  factor=P['joint_interface_rework_v3']['uppermost_fin_positive_X_reach_factor'];width=P['joint_interface_rework_v3']['uppermost_fin_transition_end_X_m']
  for p in outline:
   t=max(0,min(1,p.x/width));p.x*=1-(1-factor)*t*t*(3-2*t)
 for j in range(13):
  a=-math.pi/2+math.pi/2*j/12;profile.append((z-thickness/2+edge+edge*math.sin(a),edge-edge*math.cos(a)))
 for j in range(13):
  a=math.pi/2*j/12;profile.append((z+thickness/2-edge+edge*math.sin(a),edge-edge*math.cos(a)))
 verts=[];faces=[];N=len(outline)
 for height,inset in profile:
  for i,p in enumerate(outline):
   tangent=(outline[(i+1)%N]-outline[(i-1)%N]).normalized();q=p*scale+Vector((-tangent.y,tangent.x))*inset;verts.append((q.x,q.y,height))
 for j in range(len(profile)-1):
  for i in range(N):k=(i+1)%N;faces.append((j*N+i,j*N+k,(j+1)*N+k,(j+1)*N+i))
 faces.extend([tuple(reversed(range(N))),tuple(range((len(profile)-1)*N,len(profile)*N))]);return mesh_object(name,verts,faces,construction,black)
