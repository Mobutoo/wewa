"""Original relatedcuff interpretation; all sectionmetrics are author estimates."""
import math,numpy as np

def profiles(p,length):
 lower=p['lower_cuff_length_m'];start=lower+p['lower_transition_length_m'];end=length-p['upper_transition_length_m']-p['upper_cuff_length_m'];upper=length-p['upper_cuff_length_m'];top=length-p['upper_roundlip_axial_radius_m_estimated'];bottom=p['lower_mouth_endpoint_z_m'];pitch=(end-start)/p['fold_count_working'];assert pitch>0
 zs=sorted(set([bottom+(lower-bottom)*i/32 for i in range(33)]+[p['lower_entry_throat_end_z_m']+(p['lower_inner_chamber_start_z_m']-p['lower_entry_throat_end_z_m'])*i/p['lower_inner_step_samples']for i in range(p['lower_inner_step_samples']+1)]))
 for a,b,n in[(lower,start,48),(start,end,p['fold_count_working']*p['meridian_steps_per_fold']),(end,upper,36),(upper,top,24)]:zs.extend(a+(b-a)*i/n for i in range(1,n+1))
 outer=[];inner=[];thickness=[];wall=p['fold_wall_working_m'];cuff=p['cuff_wall_working_m'];valley=p['valley_radius_m'];crest=p['crest_radius_m'];seatwall=p['lower_cuff_outer_radius_m']-p['lower_inner_chamber_radius_m']
 def transition(z,a,b,r0,r1,t0,t1):
  t=(z-a)/(b-a);f=.5*(1-math.cos(math.pi*t));return r0+(r1-r0)*f,(r1-r0)*.5*math.pi/(b-a)*math.sin(math.pi*t),t0+(t1-t0)*f
 for z in zs:
  if z<=lower:
   r=p['lower_cuff_outer_radius_m'];dr=0;a=p['lower_entry_throat_end_z_m'];b=p['lower_inner_chamber_start_z_m'];t=max(0,min(1,(z-a)/(b-a)));f=.5*(1-math.cos(math.pi*t));ir=p['lower_cuff_opening_working_m']/2+(p['lower_inner_chamber_radius_m']-p['lower_cuff_opening_working_m']/2)*f;th=r-ir
  elif z<start:r,dr,th=transition(z,lower,start,p['lower_cuff_outer_radius_m'],valley,seatwall,wall)
  elif z<=end:
   phase=(z-start)/pitch;r=valley+(crest-valley)*.5*(1-math.cos(math.tau*phase));dr=(crest-valley)*math.pi/pitch*math.sin(math.tau*phase);th=wall
  elif z<upper:r,dr,th=transition(z,end,upper,valley,p['upper_cuff_outer_radius_m'],wall,cuff)
  else:r,dr,th=p['upper_cuff_outer_radius_m'],0,cuff
  norm=math.sqrt(1+dr*dr);outer.append([r,z]);inner.append([r-th/norm,z+th*dr/norm]);thickness.append(th)
 return np.array(outer),np.array(inner),np.array(thickness)

def validate_profile(outer,inner,wall,exact_normal_offset=True):
 a=outer[:-1];b=outer[1:];d=b-a;v=inner[:,None,:]-a[None,:,:];t=np.clip((v*d[None,:,:]).sum(-1)/(d*d).sum(-1)[None,:],0,1);distance=np.linalg.norm(v-t[:,:,None]*d[None,:,:],axis=-1);c=inner[:-1];e=inner[1:]-c
 def cross(x,y):return x[...,0]*y[...,1]-x[...,1]*y[...,0]
 q=c[None,:,:]-a[:,None,:];den=cross(d[:,None,:],e[None,:,:]);safe=np.where(abs(den)>1e-15,den,1);u=cross(q,d[:,None,:])/safe;t=cross(q,e[None,:,:])/safe;crossings=int(((abs(den)>1e-15)&(t>0)&(t<1)&(u>0)&(u<1)).sum());r={'meridian_samples':len(outer),'outer_z_strictly_increasing':bool(np.all(np.diff(outer[:,1])>0)),'inner_z_strictly_increasing':bool(np.all(np.diff(inner[:,1])>0)),'wall_boundary_proper_intersections':crossings,'min_sampled_wall_to_outer_segments_m':float(distance.min()),'max_normal_offset_error_m':float(np.abs(np.linalg.norm(outer-inner,axis=1)-wall).max()),'minimum_inner_radius_m':float(inner[:,0].min())}
 assert r['outer_z_strictly_increasing']and r['inner_z_strictly_increasing']and not crossings and r['min_sampled_wall_to_outer_segments_m']>.00075 and r['max_normal_offset_error_m']<(1e-12 if exact_normal_offset else 1e-5),r
 return r

def chaikin(points,iterations):
 q=np.array(points,dtype=float)
 for _ in range(iterations):
  out=[q[0]]
  for a,b in zip(q[:-1],q[1:]):out.extend([.75*a+.25*b,.25*a+.75*b])
  out.append(q[-1]);q=np.array(out)
 return q

def meridian(p,length):
 outer,inner,wall=profiles(p,length);top=length-p['upper_roundlip_axial_radius_m_estimated'];rad=(outer[-1,0]-inner[-1,0])/2;centre=(outer[-1,0]+inner[-1,0])/2;upper=np.array([[centre+rad*math.cos(math.pi*k/p['upper_roundlip_steps']),top+p['upper_roundlip_axial_radius_m_estimated']*math.sin(math.pi*k/p['upper_roundlip_steps'])]for k in range(1,p['upper_roundlip_steps'])]);lower=chaikin(p['lower_return_profile_anchors_rz_m'],p['lower_return_refinement_iterations']);assert np.allclose(lower[0],inner[0])and np.allclose(lower[-1],outer[0]);allpoints=np.concatenate([outer,upper,inner[::-1],lower[1:-1]]);lower_start=len(outer)+len(upper)+len(inner)
 return {'outer':outer,'inner':inner,'wall':wall,'meridian':allpoints,'lower_lip_start_ring':lower_start,'outer_rings':len(outer),'upper_lip_rings':len(upper),'lower_lip_rings':len(lower)-2}

def shape_vertices(p,length):
 d=meridian(p,length);mer=d['meridian'];N=p['radial_segments'];phi=np.arange(N)*math.tau/N;z=np.broadcast_to(mer[:,1,None],(len(mer),N)).copy();count=p['lower_local_radial_bridge_count_working'];width=math.radians(p['lower_bridge_full_angle_width_deg_estimated'])/2;angle=(phi-p['lower_bridge_phase_rad_estimated']+math.pi/count)%(math.tau/count)-math.pi/count;angular=np.where(abs(angle)<width,.5*(1+np.cos(math.pi*np.clip(angle/width,-1,1))),0)
 # Source bridge vertices are distributed by liparc before filling verticalwalls.
 # Merely lowering Z would collapse same-radius samples, so R is reparameterized
 # inside the groove only; mouth/outerbody boundaries stay unchanged.
 radial=np.broadcast_to(mer[:,0,None],(len(mer),N)).copy();ids=np.arange(d['lower_lip_start_ring'],len(mer));selected=ids[(mer[ids,0]>=.02410)&(mer[ids,0]<=.02570)];liparc=np.concatenate([[0],np.cumsum(np.linalg.norm(np.diff(mer[selected],axis=0),axis=1))]);mapped=mer[selected[0],0]+(mer[selected[-1],0]-mer[selected[0],0])*liparc/liparc[-1]
 for k,rr in zip(selected,mapped):radial[k]+=(rr-mer[k,0])*angular
 for k in range(d['lower_lip_start_ring'],len(mer)):
  zz=mer[k,1];depth=max(0,zz-p['lower_bridge_floor_z_m']);blend=min(1,depth/.0001);depth*=blend*blend*(3-2*blend);z[k]-=depth*angular
 vertices=np.stack([radial*np.cos(phi),radial*np.sin(phi),z],axis=-1).reshape(-1,3);d['vertices']=vertices;d['ring_z_by_angle']=z;d['phi']=phi;return d

def validate_closed_meridian(rz):
 a=rz;b=np.roll(rz,-1,axis=0);d=b-a;length=np.linalg.norm(d,axis=1);q=a[None,:,:]-a[:,None,:]
 def cross(x,y):return x[...,0]*y[...,1]-x[...,1]*y[...,0]
 den=cross(d[:,None,:],d[None,:,:]);safe=np.where(abs(den)>1e-15,den,1);t=cross(q,d[None,:,:])/safe;u=cross(q,d[:,None,:])/safe;hit=(abs(den)>1e-15)&(t>1e-8)&(t<1-1e-8)&(u>1e-8)&(u<1-1e-8);crossings=int(np.triu(hit,1).sum());area=float(np.sum(a[:,0]*b[:,1]-a[:,1]*b[:,0])/2);r={'rings':len(rz),'minimum_segment_length_m':float(length.min()),'proper_self_intersections':crossings,'signed_meridian_area_m2':area};assert length.min()>1e-9 and not crossings and area>0,r;return r
