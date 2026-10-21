"""Original station loft study: changing transverse crown/channel, finite wall.
SciPy monotone cubic station interpolation avoids invented oscillatory stations.
No holes/ribs/edgefinish yet, no source photograph texels or vendor mesh.
"""
from pathlib import Path
import numpy as np,json,hashlib
from scipy.interpolate import PchipInterpolator
H=Path(__file__).resolve().parent;P=json.loads((H/'parameters-study-v1.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def spline(key):
 a=np.array(P[key],float);return PchipInterpolator(a[:,0],a[:,1],extrapolate=True)
width=spline('stations_width_half_m');centre=spline('stations_centre_Z_m');edge=spline('stations_sideedge_Z_m');ymin,ymax=P['length_range_m'];us=np.linspace(-1,1,P['study_cross_samples']);ys=np.unique(np.round(np.concatenate([np.linspace(ymin,ymax,int(np.ceil((ymax-ymin)/P['study_max_Y_step_m']))+1),*[np.array(P[k])[:,0]for k in ['stations_width_half_m','stations_centre_Z_m','stations_sideedge_Z_m']]]),12));assert np.diff(ys).min()>.0009,'Intended millimetre stations must not become duplicate floating rows';U,Y=np.meshgrid(us,ys);ny,nu=U.shape
def smooth(q):q=np.clip(q,0,1);return q*q*q*(10+q*(-15+q*6))
def surface(u,y):
 blend=smooth((y-P['tray_to_canopy_blend_Y_m'][0])/np.diff(P['tray_to_canopy_blend_Y_m'])[0]);sh=P['shoulder_u_tray']+(P['shoulder_u_canopy']-P['shoulder_u_tray'])*blend;crow=P['canopy_transverse_crown_m_estimated']*blend;t=np.minimum(np.abs(u)/sh,1);q=np.clip((np.abs(u)-sh)/(1-sh),0,1);z=centre(y)-crow*t**4+(edge(y)-centre(y)+crow)*(q*q*(2-q));return np.stack([u*width(y),y,z],-1)
S=surface(U,Y);hu=1e-5;hy=1e-5;up=np.minimum(U+hu,1);um=np.maximum(U-hu,-1);yp=np.minimum(Y+hy,ymax);ym=np.maximum(Y-hy,ymin);du=(surface(up,Y)-surface(um,Y))/(up-um)[...,None];dy=(surface(U,yp)-surface(U,ym))/(yp-ym)[...,None];N=np.cross(du,dy);N/=np.linalg.norm(N,axis=-1,keepdims=True);assert np.all(N[:,:,2]>0)
th=P['wall_thickness_m_estimated'];V=np.concatenate([(S+N*th/2).reshape(-1,3),(S-N*th/2).reshape(-1,3)]);NN=np.concatenate([N.reshape(-1,3),-N.reshape(-1,3)]);count=ny*nu;F=[];roles=[]
for layer in range(2):
 off=layer*count
 for i in range(ny-1):
  for j in range(nu-1):
   a=off+i*nu+j;b=a+1;c=a+nu+1;d=a+nu;tri=[(a,b,c),(a,c,d)];F.extend(tri if layer==0 else[x[::-1]for x in tri]);roles.extend([layer]*2)
boundary=list(range(nu))+[i*nu+nu-1 for i in range(1,ny)]+[(ny-1)*nu+j for j in range(nu-2,-1,-1)]+[i*nu for i in range(ny-2,0,-1)];B=S.reshape(-1,3)[boundary];along=np.concatenate([[0],np.cumsum(np.linalg.norm(np.roll(B,-1,axis=0)-B,axis=1))]);wallUV=[]
for k,a in enumerate(boundary):
 b=boundary[(k+1)%len(boundary)];F.extend([(a,a+count,b+count),(a,b+count,b)]);roles.extend([2,2]);wallUV.extend([[(along[k],0),(along[k],th),(along[k+1],th)],[(along[k],0),(along[k+1],th),(along[k+1],0)]])
F=np.array(F,np.uint32);roles=np.array(roles,np.uint8);tri=V[F];cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);areas=np.linalg.norm(cross,axis=1)/2;assert areas.min()>1e-16,float(areas.min());volume=np.einsum('ij,ij->i',tri[:,0],cross).sum()/6;assert volume>0
base=roles<2;cn=cross[base]/np.linalg.norm(cross[base],axis=1,keepdims=True);target=NN[F[base]].mean(1);target/=np.linalg.norm(target,axis=1,keepdims=True);dots=np.einsum('ij,ij->i',cn,target);assert dots.min()>0,float(dots.min())
# Approximate physical cap charts: section arclength and centre longitudinal path.
across=np.concatenate([np.zeros((ny,1)),np.cumsum(np.linalg.norm(np.diff(S,axis=1),axis=-1),axis=1)],axis=1);long=np.concatenate([[0],np.cumsum(np.linalg.norm(np.diff(S[:,nu//2,:],axis=0),axis=-1))]);UV=np.stack([across,np.broadcast_to(long[:,None],U.shape)],-1).reshape(-1,2);UV=np.concatenate([UV,UV]);uv=UV[F];uv[roles==2]=np.array(wallUV);uv/=P['original_UV_reference_tile_m'];qa=uv[:,1]-uv[:,0];qb=uv[:,2]-uv[:,0];uarea=np.abs(qa[:,0]*qb[:,1]-qa[:,1]*qb[:,0]);assert uarea.min()>1e-14,float(uarea.min())
ns=NN[F];face=cross/np.linalg.norm(cross,axis=1,keepdims=True);ns[roles==2]=np.broadcast_to(face[roles==2,None,:],ns[roles==2].shape)
np.savez_compressed(H/'study-author-geometry-v1.npz',positions=V.astype(np.float32),triangles=F,loop_normals=ns.astype(np.float32),loop_UV=uv.astype(np.float32),roles=roles)
r={'component_id':P['component_id'],'revision':P['revision'],'stage':'Initial loft surface study before physical mouths/ribs/edgefinish','parameters_sha256':sha(H/'parameters-study-v1.json'),'generator_sha256':sha(Path(__file__)),'author_mesh_sha256':sha(H/'study-author-geometry-v1.npz'),'vertices':len(V),'triangles':len(F),'grid_shape':[ny,nu],'bounds_m':[V.min(0).tolist(),V.max(0).tolist()],'signed_wall_volume_m3':float(volume),'minimum_triangle_area_m2':float(areas.min()),'minimum_offset_triangle_target_normal_dot':float(dots.min()),'minimum_UV_doublearea':float(uarea.min()),'normal_offset_wall_m_estimated':th,'wall_is_not_a_filled_wheel_cavity':True,'UV_section_and_centre_arclength_scale_approximate':True,'mouths_built':False,'ribs_built':False,'edge_finishing_built':False,'component_complete':False,'hidden_underside_measured':False,'current_RDC_identity_verified':False,'all_metric_parameters_estimated':True,'global_3D_selfintersection_certified':False,'art_accepted':False};(H/'study-author-generation-v1.json').write_text(json.dumps(r,indent=2)+'\n');print('REAR_MUDGUARD_STUDY_AUTHOR',json.dumps(r))
