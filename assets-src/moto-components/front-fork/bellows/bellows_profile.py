"""Original meridian and true normal-offset inner wall; no measured OEM section."""
import math,numpy as np

def profiles(p,length):
 lower=p['lower_cuff_length_m'];start=lower+p['lower_transition_length_m'];end=length-p['upper_transition_length_m']-p['upper_cuff_length_m'];upper=length-p['upper_cuff_length_m'];pitch=(end-start)/p['fold_count_working'];assert pitch>0
 segments=[(0,lower,16),(lower,start,32),(start,end,p['fold_count_working']*p['meridian_steps_per_fold']),(end,upper,36),(upper,length,24)];zs=[0.]
 for a,b,n in segments:zs.extend(a+(b-a)*i/n for i in range(1,n+1))
 outer=[];inner=[];thickness=[];wall=p['fold_wall_working_m'];cuff=p['cuff_wall_working_m'];valley=p['valley_radius_m'];crest=p['crest_radius_m']
 def transition(z,a,b,r0,r1,t0,t1):
  t=(z-a)/(b-a);f=.5*(1-math.cos(math.pi*t));return r0+(r1-r0)*f,(r1-r0)*.5*math.pi/(b-a)*math.sin(math.pi*t),t0+(t1-t0)*f
 for z in zs:
  if z<=lower:r,dr,th=p['lower_cuff_outer_radius_m'],0,cuff
  elif z<start:r,dr,th=transition(z,lower,start,p['lower_cuff_outer_radius_m'],valley,cuff,wall)
  elif z<=end:
   phase=(z-start)/pitch;r=valley+(crest-valley)*.5*(1-math.cos(math.tau*phase));dr=(crest-valley)*math.pi/pitch*math.sin(math.tau*phase);th=wall
  elif z<upper:r,dr,th=transition(z,end,upper,valley,p['upper_cuff_outer_radius_m'],wall,cuff)
  else:r,dr,th=p['upper_cuff_outer_radius_m'],0,cuff
  norm=math.sqrt(1+dr*dr);outer.append([r,z]);inner.append([r-th/norm,z+th*dr/norm]);thickness.append(th)
 return np.array(outer),np.array(inner),np.array(thickness)

def validate_profile(outer,inner,wall,exact_normal_offset=True):
 a=outer[:-1];b=outer[1:];d=b-a;v=inner[:,None,:]-a[None,:,:];t=np.clip((v*d[None,:,:]).sum(-1)/(d*d).sum(-1)[None,:],0,1);distance=np.linalg.norm(v-t[:,:,None]*d[None,:,:],axis=-1)
 # Proper segment crossings are forbidden between the two wall boundaries.
 c=inner[:-1];e=inner[1:]-c
 def cross(x,y):return x[...,0]*y[...,1]-x[...,1]*y[...,0]
 q=c[None,:,:]-a[:,None,:];den=cross(d[:,None,:],e[None,:,:]);safe=np.where(abs(den)>1e-15,den,1);u=cross(q,d[:,None,:])/safe;t=cross(q,e[None,:,:])/safe;crossings=int(((abs(den)>1e-15)&(t>0)&(t<1)&(u>0)&(u<1)).sum())
 r={'meridian_samples':len(outer),'outer_z_strictly_increasing':bool(np.all(np.diff(outer[:,1])>0)),'inner_z_strictly_increasing':bool(np.all(np.diff(inner[:,1])>0)),'wall_boundary_proper_intersections':crossings,'min_sampled_wall_to_outer_segments_m':float(distance.min()),'max_normal_offset_error_m':float(np.abs(np.linalg.norm(outer-inner,axis=1)-wall).max()),'minimum_inner_radius_m':float(inner[:,0].min())}
 assert r['outer_z_strictly_increasing'] and r['inner_z_strictly_increasing'] and not crossings and r['min_sampled_wall_to_outer_segments_m']>.00075 and r['max_normal_offset_error_m']<(1e-12 if exact_normal_offset else 1e-5),r
 return r
