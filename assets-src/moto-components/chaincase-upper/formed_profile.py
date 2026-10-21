"""Original bounded working silhouette/pressing fields, not a photo-calibrated trace.
Metres; coordinates(Y,Z), panel+X. Upper half attribution remains conditional.
"""
import math
import numpy as np

def bezier(a,b,c,d,n=16):
 a,b,c,d=map(lambda p:np.asarray(p,float),(a,b,c,d));return[(1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d for t in np.arange(n)/n]
def outline(P):
 ro=P['rear_outer_radius_m_estimated'];ri=P['rear_opening_radius_m_estimated'];front=ro-P['length_m_estimated'];out=[]
 def curve(a,b,c,d,n=16):out.extend(bezier(a,b,c,d,n))
 z0=P['front_notch_start_z_m_estimated'];nh=P['front_notch_height_m_estimated'];nd=P['front_notch_depth_m_estimated']
 curve((front,.008),(front,.012),(front,.016),(front,z0),12)
 out.extend([(front+nd*math.sin(math.pi*t)**2,z0+nh*t)for t in np.linspace(0,1,48,endpoint=False)])
 curve((front,z0+nh),(front,.055),(front,.065),(front+.005,.075),20)
 curve((front+.005,.075),(front+.009,.085),(front+.025,.09),(front+.045,.09))
 curve((front+.045,.09),(-.35,.091),(-.22,.075),(-.16,.076),45)
 target=(ro*math.cos(2*math.pi/3),ro*math.sin(2*math.pi/3));curve((-.16,.076),(-.12,.075),(-.075,.078),target,24)
 out.extend([(ro*math.cos(t),ro*math.sin(t))for t in np.linspace(2*math.pi/3,0,100,endpoint=False)])
 curve((ro,0),(ro,-.008),(ro,-.02),(ro-.005,-.02))
 curve((ro-.005,-.02),(ro-.010,-.02),(ri+.007,-.02),(ri+.004,-.02),8)
 curve((ri+.004,-.02),(ri,-.02),(ri,-.008),(ri,0))
 out.extend([(ri*math.cos(t),ri*math.sin(t))for t in np.linspace(0,math.pi,100,endpoint=False)])
 curve((-ri,0),(-.12,0),(-.32,.002),(front+.025,0),50)
 curve((front+.025,0),(front+.008,0),(front,.002),(front,.008))
 out=np.asarray(out);area=.5*np.sum(out[:,0]*np.roll(out[:,1],-1)-np.roll(out[:,0],-1)*out[:,1]);return out[::-1].copy()if area<0 else out

def inside(points,poly):
 points=np.asarray(points);p=np.zeros(len(points),bool);x,y=points[:,0],points[:,1]
 for a,b in zip(poly,np.roll(poly,-1,axis=0)):
  if abs(b[1]-a[1])<1e-16:continue
  p^=((a[1]>y)!=(b[1]>y))&(x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])
 return p

def distance_to_path(points,path,closed=False):
 points=np.asarray(points,float);path=np.asarray(path,float);a=path;b=np.roll(path,-1,axis=0)if closed else path[1:];a=a if closed else a[:-1];d=b-a;den=np.sum(d*d,axis=1);assert np.all(den>1e-20);result=[]
 for chunk in np.array_split(points,max(1,math.ceil(len(points)/2048))):
  v=chunk[:,None,:]-a[None,:,:];u=np.clip(np.sum(v*d[None,:,:],axis=-1)/den[None,:],0,1);delta=v-u[:,:,None]*d[None,:,:];result.extend(np.sqrt(np.min(np.sum(delta*delta,axis=-1),axis=1)))
 return np.asarray(result)

def smoothstep(x,a,b):
 u=np.clip((x-a)/(b-a),0,1);return u*u*(3-2*u)

def rib_controls():
 d=np.array([-.0465,.093*math.sin(2*math.pi/3)]);T=np.array([math.cos(math.pi/6),math.sin(math.pi/6)]);N=np.array([.5,-math.sqrt(3)/2]);speed=.070
 end1=d-speed/5*T;end2=2*end1-d+(speed*speed/.093)*N/20
 return np.array([[-.16,.060],[-.135,.060],[-.110,.060],end2,end1,d])

def evaluate_bezier(t,controls):
 t=np.asarray(t);out=np.zeros((len(t),2));degree=len(controls)-1
 for k,p in enumerate(controls):out+=(math.comb(degree,k)*(1-t)**(degree-k)*t**k)[:,None]*p
 return out

def rib_path():
 out=np.column_stack([np.linspace(-.46,-.16,50,endpoint=False),np.full(50,.060)]).tolist();out.extend(evaluate_bezier(np.linspace(0,1,70,endpoint=False),rib_controls()));out.extend([(.093*math.cos(t),.093*math.sin(t))for t in np.linspace(2*math.pi/3,.06,100)]);return np.asarray(out)

def distance_to_rib(points):
 # Exact straight/circular pieces and Newton projection on original C2 quintic connector.
 p=np.asarray(points);line=np.column_stack([np.clip(p[:,0],-.46,-.16),np.full(len(p),.060)]);dline=np.linalg.norm(p-line,axis=1);theta=np.clip(np.arctan2(p[:,1],p[:,0]),.06,2*math.pi/3);arc=.093*np.column_stack([np.cos(theta),np.sin(theta)]);darc=np.linalg.norm(p-arc,axis=1);controls=rib_controls();c1=5*np.diff(controls,axis=0);c2=4*np.diff(c1,axis=0);coarse_t=np.linspace(0,1,41);coarse=evaluate_bezier(coarse_t,controls);out=[]
 for chunk in np.array_split(p,max(1,math.ceil(len(p)/2048))):
  ds=np.sum((chunk[:,None,:]-coarse[None,:,:])**2,axis=-1);idx=ds.argmin(axis=1);t=coarse_t[idx].copy();best=ds[np.arange(len(chunk)),idx]
  for _ in range(8):
   q=evaluate_bezier(t,controls);dq=evaluate_bezier(t,c1);ddq=evaluate_bezier(t,c2);v=q-chunk;den=np.sum(dq*dq+v*ddq,axis=1);step=np.divide(np.sum(v*dq,axis=1),den,out=np.zeros(len(chunk)),where=abs(den)>1e-18);t=np.clip(t-step,0,1)
  q=evaluate_bezier(t,controls);out.extend(np.sqrt(np.minimum(best,np.sum((q-chunk)**2,axis=1))))
 return np.minimum(np.minimum(dline,darc),np.asarray(out))

def field(points,P,poly):
 points=np.asarray(points,float);edge=distance_to_path(points,poly,True);fade=smoothstep(edge,0,.005);d=distance_to_rib(points);features=[.0025*np.exp(-(d/.0030)**2)]
 # Three visible passages have original estimated pressings; no fourth mount.
 for i,centre in enumerate(P['mount_holes_candidate_YZ_m']):
  r=np.linalg.norm(points-np.asarray(centre),axis=1);rh=P['mount_hole_diameter_m_estimated']/2;outer=.012 if i==0 else .009;h=.006 if i==0 else .0018;features.append(h*(1-smoothstep(r,rh+.0008,outer)))
 # Clearly closed circular relief, no drill.
 r=np.linalg.norm(points-np.array([-.065,.060]),axis=1);features.append(.0012*(1-smoothstep(r,.005,.007))+.0005*np.exp(-((r-.006)/.0012)**2))
 power=P['pressing_blend_power_estimated'];height=sum(f**power for f in features)**(1/power)
 return height*fade

def face_points_and_normals(points,P,poly):
 points=np.asarray(points,float);height=field(points,P,poly);eps=1e-6;dy=(field(points+[eps,0],P,poly)-field(points-[eps,0],P,poly))/(2*eps);dz=(field(points+[0,eps],P,poly)-field(points-[0,eps],P,poly))/(2*eps);n=np.stack([np.ones(len(points)),-dy,-dz],1);n/=np.linalg.norm(n,axis=1,keepdims=True);v=np.column_stack([height,points]);return v,n
