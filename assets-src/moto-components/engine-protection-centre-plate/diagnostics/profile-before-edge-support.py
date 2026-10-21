"""Original developed plate outline and a bounded 90degree sheet return.
Fold/back profile is a working estimate, not a measured PF231201 section.
"""
import numpy as np,math
def shape(P):
 top=P['fold_start_Z_m']+P['fold_mean_radius_m']*math.pi/2+P['return_length_m'];lo=P['flat_bottom_Z_m'];w=P['width_m']/2;r=P['lower_corner_radius_m'];rt=P['upper_corner_radius_m'];out=[]
 for cx,cy,rad,a,b in [(w-r,lo+r,r,-math.pi/2,0),(w-rt,top-rt,rt,0,math.pi/2),(-w+rt,top-rt,rt,math.pi/2,math.pi),(-w+r,lo+r,r,math.pi,3*math.pi/2)]:
  for t in np.linspace(a,b,33)[:-1]:out.append((cx+rad*math.cos(t),cy+rad*math.sin(t)))
 loops=[np.array(out,float)]
 for x,z in P['hole_centres_XZ_m']:
  a=np.linspace(0,-math.tau,129)[:-1];loops.append(np.column_stack([x+P['hole_radius_m']*np.cos(a),z+P['hole_radius_m']*np.sin(a)]))
 return loops
def normal2(a):
 prev=a-np.roll(a,1,axis=0);nxt=np.roll(a,-1,axis=0)-a;prev/=np.linalg.norm(prev,axis=1,keepdims=True);nxt/=np.linalg.norm(nxt,axis=1,keepdims=True);t=prev+nxt;t/=np.linalg.norm(t,axis=1,keepdims=True);return np.column_stack([t[:,1],-t[:,0]])
def inside(q,a):
 q=np.asarray(q);result=np.zeros(len(q),bool)
 for p,b in zip(a,np.roll(a,-1,axis=0)):
  if p[1]==b[1]:continue
  result^=((p[1]>q[:,1])!=(b[1]>q[:,1]))&(q[:,0]<(b[0]-p[0])*(q[:,1]-p[1])/(b[1]-p[1])+p[0])
 return result
def warp(V,NS,F,P):
 # Input flat coordinates(dnormal,uwidth,vdeveloped). Positive d faces -Y.
 r=P['fold_mean_radius_m'];start=P['fold_start_Z_m'];end=start+r*math.pi/2;v=V[:,2];d=V[:,0];u=V[:,1];a=np.clip((v-start)/r,0,math.pi/2);y=np.where(v<=start,0,np.where(v<end,r*(1-np.cos(a)),r+v-end));z=np.where(v<=start,v,np.where(v<end,start+r*np.sin(a),start+r));NY=-np.cos(a);NZ=np.sin(a);TY=np.sin(a);TZ=np.cos(a);k=np.where((v>start)&(v<end),1/r,0.);W=np.column_stack([u,y+d*NY,z+d*NZ]);ids=np.asarray(F).ravel();ns=np.asarray(NS);nv=ns[:,2]/(1+d[ids]*k[ids]);N=np.column_stack([ns[:,1],ns[:,0]*NY[ids]+nv*TY[ids],ns[:,0]*NZ[ids]+nv*TZ[ids]]);N/=np.linalg.norm(N,axis=1,keepdims=True);return W,N
