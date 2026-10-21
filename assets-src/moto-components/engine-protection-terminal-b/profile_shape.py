"""Original rounded paddle→narrow lug and finite double circularbend section.
All measures/profile/parallelendplanes are authored estimates from relatedphoto.
"""
import numpy as np,math
def section(P):
 a=math.radians(P['bend_angle_deg']);r=P['bend_mean_radius_m'];off=P['terminal_plane_offset_m'];L=(off-2*r*(1-math.cos(a)))/math.sin(a);assert L>0 and r>P['thickness_m']/2;start=P['bend_start_V_m'];v1=start+r*a;v2=v1+L;end=v2+r*a;z_end=start+2*r*math.sin(a)+L*math.cos(a);return a,r,L,start,v1,v2,end,z_end

def shape(P):
 r=P['lower_paddle_radius_m'];ru=P['upper_lug_radius_m'];ev=P['lower_circle_end_V_m'];vtop=P['upper_lug_circle_centre_V_m'];vn=P['neck_end_V_m'];a=math.asin(ev/r);right=np.array([[r*math.cos(t),r*math.sin(t)]for t in np.linspace(-math.pi/2,a,97)]);p0=right[-1];dv=vn-ev;slope=-ev/math.sqrt(r*r-ev*ev);p1=p0+np.array([slope*dv/3,dv/3]);p2=np.array([ru,vn-dv/3]);p3=np.array([ru,vn]);t=np.linspace(0,1,97);curve=(1-t)[:,None]**3*p0+3*((1-t)**2*t)[:,None]*p1+3*((1-t)*t*t)[:,None]*p2+t[:,None]**3*p3;upper=np.array([[ru*math.cos(t),vtop+ru*math.sin(t)]for t in np.linspace(0,math.pi,97)]);outline=np.vstack([right,curve[1:],[[ru,vtop]],upper[1:],[[ -ru,vn]],curve[-2::-1]*[-1,1],right[-2::-1]*[-1,1]]);raw=[]
 for x in outline:
  if not raw or np.linalg.norm(x-raw[-1])>1e-12:raw.append(x)
 if np.linalg.norm(raw[0]-raw[-1])<1e-12:raw.pop()
 # Retain exact arc/curve endpoints; sample developedside through BOTH bends.
 dense=[]
 for p,q in zip(raw,np.roll(raw,-1,axis=0)):
  step=P['bend_boundary_step_m']if abs(q[1]-p[1])>1e-9 else P['boundary_step_m'];n=max(1,math.ceil(np.linalg.norm(q-p)/step));dense.extend(p+(q-p)*t for t in np.arange(n)/n)
 loops=[np.asarray(dense)]
 for (u,v),rad in zip(P['hole_centres_UV_m'],P['hole_radii_m']):
  a=np.linspace(0,-math.tau,129)[:-1];loops.append(np.column_stack([u+rad*np.cos(a),v+rad*np.sin(a)]))
 return loops

def normal2(a):
 prev=a-np.roll(a,1,axis=0);nxt=np.roll(a,-1,axis=0)-a;prev/=np.linalg.norm(prev,axis=1,keepdims=True);nxt/=np.linalg.norm(nxt,axis=1,keepdims=True);t=prev+nxt;t/=np.linalg.norm(t,axis=1,keepdims=True);return np.column_stack([t[:,1],-t[:,0]])
def inside(q,a):
 q=np.asarray(q);result=np.zeros(len(q),bool)
 for p,b in zip(a,np.roll(a,-1,axis=0)):
  if p[1]==b[1]:continue
  result^=((p[1]>q[:,1])!=(b[1]>q[:,1]))&(q[:,0]<(b[0]-p[0])*(q[:,1]-p[1])/(b[1]-p[1])+p[0])
 return result

def neutral(v,P):
 a,r,L,start,v1,v2,end,zend=section(P);v=np.asarray(v);s1=np.clip(v-start,0,r*a);b=s1/r;s2=np.clip(v-v1,0,L);s3=np.clip(v-v2,0,r*a);c=s3/r;y=r*(1-np.cos(b))+s2*np.sin(a)+r*(np.cos(a-c)-np.cos(a));z=np.minimum(v,start)+r*np.sin(b)+s2*np.cos(a)+r*(np.sin(a)-np.sin(a-c))+np.maximum(v-end,0);angle=np.where(v<=v1,b,np.where(v<=v2,a,a-c));k=np.where((v>start)&(v<v1),1/r,np.where((v>v2)&(v<end),-1/r,0.));return y,z,angle,k

def warp(V,NS,F,P):
 V=np.asarray(V);d=V[:,0];u=V[:,1];v=V[:,2];y,z,a,k=neutral(v,P);NY=-np.cos(a);NZ=np.sin(a);TY=np.sin(a);TZ=np.cos(a);W=np.column_stack([u,y+d*NY,z+d*NZ]);ids=np.asarray(F).ravel();ns=np.asarray(NS);fac=1+d[ids]*k[ids];assert fac.min()>0.;nv=ns[:,2]/fac;N=np.column_stack([ns[:,1],ns[:,0]*NY[ids]+nv*TY[ids],ns[:,0]*NZ[ids]+nv*TZ[ids]]);N/=np.linalg.norm(N,axis=1,keepdims=True);return W,N
