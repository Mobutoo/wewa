"""Bounded periodic cubic contour fit: original editable curves, no photo texture."""
import json,numpy as np,hashlib
from scipy.optimize import minimize
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];source=ROOT/'creative/research/switchgear-left/marking-vector-contours-v2.json';d=json.loads(source.read_text())
def resample(points,N=384):
 p=np.asarray(points,float);q=np.roll(p,-1,axis=0);length=np.linalg.norm(q-p,axis=1);c=np.r_[0,np.cumsum(length)];t=np.arange(N)*c[-1]/N;i=np.minimum(np.searchsorted(c,t,side='right')-1,len(p)-1);return p[i]+(q[i]-p[i])*((t-c[i])/length[i])[:,None]
def matrix(N,K):
 t=np.arange(N)*K/N;i=np.floor(t).astype(int);u=t-i;w=np.stack(((1-u)**3,3*u**3-6*u*u+4,-3*u**3+3*u*u+3*u+1,u**3),axis=1)/6;B=np.zeros((N,K))
 for j in range(4):B[np.arange(N),(i+j-1)%K]+=w[:,j]
 return B

def distance(a,poly):
 p=np.asarray(poly);q=np.roll(p,-1,axis=0);e=q-p;v=a[:,None,:]-p;u=np.clip(np.sum(v*e,axis=2)/np.sum(e*e,axis=1),0,1);return np.min(np.linalg.norm(v-u[:,:,None]*e,axis=2),axis=1)
def crosses(poly):
 p=np.asarray(poly);q=np.roll(p,-1,axis=0);n=len(p);cross=lambda a,b:a[...,0]*b[...,1]-a[...,1]*b[...,0]
 for i,(a,b)in enumerate(zip(p,q)):
  ids=[j for j in range(n)if j not in[i,(i-1)%n,(i+1)%n]];c=p[ids];e=q[ids];x=cross(b-a,c-a);y=cross(b-a,e-a);u=cross(e-c,a-c);v=cross(e-c,b-c)
  if np.any((x*y<-1e-12)&(u*v<-1e-12)):return True
 return False
def capsule_handles(params):
 centre=np.array(params[:2]);angle,ell,r=params[2:];u=np.array([np.cos(angle),np.sin(angle)]);v=np.array([-u[1],u[0]]);k=4*(np.sqrt(2)-1)/3
 co=[ell*u+r*v,-ell*u+r*v,-(ell+r)*u,-ell*u-r*v,ell*u-r*v,(ell+r)*u]
 left=[co[0]+k*r*u,co[1]+2*ell*u/3,co[2]+k*r*v,co[3]-k*r*u,co[4]-2*ell*u/3,co[5]-k*r*v]
 right=[co[0]-2*ell*u/3,co[1]-k*r*u,co[2]-k*r*v,co[3]+2*ell*u/3,co[4]+k*r*u,co[5]+k*r*v]
 return [{'co_px':(a+centre).tolist(),'handle_left_px':(b+centre).tolist(),'handle_right_px':(c+centre).tolist()} for a,b,c in zip(co,left,right)]
def evaluate_handles(vertices,N=96):
 out=[]
 for i,a in enumerate(vertices):
  b=vertices[(i+1)%len(vertices)];aa=np.array(a['co_px']);ab=np.array(a['handle_right_px']);ba=np.array(b['handle_left_px']);bb=np.array(b['co_px']);t=np.arange(N)/N
  out.extend(((1-t)**3)[:,None]*aa+(3*t*(1-t)**2)[:,None]*ab+(3*t*t*(1-t))[:,None]*ba+(t**3)[:,None]*bb)
 return np.array(out)
def fit_capsule(points):
 p=np.asarray(points);mu=p.mean(0);_,basis=np.linalg.eigh(np.cov(p.T));u=basis[:,-1];u=u if u[0]>0 else -u;v=np.array([-u[1],u[0]]);pca=(p-mu)@np.array([u,v]).T;low=pca.min(0);high=pca.max(0);centre=mu+(low[0]+high[0])/2*u+(low[1]+high[1])/2*v;r=(high[1]-low[1])/2;init=[*centre,np.arctan2(u[1],u[0]),(high[0]-low[0])/2-r,r];a=resample(points)
 def error(x):
  if x[3]<1 or x[4]<.4 or x[4]>4:return 1e4
  q=evaluate_handles(capsule_handles(x),24)
  return max(distance(q,points).max(),distance(a,q).max())
 result=minimize(error,init,method='Powell',options={'maxiter':200,'xtol':1e-6,'ftol':1e-6});handles=capsule_handles(result.x);curve=evaluate_handles(handles)
 return handles,curve,max(distance(curve,points).max(),distance(a,curve).max()),result.x.tolist()
rows=[]
for name,g in d['glyphs'].items():
 for ci,c in enumerate(g['components']):
  for li,loop in enumerate(c['loops']):
   points=loop['points_px'];a=resample(points);tol=1.30 if name!='horn'and c['white_pixels']<100 else 1.25 if name=='horn'else 1.0
   for K in range(5,49):
    B=matrix(len(a),K);control=np.linalg.lstsq(B,a,rcond=None)[0];curve=matrix(512,K)@control;error=max(distance(curve,points).max(),distance(a,curve).max())
    if error<tol:break
   assert error<tol,(name,ci,li,error);assert not crosses(curve),(name,ci,li,'Self crossing')
   area=np.sum(curve[:,0]*np.roll(curve[:,1],-1)-curve[:,1]*np.roll(curve[:,0],-1))/2;assert area*loop['signed_area_px2']>0
   vertices=[]
   for k in range(K):
    co=(control[(k-1)%K]+4*control[k]+control[(k+1)%K])/6;tangent=(control[(k+1)%K]-control[(k-1)%K])/6;vertices.append({'co_px':co.tolist(),'handle_left_px':(co-tangent).tolist(),'handle_right_px':(co+tangent).tolist()})
   continuity='C2 periodic cubic B-spline'
   if name!='horn' and c['white_pixels']<100:
    vertices,curve,error,params=fit_capsule(points);K=len(vertices);tol=1.30;assert error<tol,(name,ci,error);assert not crosses(curve);area=np.sum(curve[:,0]*np.roll(curve[:,1],-1)-curve[:,1]*np.roll(curve[:,0],-1))/2;assert area*loop['signed_area_px2']>0;continuity='G1 tangent-continuous analytical straight sides and quarter-circle cubic ends, not C2 at joins';loop['capsule_fit_centre_angle_half_straight_radius_px']=params
   loop['bezier_handles']=vertices;loop['continuity']=continuity;loop['fit_max_two_sided_distance_to_v2_polyline_px']=float(error);loop['fit_tolerance_px']=tol;loop['fit_sampled_area_px2']=float(area);loop['self_crossings_detected']=False
   rows.append({'glyph':name,'component':ci,'loop':li,'Bezier_knots':K,'max_two_sided_error_px':float(error),'native_bound_including_v2_simplification_px':float(error)+d['simplification_tolerance_px'],'original_polygon_vertices':len(points)})
d.update({'revision':'smooth-v3','parent_vector_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'method':'D and horn: fewest-knots bounded periodic cubic B-splines, exact editable C2 Bezier conversion. Ten rays: independently fitted smooth six-knot capsules with straight sides and cubic circular ends, tangent-continuous G1 joins, not C2; actual cubic outlines tested against the documentary boundary. No VECTOR handle stair corners. Loops retain winding and are checked for crossings.','native_reading_uncertainty_working_px':2.0,'physical_calibration':False,'fit_summary':rows,'art_accepted':False})
assert max(r['native_bound_including_v2_simplification_px']for r in rows)<2
out=ROOT/'creative/research/switchgear-left/marking-vector-contours-v3.json';out.write_text(json.dumps(d,indent=2)+'\n');print('SMOOTH_CONTOURS',len(rows),'native bound',max(r['native_bound_including_v2_simplification_px']for r in rows))
