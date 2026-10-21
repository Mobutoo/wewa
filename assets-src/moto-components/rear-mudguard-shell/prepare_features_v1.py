"""Prepare original constrained chart with five observed mouth loops.
No dimensions inferred from paper, image metadata or a neighbouring fastener.
"""
from pathlib import Path
import numpy as np,json,hashlib,sys
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H));from shell_surface_v1 import P,frames,scale,base,base_normal,relief
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();lo,hi=P['length_range_m'];step=P['domain_boundary_pitch_m']
# CCW outside and clockwise holes: material is always on the left.
# A small rounded perimetercorner is an explicit section estimate, not a
# hidden flange. Both arc endpoints retained before densifying straight runs.
outline=[];rc=.0025
for cx,cy,aa,bb in [(.1-rc,lo+rc,-np.pi/2,0),(.1-rc,hi-rc,0,np.pi/2),(-.1+rc,hi-rc,np.pi/2,np.pi),(-.1+rc,lo+rc,np.pi,3*np.pi/2)]:
 for t in np.linspace(aa,bb,17):outline.append(np.array([cx+rc*np.cos(t),cy+rc*np.sin(t)]))
out=[]
for a,b in zip(outline,np.roll(outline,-1,axis=0)):
 n=max(1,int(np.ceil(np.linalg.norm(b-a)/step)));out.extend((a+(b-a)*t)for t in np.arange(n)/n)
loops=[np.asarray(out)]
for m in P['observed_mouths_estimated']:
 c,J,inv=frames[m['id']];t=np.linspace(0,-2*np.pi,129)[:-1];v=np.column_stack([np.cos(t),np.sin(t)])*m['mean_edge_radius_m'];loops.append(c+v@inv.T)
def inside(q,a):
 q=np.asarray(q);r=np.zeros(len(q),bool)
 for p,b in zip(a,np.roll(a,-1,axis=0)):
  if p[1]==b[1]:continue
  r^=((p[1]>q[:,1])!=(b[1]>q[:,1]))&(q[:,0]<(b[0]-p[0])*(q[:,1]-p[1])/(b[1]-p[1])+p[0])
 return r
def domain(q):
 keep=inside(q,loops[0])
 for a in loops[1:]:keep&=~inside(q,a)
 return keep
pitch=P['domain_grid_pitch_m'];x=np.arange(-.1+pitch*.37,.1,pitch);y=np.arange(lo+pitch*.41,hi,pitch);X,Y=np.meshgrid(x,y);q=np.column_stack([X.ravel(),Y.ravel()]);q=q[domain(q)];samples=[q]
# True feature bands get local sampling; increased detail is local, not a blind
# million-triangle increase of the whole shell. Ring and hole near-boundaries.
for m,a in zip(P['observed_mouths_estimated'],loops[1:]):
 c,J,inv=frames[m['id']];angles=np.linspace(0,2*np.pi,129)[:-1]
 deltas=[.0004,.0008,.0013,.002,.003,.0045]
 if m.get('ring_height_m'):
  outer=m['ring_flat_radius_m']+m['ring_fade_m'];deltas=np.unique(np.r_[deltas,np.arange(m['mean_edge_radius_m']+.0002,outer+.0001,P['local_sampling_policy']['roof_ring_radial_step_m'])-m['mean_edge_radius_m'],m['ring_flat_radius_m']-m['mean_edge_radius_m'],outer-m['mean_edge_radius_m']])
 for delta in deltas:
  r=m['mean_edge_radius_m']+delta;v=np.column_stack([np.cos(angles),np.sin(angles)])*r;s=c+v@inv.T;samples.append(s[domain(s)])
for band in P['outer_band_candidates']:
 s=np.asarray(band['stations_Y_u']);from scipy.interpolate import PchipInterpolator
 yy=np.linspace(s[0,0],s[-1,0],int((s[-1,0]-s[0,0])/.0008)+1);curve=PchipInterpolator(s[:,0],s[:,1]*scale*band['side']);offsets=np.linspace(-band['halfwidth_chart_m']*1.3,band['halfwidth_chart_m']*1.3,17);xx=curve(yy)[:,None]+offsets[None,:];y=np.broadcast_to(yy[:,None],xx.shape);a=np.column_stack([xx.ravel(),y.ravel()]);samples.append(a[domain(a)])
a=P['outer_step_shoulder_rib'];yy=np.arange(*a['Y_range_m'],.0008);off=np.linspace(-a['halfwidth_chart_m']*1.3,a['halfwidth_chart_m']*1.3,17)
for sign in [-1,1]:
 X,Y=np.meshgrid(sign*a['u_center_abs']*scale+off,yy);q=np.column_stack([X.ravel(),Y.ravel()]);samples.append(q[domain(q)])
# Local highcurvature transition patches identified by stage1reflections and
# authorfield interpolation check. Mainarch/interior grid stays unchanged.
l=P['local_sampling_policy'];y=np.arange(*l['step_patch_Y_m'],l['step_patch_pitch_m']);x=np.arange(*l['step_patch_chart_X_abs_m'],l['step_patch_pitch_m'])
for sign in [-1,1]:
 X,Y=np.meshgrid(sign*x,y);q=np.column_stack([X.ravel(),Y.ravel()]);samples.append(q[domain(q)])
y=np.arange(lo+.0001,-.39,l['front_return_Y_pitch_m']);x=np.arange(-.1+.0001,.1,l['front_return_chart_X_pitch_m']);X,Y=np.meshgrid(x,y);q=np.column_stack([X.ravel(),Y.ravel()]);samples.append(q[domain(q)])
points=np.concatenate(samples);np.savez_compressed(H/'feature-domain-input-v1.npz',**{'loop_'+str(i):a for i,a in enumerate(loops)},interior_points=points)
r={'component_id':P['component_id'],'revision':P['revision'],'parameters_sha256':sha(H/'parameters-features-v1.json'),'surface_recipe_sha256':sha(H/'shell_surface_v1.py'),'prepare_recipe_sha256':sha(Path(__file__)),'chart_input_sha256':sha(H/'feature-domain-input-v1.npz'),'boundary_loops':len(loops),'mouth_loops':len(loops)-1,'interior_samples':len(points),'all_metric_parameters_estimated':True,'approximate_tangent_mouths_not_certified_cylindrical_drills':True,'art_accepted':False};(H/'feature-domain-preparation-v1.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
