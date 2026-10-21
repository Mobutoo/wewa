"""Visible bounded rear closure with small bore; no hidden exhaust chambers."""
import math
from mathutils import Vector

def build(P):
 rx,rz=P['working_outer_semiaxes_xz_m'];ri=P['working_small_outlet_radius_m'];rr=P['working_outer_and_bore_edge_round_m'];t=P['working_plate_thickness_m'];raised=t+P['working_lip_raise_m'];lip=P['working_lip_outer_radius_m'];transition=P['working_lip_transition_outer_radius_m'];assert 0<rr<t/2 and ri+rr<lip<transition<min(rx,rz)-rr;profile=[]
 def add(x,z,y,dx,dz,dy):
  row=(x,z,y,dx,dz,dy)
  if profile and max(abs(a-b)for a,b in zip(profile[-1][:3],row[:3]))<1e-13:return
  profile.append(row)
 # Front annular face. Flat radial support is technical, not an inspected hidden profile.
 add(rx-rr,rz-rr,0,-1,-1,0);add(ri+rr,ri+rr,0,-1,-1,0)
 for j in range(17):
  a=math.pi*j/32;add(ri+rr-rr*math.sin(a),ri+rr-rr*math.sin(a),rr-rr*math.cos(a),-math.cos(a),-math.cos(a),math.sin(a))
 add(ri,ri,raised-rr,0,0,1)
 for j in range(17):
  a=math.pi*j/32;add(ri+rr-rr*math.cos(a),ri+rr-rr*math.cos(a),raised-rr+rr*math.sin(a),math.sin(a),math.sin(a),math.cos(a))
 add(lip,lip,raised,1,1,0)
 for j in range(33):
  u=j/32;r=lip+(transition-lip)*u;h=3*u*u-2*u*u*u;dh=6*u-6*u*u;add(r,r,raised-P['working_lip_raise_m']*h,transition-lip,transition-lip,-P['working_lip_raise_m']*dh)
 add(rx-rr,rz-rr,t,1,1,0)
 for j in range(17):
  a=math.pi*j/32;add(rx-rr+rr*math.sin(a),rz-rr+rr*math.sin(a),t-rr+rr*math.cos(a),math.cos(a),math.cos(a),-math.sin(a))
 add(rx,rz,rr,0,0,-1)
 for j in range(16):
  a=math.pi*j/32;add(rx-rr+rr*math.cos(a),rz-rr+rr*math.cos(a),rr-rr*math.sin(a),-math.sin(a),-math.sin(a),-math.cos(a))
 N=P['circumferential_vertices'];vertices=[];normals=[];faces=[];UV=[];vcoords=[0.]
 for i,(x,z,y,dx,dz,dy)in enumerate(profile):
  if i:vcoords.append(vcoords[-1]+math.sqrt(((x-profile[i-1][0])**2+(z-profile[i-1][1])**2)/2+(y-profile[i-1][2])**2))
  for j in range(N):
   a=math.tau*j/N;c,s=math.cos(a),math.sin(a);vertices.append((x*c,y,z*s));around=Vector((-x*s,0,z*c));along=Vector((dx*c,dy,dz*s));normal=around.cross(along).normalized();assert normal.length>.9;normals.append(tuple(normal))
 total=vcoords[-1]+math.sqrt(((profile[0][0]-profile[-1][0])**2+(profile[0][1]-profile[-1][1])**2)/2+(profile[0][2]-profile[-1][2])**2);vcoords=[v/total for v in vcoords]
 for i in range(len(profile)):
  ni=(i+1)%len(profile);v0=vcoords[i];v1=vcoords[ni]if ni else 1.
  for j in range(N):
   nj=(j+1)%N;a=i*N+j;b=i*N+nj;c=ni*N+nj;d=ni*N+j;u0=j/N;u1=(j+1)/N;faces.extend([(a,b,c),(a,c,d)]);UV.extend([[(u0,v0),(u1,v0),(u1,v1)],[(u0,v0),(u1,v1),(u0,v1)]])
 return vertices,faces,normals,UV,Vector(P['working_front_face_centre_world_m']),{'profile_stations':len(profile),'circumferential_vertices':N,'small_outlet_open':True,'hidden_outlet_tube_or_baffles_fabricated':False,'rear_plate_back_wall_and_lip_estimated':True,'source_normals_analytic':True,'outer_section_inherited_from_estimated_body_not_rear_photo_metric':True}
