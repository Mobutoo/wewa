# Independent study support; circle/common-radius initialization is conditional, not calibration.
import json,numpy as np,math
from pathlib import Path
from scipy.optimize import least_squares
p=Path(__file__).with_name('speed-dial-calage.json');D=json.loads(p.read_text());rim=np.array(D['landmarks_native_px']);marks=np.array([a['native_outer_mark_anchor_px_approx']for a in D['anchor_diagnostics']]);C=np.array(D['ellipse_centre_px']);S=80.;A=np.array(D['working_face_unit_to_native_matrix'])[:2,:2]/S;baseang=math.radians(225-40*270/140);R=np.array([[math.cos(baseang),-math.sin(baseang)],[math.sin(baseang),math.cos(baseang)]]);H0=np.eye(3);H0[:2,:2]=A@R
speeds=np.array([a['value_kmh']for a in D['anchor_diagnostics']]);ks=(speeds-40)/20

def unpack(p,persp,delta):
 h=np.eye(3);h[:2]=p[:6].reshape(2,3);offset=6
 if persp:h[2,:2]=p[6:8];offset=8
 r=p[offset];de=math.radians(delta) if delta is not None else p[offset+1]
 return h,r,de

def project(h,xy):
 q=np.column_stack([xy,np.ones(len(xy))])@h.T;return C+S*q[:,:2]/q[:,2,None]

def edge_res(h,edge):
 inv=np.linalg.inv(h);cc=inv.T@np.diag([1.,1.,-1.])@inv;q=np.column_stack([(edge-C)/S,np.ones(len(edge))]);f=np.einsum('ij,ij->i',q@cc,q);g=2*(q@cc)[:,:2];return S*f/np.linalg.norm(g,axis=1)

def pred(p,persp,delta):
 h,r,de=unpack(p,persp,delta);return project(h,np.column_stack([r*np.cos(-ks*de),r*np.sin(-ks*de)]))

def fit(persp=True,delta=None,keep=range(6),edge=rim,obs=marks):
 # Refit initial ellipse only from training rim points. Initial in-plane gauge
 # uses only a retained mark; held-out marks/edges never set the initial fit.
 ec=np.mean(edge,axis=0)
 def er(v):
  cx,cy,a,b,theta=v;dd=edge-[cx,cy];co=np.cos(theta);si=np.sin(theta);xx=dd[:,0]*co+dd[:,1]*si;yy=-dd[:,0]*si+dd[:,1]*co;F=xx**2/a**2+yy**2/b**2-1
  return F/np.maximum(2*np.sqrt(xx**2/a**4+yy**2/b**4),1e-8)
 ee=least_squares(er,[ec[0],ec[1],81,69,.05]).x;cx,cy,a,b,theta=ee;co=np.cos(theta);si=np.sin(theta);AA=np.array([[a*co,b*si],[a*si,-b*co]])/S
 first=list(keep)[0];qq=np.linalg.solve(AA,(obs[first]-[cx,cy])/S);phase=np.arctan2(qq[1],qq[0])+ks[first]*math.radians(delta if delta is not None else 40)
 rr=np.array([[math.cos(phase),-math.sin(phase)],[math.sin(phase),math.cos(phase)]]);initialH=np.eye(3);initialH[:2,:2]=AA@rr;initialH[:2,2]=(np.array([cx,cy])-C)/S
 init=list(initialH[:2].reshape(-1));lo=[-3,-3,-.5,-3,-3,-.5];hi=[3,3,.5,3,3,.5]
 if persp:init.extend([0,0]);lo.extend([-.6,-.6]);hi.extend([.6,.6])
 init.append(.975);lo.append(.8);hi.append(1.1)
 if delta is None:init.append(math.radians(40));lo.append(math.radians(20));hi.append(math.radians(60))
 def res(v):
  h,_,_=unpack(v,persp,delta);return np.r_[edge_res(h,edge)/3,((pred(v,persp,delta)-obs)[list(keep)]/3).reshape(-1)]
 best=least_squares(res,init,bounds=(lo,hi),max_nfev=2500,xtol=1e-11,ftol=1e-11,gtol=1e-11)
 return best

