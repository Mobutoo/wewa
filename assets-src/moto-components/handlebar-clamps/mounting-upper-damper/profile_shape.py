"""Original estimated front collar/rim profile; unobserved reverse plain, not mirrored."""
import math,numpy as np
def smooth(t):
 t=np.clip(t,0,1);return t*t*t*(10+t*(-15+6*t))
def dsmooth(t):
 t=np.asarray(t);return np.where((t>0)&(t<1),30*t*t*(1-t)*(1-t),0.)
def front(r,P):
 R=P['outer_radius_m'];b=P['bore_radius_m'];ei=P['bore_edge_radius_m'];eo=P['outer_edge_radius_m'];wi=P['inner_collar_radial_width_m']-ei;wo=P['outer_rim_radial_width_m']-eo;ti=(np.asarray(r)-(b+ei))/wi;to=(np.asarray(r)-(R-P['outer_rim_radial_width_m']))/wo;h=P['plain_face_height_m']+P['inner_collar_height_m']*(1-smooth(ti))+P['outer_rim_height_m']*smooth(to);d=-P['inner_collar_height_m']*dsmooth(ti)/wi+P['outer_rim_height_m']*dsmooth(to)/wo;return h,d
def profile(P):
 R=P['outer_radius_m'];b=P['bore_radius_m'];eo=P['outer_edge_radius_m'];ei=P['bore_edge_radius_m'];n=P['quarter_round_steps'];rows=[]
 def arc(rc,zc,e,a,c,skip=False):
  for t in np.linspace(a,c,n+1)[1 if skip else 0:]:rows.append((rc+e*math.cos(t),zc+e*math.sin(t),math.cos(t),math.sin(t),'roundedge'))
 arc(R-eo,eo,eo,-math.pi/2,0);h=float(front(R-eo,P)[0]);rows.append((R,h-eo,1.,0.,'outerwall'));arc(R-eo,h-eo,eo,0,math.pi/2,True)
 rows[-1]=(*rows[-1][:4],'frontface')
 rr=np.unique(np.concatenate([np.linspace(b+ei,R-eo,int(math.ceil((R-eo-b-ei)/P['front_radial_step_m']))+1),[b+P['inner_collar_radial_width_m'],R-P['outer_rim_radial_width_m']]]))[::-1]
 for r in rr[1:]:
  z,d=map(float,front(r,P));a=math.hypot(d,1);rows.append((float(r),z,-d/a,1/a,'frontface'))
 h=float(front(b+ei,P)[0]);arc(b+ei,h-ei,ei,math.pi/2,math.pi,True);rows.append((b,ei,-1.,0.,'borewall'));arc(b+ei,ei,ei,math.pi,3*math.pi/2,True)
 for a,b in zip(rows,np.roll(np.array(rows,dtype=object),-1,axis=0)):
  assert math.hypot(a[0]-b[0],a[1]-b[1])>1e-12
 return rows
