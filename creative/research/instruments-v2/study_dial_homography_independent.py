from pathlib import Path
import json,math,sys,numpy as np
from scipy.optimize import least_squares
from independent_homography_common import fit,unpack,project,edge_res,rim,marks,speeds,ks,C,S

def ray_model(p,persp,delta):
 count=8 if persp else 6
 q=np.r_[p[:count],1.] if delta is not None else np.r_[p[:count],1.,p[count]]
 return unpack(q,persp,delta)
def distances(p,persp,delta,obs=marks):
 h,_,de=ray_model(p,persp,delta);origin=project(h,np.zeros((1,2)))[0];a=np.column_stack([np.cos(-ks*de),np.sin(-ks*de)]);direction=project(h,a)-origin;direction/=np.linalg.norm(direction,axis=1,keepdims=True);d=obs-origin
 return direction[:,0]*d[:,1]-direction[:,1]*d[:,0]
def rfit(persp=True,delta=None,keep=range(6),edge=rim,obs=marks):
 z=fit(persp,delta,keep,edge,obs);count=8 if persp else 6;init=np.r_[z.x[:count],z.x[-1]] if delta is None else z.x[:count]
 lo=[-3,-3,-.5,-3,-3,-.5];hi=[3,3,.5,3,3,.5]
 if persp:lo.extend([-.6,-.6]);hi.extend([.6,.6])
 if delta is None:lo.append(math.radians(20));hi.append(math.radians(60))
 def residual(p):
  h,_,_=ray_model(p,persp,delta);return np.r_[edge_res(h,edge)/3,distances(p,persp,delta,obs)[list(keep)]/3]
 return least_squares(residual,init,bounds=(lo,hi),max_nfev=2500,ftol=1e-11,xtol=1e-11,gtol=1e-11)
# No Blender, images, source asset, pivots or v1 angles are changed by this script.
if __name__=='__main__':
 rows=[]
 for persp in [False,True]:
  for de in [270/7,40.,None]:
   z=rfit(persp,de);h,r,d=ray_model(z.x,persp,de);err=distances(z.x,persp,de);holds=[]
   for k in range(6):
    zz=rfit(persp,de,keep=[q for q in range(6)if q!=k]);hh,_,dd=ray_model(zz.x,persp,de);holds.append({'withheld_kmh':int(speeds[k]),'signed_line_distance_px':float(distances(zz.x,persp,de)[k]),'fitted_delta_deg':math.degrees(dd),'circle_centre_projection_px':project(hh,np.zeros((1,2)))[0].tolist()})
   inv=np.linalg.inv(np.array([[S,0,C[0]],[0,S,C[1]],[0,0,1]])@h);q=np.column_stack([marks,np.ones(6)])@inv.T;xy=q[:,:2]/q[:,2,None]
   rows.append({'perspective':persp,'fixed_delta_deg':de,'fitted_delta_deg':math.degrees(d),'H_face_to_native_uv':(np.array([[S,0,C[0]],[0,S,C[1]],[0,0,1]])@h).tolist(),'estimated_anchor_radius_each':np.linalg.norm(xy,axis=1).tolist(),'edge_residual_px_approx':edge_res(h,rim).tolist(),'anchor_signed_ray_distance_px':err.tolist(),'max_training_ray_distance_px':float(abs(err).max()),'rms_training_ray_distance_px':float(np.sqrt(np.mean(err**2))),'LOO_ray_holdouts':holds,'max_LOO_ray_distance_px':max(abs(q['signed_line_distance_px'])for q in holds),'active_bounds':z.active_mask.tolist()})
 rg=np.random.default_rng(4440);sens=[]
 for k in range(120):
  ee=rim+rg.uniform(-3,3,rim.shape);mm=marks+rg.uniform(-3,3,marks.shape);z=rfit(True,None,edge=ee,obs=mm);h,_,de=ray_model(z.x,True,None);sens.append(math.degrees(de))
 profile=[]
 for de in np.arange(20,46.01,.5):
  z=rfit(True,float(de));h,_,dd=ray_model(z.x,True,float(de));e=distances(z.x,True,float(de));re=edge_res(h,rim);profile.append({'delta_deg':float(de),'max_abs_ray_distance_px':float(abs(e).max()),'max_abs_rim_residual_px_approx':float(abs(re).max()),'both_residuals_below3':bool(abs(e).max()<=3 and abs(re).max()<=3)})
 out={'models':rows,'sensitivity':{'repetitions':120,'uniform_each_coord_interval_px':[-3,3],'delta_min_max_deg':[min(sens),max(sens)],'delta_p5_p50_p95_deg':np.percentile(sens,[5,50,95]).tolist(),'confidence_interval':False},'profile':profile}
 # Withhold interleaved rim points, never use withheld rim points for initialization.
 edge_holds=[]
 for de in [270/7,None]:
  for group in range(4):
   held=list(range(group,16,4)); train=[i for i in range(16) if i not in held]
   zz=rfit(True,de,edge=rim[train]);hh,_,dd=ray_model(zz.x,True,de)
   edge_holds.append({'fixed_delta_deg':de,'held_out_rim_indices':held,'held_out_rim_approx_distance_px':edge_res(hh,rim[held]).tolist(),'fitted_delta_deg':math.degrees(dd)})
 out['interleaved_rim_holdouts']=edge_holds;Path(__file__).with_name('speed-dial-homography-independent-results.json').write_text(json.dumps(out,indent=2));print(json.dumps([{k:r[k]for k in ['perspective','fixed_delta_deg','fitted_delta_deg','max_training_ray_distance_px','rms_training_ray_distance_px','max_LOO_ray_distance_px']}for r in rows],indent=2));print('sensitivity',out['sensitivity']);print('profilefound',[p['delta_deg']for p in profile if p['both_residuals_below3']])
