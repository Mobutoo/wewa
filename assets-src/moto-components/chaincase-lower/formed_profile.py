"""Original lower-half contour and pressing; no mirrored upper mesh or photo trace.
Metric values are bounded working estimates, not OEM dimensions.
"""
import math
import numpy as np

def bezier(a,b,c,d,n=16):
 a,b,c,d=map(lambda p:np.asarray(p,float),(a,b,c,d));return[(1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d for t in np.arange(n)/n]
def outline(P):
 ro=P['rear_outer_radius_m_estimated'];ri=P['rear_opening_radius_m_estimated'];f=ro-P['length_m_estimated'];out=[]
 def curve(a,b,c,d,n=16):out.extend(bezier(a,b,c,d,n))
 # Free front edge and stepped shoulder are not the upper's concave edge.
 curve((f,-.072),(f-.001,-.050),(f+.001,-.020),(f+.004,-.009),20)
 curve((f+.004,-.009),(f+.009,-.009),(f+.020,-.012),(f+.027,-.012),12)
 curve((f+.027,-.012),(f+.034,-.012),(f+.037,-.006),(f+.040,-.003),12)
 curve((f+.040,-.003),(f+.052,-.003),(-.433,-.012),(-.425,-.012),16)
 # Continuous bounded lobe around the single clearly visible forward mouth.
 curve((-.425,-.012),(-.415,-.012),(-.421,.010),(-.405,.010),20)
 curve((-.405,.010),(-.389,.010),(-.389,-.012),(-.379,-.014),20)
 curve((-.379,-.014),(-.32,-.014),(-.20,-.018),(-.125,-.013),38)
 curve((-.125,-.013),(-.102,-.010),(-ri,.012),(-ri,0),24)
 out.extend([(ri*math.cos(t),ri*math.sin(t))for t in np.linspace(math.pi,math.tau,120,endpoint=False)])
 curve((ri,0),(ri,.010),(ro-.006,.0065),(ro-.003,.001),12)
 curve((ro-.003,.001),(ro,-.0045),(ro,-.004),(math.sqrt(ro*ro-.008**2),-.008),20)
 out.extend([(ro*math.cos(t),ro*math.sin(t))for t in np.linspace(-math.asin(.008/ro),-2*math.pi/3,100,endpoint=False)])
 e=(ro*math.cos(-2*math.pi/3),ro*math.sin(-2*math.pi/3))
 curve(e,(-.077,-.0768),(-.115,-.082),(-.160,-.082),32)
 curve((-.160,-.082),(-.24,-.082),(-.37,-.082),(f+.027,-.078),40)
 curve((f+.027,-.078),(f+.010,-.077),(f+.003,-.078),(f,-.072),16)
 out=np.asarray(out);area=.5*np.sum(out[:,0]*np.roll(out[:,1],-1)-np.roll(out[:,0],-1)*out[:,1]);return out[::-1].copy()if area<0 else out

def inside(points,poly):
 points=np.asarray(points);p=np.zeros(len(points),bool);x,y=points[:,0],points[:,1]
 for a,b in zip(poly,np.roll(poly,-1,axis=0)):
  if abs(b[1]-a[1])<1e-16:continue
  p^=((a[1]>y)!=(b[1]>y))&(x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])
 return p

def distance_to_path(points,path,closed=False):
 points=np.asarray(points,float);path=np.asarray(path,float);a=path if closed else path[:-1];b=np.roll(path,-1,axis=0)if closed else path[1:];d=b-a;den=np.sum(d*d,axis=1);assert np.all(den>1e-20);result=[]
 for chunk in np.array_split(points,max(1,math.ceil(len(points)/2048))):
  v=chunk[:,None,:]-a[None,:,:];u=np.clip(np.sum(v*d[None,:,:],axis=-1)/den[None,:],0,1);delta=v-u[:,:,None]*d[None,:,:];result.extend(np.sqrt(np.min(np.sum(delta*delta,axis=-1),axis=1)))
 return np.asarray(result)

def smoothstep(x,a,b):
 u=np.clip((x-a)/(b-a),0,1);return u*u*(3-2*u)

def rib_controls():
 rad=.091;end=np.array([rad*math.cos(-2*math.pi/3),rad*math.sin(-2*math.pi/3)]);T=np.array([math.sqrt(3)/2,-.5]);N=np.array([.5,math.sqrt(3)/2]);speed=.075
 e1=end-speed*T/5;e2=2*e1-end+(speed*speed/rad)*N/20
 return np.array([[-.16,-.066],[-.135,-.066],[-.110,-.066],e2,e1,end])

def evaluate_bezier(t,c):
 t=np.asarray(t);out=np.zeros((len(t),2));d=len(c)-1
 for k,p in enumerate(c):out+=(math.comb(d,k)*(1-t)**(d-k)*t**k)[:,None]*p
 return out

def rib_path():
 out=np.column_stack([np.linspace(-.46,-.16,50,endpoint=False),np.full(50,-.066)]).tolist();out.extend(evaluate_bezier(np.linspace(0,1,70,endpoint=False),rib_controls()));out.extend([(.091*math.cos(t),.091*math.sin(t))for t in np.linspace(-2*math.pi/3,-.10,110)]);return np.asarray(out)

def distance_to_rib(points):
 p=np.asarray(points);line=np.column_stack([np.clip(p[:,0],-.46,-.16),np.full(len(p),-.066)]);dl=np.linalg.norm(p-line,axis=1);theta=np.clip(np.arctan2(p[:,1],p[:,0]),-2*math.pi/3,-.10);arc=.091*np.column_stack([np.cos(theta),np.sin(theta)]);da=np.linalg.norm(p-arc,axis=1);c=rib_controls();c1=5*np.diff(c,axis=0);c2=4*np.diff(c1,axis=0);ts=np.linspace(0,1,41);coarse=evaluate_bezier(ts,c);out=[]
 for chunk in np.array_split(p,max(1,math.ceil(len(p)/2048))):
  ds=np.sum((chunk[:,None,:]-coarse[None,:,:])**2,axis=-1);idx=ds.argmin(axis=1);t=ts[idx].copy();best=ds[np.arange(len(chunk)),idx]
  for _ in range(8):
   q=evaluate_bezier(t,c);dq=evaluate_bezier(t,c1);ddq=evaluate_bezier(t,c2);v=q-chunk;den=np.sum(dq*dq+v*ddq,axis=1);step=np.divide(np.sum(v*dq,axis=1),den,out=np.zeros(len(chunk)),where=abs(den)>1e-18);t=np.clip(t-step,0,1)
  out.extend(np.sqrt(np.minimum(best,np.sum((evaluate_bezier(t,c)-chunk)**2,axis=1))))
 return np.minimum(np.minimum(dl,da),out)

def field(points,P,poly):
 p=np.asarray(points,float);edge=distance_to_path(p,poly,True);fade=smoothstep(edge,0,.004);d=distance_to_rib(p);features=[.0023*np.exp(-(d/.0032)**2)]
 for i,c in enumerate(P['mount_holes_candidate_YZ_m']):
  rad=np.linalg.norm(p-np.asarray(c),axis=1);rh=P['mount_hole_diameter_m_estimated']/2
  if i==0:
   u=np.clip((rad-.0055)/.0035,0,1);features.append(P['front_boss_height_m_estimated']*(1-u**3*(10-15*u+6*u*u)))
  else:features.append(.0020*(1-smoothstep(rad,rh+.001,.010)))
 # Original shallow rectangular panel observed on reverse; no label/text pixels.
 q=np.abs(p-np.array([-.215,-.045]))-np.array([.030,.012]);sdf=np.linalg.norm(np.maximum(q,0),axis=1)+np.minimum(np.maximum(q[:,0],q[:,1]),0)-.006;features.append(.00065*(1-smoothstep(sdf,-.002,.002)))
 # Inspection opening is a plain finite cut edge: unseen seat/retention not invented.
 height=sum(f**8 for f in features)**(1/8)
 return height*fade

def face_points_and_normals(points,P,poly):
 p=np.asarray(points,float);h=field(p,P,poly);e=1e-6;dy=(field(p+[e,0],P,poly)-field(p-[e,0],P,poly))/(2*e);dz=(field(p+[0,e],P,poly)-field(p-[0,e],P,poly))/(2*e);n=np.stack([np.ones(len(p)),-dy,-dz],1);n/=np.linalg.norm(n,axis=1,keepdims=True);return np.column_stack([h,p]),n
