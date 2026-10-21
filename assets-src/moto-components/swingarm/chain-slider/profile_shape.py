"""Original bounded ring/fork silhouette from same-face related photos, not a trace."""
import math
import numpy as np

def bezier(a,b,c,d,n=16):
 a,b,c,d=map(lambda p:np.asarray(p,float),(a,b,c,d));return[(1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d for t in np.arange(n)/n]
def orient(p,ccw=True):
 p=np.asarray(p,float);s=.5*np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1]);return p if(s>0)==ccw else p[::-1].copy()
def shape(P):
 R=P['ring_outer_diameter_m_estimated']/2;r=P['ring_bore_diameter_m_estimated']/2;tip=P['fork_tip_y_m_estimated'];join=0.;zj=R;p=[]
 def c(a,b,d,e,n=16):p.extend(bezier(a,b,d,e,n))
 c((join,zj),(.012,zj),(.030,.020),(.040,.020),24)
 c((.040,.020),(.070,.020),(.110,.020),(tip-.014,.020),42)
 c((tip-.014,.020),(tip-.008,.020),(tip-.006,.022),(tip,.022),20)
 p.extend([(tip+.005*math.cos(t),.017+.005*math.sin(t))for t in np.linspace(math.pi/2,-math.pi/2,48,endpoint=False)])
 c((tip,.012),(tip-.006,.012),(tip-.008,.015),(tip-.018,.015),20)
 c((tip-.018,.015),(.110,.015),(.085,.015),(.064,.015),36)
 c((.064,.015),(.059,.015),(.056,.015),(.056,.010),20)
 c((.056,.010),(.056,.004),(.056,-.004),(.056,-.010),16)
 c((.056,-.010),(.056,-.015),(.059,-.015),(.064,-.015),20)
 c((.064,-.015),(.085,-.015),(.110,-.015),(tip-.018,-.015),36)
 c((tip-.018,-.015),(tip-.008,-.015),(tip-.006,-.012),(tip,-.012),20)
 p.extend([(tip+.005*math.cos(t),-.017+.005*math.sin(t))for t in np.linspace(math.pi/2,-math.pi/2,48,endpoint=False)])
 c((tip,-.022),(tip-.006,-.022),(tip-.008,-.020),(tip-.014,-.020),20)
 c((tip-.014,-.020),(.110,-.020),(.070,-.020),(.040,-.020),42)
 c((.040,-.020),(.030,-.020),(.012,-zj),(join,-zj),24)
 t0=-math.acos(join/R);p.extend([(R*math.cos(t),R*math.sin(t))for t in np.linspace(t0,-math.tau-t0,260,endpoint=False)])
 outer=orient(p,True)
 a=np.linspace(0,math.tau,256,endpoint=False);ring=orient(r*np.column_stack([np.cos(a),np.sin(a)]),False)
 # First genuinely open small window, foreweb and bridge are visible; no hidden screws.
 lo,hi=.024,.049;bot,top=-.012,.012;rc=.0025;w=[]
 for cy,cz,t1,t2 in [(lo+rc,bot+rc,math.pi,1.5*math.pi),(hi-rc,bot+rc,1.5*math.pi,2*math.pi),(hi-rc,top-rc,0,.5*math.pi),(lo+rc,top-rc,.5*math.pi,math.pi)]:
  w.extend([(cy+rc*math.cos(t),cz+rc*math.sin(t))for t in np.linspace(t1,t2,24,endpoint=False)])
 return[outer,ring,orient(w,False)]
def normal2(poly):
 t=np.roll(poly,-1,axis=0)-np.roll(poly,1,axis=0);o=np.column_stack([t[:,1],-t[:,0]]);return o/np.linalg.norm(o,axis=1,keepdims=True)
def inside(p,poly):
 p=np.asarray(p);out=np.zeros(len(p),bool);x,y=p[:,0],p[:,1]
 for a,b in zip(poly,np.roll(poly,-1,axis=0)):
  if abs(b[1]-a[1])<1e-16:continue
  out^=((a[1]>y)!=(b[1]>y))&(x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])
 return out

def distance(p,loops):
 p=np.asarray(p);path=np.concatenate(loops);end=np.concatenate([np.roll(a,-1,axis=0)for a in loops]);d=end-path;den=np.sum(d*d,axis=1);out=[];assert np.min(den)>1e-20
 for q in np.array_split(p,max(1,math.ceil(len(p)/1024))):
  v=q[:,None,:]-path[None,:,:];u=np.clip(np.sum(v*d,axis=-1)/den,0,1);out.extend(np.sqrt(np.min(np.sum((v-u[:,:,None]*d)**2,axis=-1),axis=1)))
 return np.asarray(out)
def front_field(p,caploops):
 d=distance(p,caploops);u=np.clip(d/.0005,0,1);fade=u**3*(10-15*u+6*u*u);t=np.clip((d-.00145)/.00030,0,1);tail=1-t**3*(10-15*t+6*t*t);return-.00025*np.exp(-((d-.0011)/.00035)**2)*fade*tail
