"""Original station surface and visible outer relief fields.
Every metric is an authored estimate. No hidden ribs or photograph pixels.
"""
from pathlib import Path
import numpy as np,json
from scipy.interpolate import PchipInterpolator
H=Path(__file__).resolve().parent;P=json.loads((H/'parameters-features-v1.json').read_text());scale=P['domain_chart_u_scale_m']
def spline(key):
 a=np.array(P[key],float);return PchipInterpolator(a[:,0],a[:,1],extrapolate=True)
width=spline('stations_width_half_m');centre=spline('stations_centre_Z_m');edge=spline('stations_sideedge_Z_m');ymin,ymax=P['length_range_m']
def smooth(q):
 q=np.clip(q,0,1);return q*q*q*(10+q*(-15+q*6))
def base(q):
 q=np.asarray(q);u=q[...,0]/scale;y=q[...,1];blend=smooth((y-P['tray_to_canopy_blend_Y_m'][0])/np.diff(P['tray_to_canopy_blend_Y_m'])[0]);sh=P['shoulder_u_tray']+(P['shoulder_u_canopy']-P['shoulder_u_tray'])*blend;crow=P['canopy_transverse_crown_m_estimated']*blend;t=np.minimum(np.abs(u)/sh,1);v=np.clip((np.abs(u)-sh)/(1-sh),0,1);z=centre(y)-crow*t**4+(edge(y)-centre(y)+crow)*(v*v*(2-v));return np.stack([u*width(y),y,z],-1)
def derivative(fn,q,j,h=1e-6):
 q=np.asarray(q,float);a=q.copy();b=q.copy();a[...,j]+=h;b[...,j]-=h;lo,hi=(-scale,scale)if j==0 else(ymin,ymax);a[...,j]=np.minimum(a[...,j],hi);b[...,j]=np.maximum(b[...,j],lo);return(fn(a)-fn(b))/(a[...,j]-b[...,j])[...,None]
def unit(a):return a/np.linalg.norm(a,axis=-1,keepdims=True)
def base_normal(q):return unit(np.cross(derivative(base,q,0),derivative(base,q,1)))
def mouth_frame(m):
 q=np.array([m['u']*scale,m['y_m']]);J=np.column_stack([derivative(base,q,0),derivative(base,q,1)]);w,U=np.linalg.eigh(J.T@J);inv=(U*(1/np.sqrt(w)))@U.T;return q,J,inv
frames={m['id']:mouth_frame(m)for m in P['observed_mouths_estimated']}
def compact(x):
 x=np.asarray(x);return np.where(abs(x)<1,(1-x*x)**3,0.)
def relief(q):
 q=np.asarray(q);x=q[...,0];y=q[...,1];h=np.zeros(q.shape[:-1])
 for m in P['observed_mouths_estimated']:
  if not m.get('ring_height_m'):continue
  c,J,_=frames[m['id']];radius=np.linalg.norm((q-c)@J.T,axis=-1);h+=m['ring_height_m']*(1-smooth((radius-m['ring_flat_radius_m'])/m['ring_fade_m']))
 for band in P['outer_band_candidates']:
  s=np.asarray(band['stations_Y_u']);yc=s[:,0];uc=s[:,1]*scale*band['side'];curve=PchipInterpolator(yc,uc,extrapolate=True);d=(x-curve(y))/band['halfwidth_chart_m'];fade=smooth((y-yc[0])/band['fade_length_m'])*smooth((yc[-1]-y)/band['fade_length_m']);h+=band['height_m']*compact(d)*fade
 a=P['outer_step_shoulder_rib'];yy=a['Y_range_m'];fade=smooth((y-yy[0])/a['fade_length_m'])*smooth((yy[1]-y)/a['fade_length_m']);h+=a['height_m']*compact((abs(x)-a['u_center_abs']*scale)/a['halfwidth_chart_m'])*fade
 return h
# Only the outside has the observed rib/ring relief; hidden underside is plain.
def outer(q):return base(q)+base_normal(q)*(P['wall_thickness_m_estimated']/2+relief(q))[...,None]
def inner(q):return base(q)-base_normal(q)*P['wall_thickness_m_estimated']/2
def surface_normals(fn,q,sign=1):return sign*unit(np.cross(derivative(fn,q,0),derivative(fn,q,1)))
