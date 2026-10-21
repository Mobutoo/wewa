"""Documentary pixel extraction + conditional two-view camera exploration.
No image, model, material or registry is modified. No photo-to-mm calibration.
"""
import json,hashlib,math
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import label,binary_erosion,distance_transform_edt,map_coordinates
from scipy.spatial import ConvexHull
from scipy.optimize import least_squares
R=Path(__file__).resolve().parents[3];Q=Path(__file__).resolve().parent
G=json.loads(Path('/tmp/wewa-cowl-source3-points.json').read_text());points=np.array(G['points'],dtype=np.float64)[::3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def ellipse_dist(p,t):
 cx,cy,a,b,ang=t
 d=p-np.array([cx,cy]);ca,sa=math.cos(ang),math.sin(ang);x=ca*d[:,0]+sa*d[:,1];y=-sa*d[:,0]+ca*d[:,1]
 F=(x/a)**2+(y/b)**2-1;gradient=np.hypot(2*x/a**2,2*y/b**2)
 return F/np.maximum(gradient,1e-9)

def photo(n):
 p=Path('/workspace/wewa-assets/references/headlamp/cowl-black-'+n+'.jpg');a=np.array(Image.open(p).convert('RGB'));fits=[];chosen=None
 for threshold in [210,220,230,240]:
  labels,count=label(a.min(axis=2)>threshold);sizes=np.bincount(labels.ravel());order=np.argsort(sizes[1:])[::-1]+1
  # Largest white island away from image borders = aperture, not outside white.
  for i in order:
   y,x=np.where(labels==i)
   if x.min()>0 and y.min()>0 and x.max()<799 and y.max()<799 and len(x)>10000:break
  island=labels==i;boundary=np.argwhere(island&~binary_erosion(island))[:,::-1].astype(float);hull=boundary[ConvexHull(boundary).vertices]
  initial=[float(x.mean()),float(y.mean()),(x.max()-x.min())/2,(y.max()-y.min())/2,0.]
  result=least_squares(lambda v:ellipse_dist(hull,v),initial,bounds=([0,0,50,50,-.7],[800,800,400,400,.7]),loss='soft_l1',f_scale=1.5,max_nfev=200)
  residual=ellipse_dist(hull,result.x);record={'threshold_min_RGB':threshold,'white_aperture_area_px':int(len(x)),'bbox_xyxy_native_px':[int(x.min()),int(y.min()),int(x.max()),int(y.max())],'ellipse_cx_cy_a_b_angle_rad':result.x.tolist(),'convex_hull_points':len(hull),'hull_geometric_residual_RMS_px':float(np.sqrt(np.mean(residual**2))),'hull_max_abs_residual_px':float(abs(residual).max())};fits.append(record)
  if threshold==230:chosen=(result.x,hull,record)
 L,_=label(a.min(axis=2)<180);sizes=np.bincount(L.ravel());k=int(np.argmax(sizes[1:])+1);body=L==k;y,x=np.where(body);bodybox=[int(x.min()),int(y.min()),int(x.max()),int(y.max())]
 return {'path':str(p),'sha256':sha(p),'native_pixels':[800,800],'aperture_threshold_sensitivity':fits,'native_body_bbox_minRGB180':bodybox},chosen[0],chosen[1],distance_transform_edt(~body)

def project(p,d,elev,az,side,principal,roll,f):
 eye=np.array([math.cos(elev)*math.sin(az),side*math.cos(elev)*math.cos(az),math.sin(elev)])
 forward=-eye;right=np.cross(forward,[0.,0.,1.]);right/=np.linalg.norm(right);up=np.cross(right,forward)
 ca,sa=math.cos(roll),math.sin(roll);rr=right*ca+up*sa;uu=-right*sa+up*ca;depth=d-p@eye
 out=np.column_stack([principal[0]+f*(p@rr)/depth,principal[1]-f*(p@uu)/depth])
 return out,depth,(eye*d).tolist()

ang=np.linspace(0,math.tau,192,endpoint=False);radius=.10225;circle=np.column_stack([radius*np.sin(ang),np.zeros(len(ang)),radius*np.cos(ang)])
results=[]
for n,side in [('8494',-1),('8495',1)]:
 doc,target,hull,dist=photo(n);grid=[]
 for focal in [16,20,24,28,35,50,65]:
  f=focal*800/36
  for azimuth in [-25,-12.5,-7.5,0,7.5,12.5,25]:
   az=math.radians(azimuth)
   def residual(v):
    d,e,cx,cy,roll=v;p,_,_=project(circle,d,e,az,side,(cx,cy),roll,f)
    return ellipse_dist(p,target)
   ratio=min(.999,max(.05,target[3]/target[2]));initial=[f*radius/target[2],math.acos(ratio),target[0],target[1],math.pi]
   initial=np.maximum([.12001,.0301,100.001,100.001,math.pi-.699],np.minimum([1.9999,1.3999,699.999,699.999,math.pi+.699],initial))
   fit=least_squares(residual,initial,bounds=([.12,.03,100,100,math.pi-.7],[2.,1.4,700,700,math.pi+.7]),max_nfev=100,ftol=1e-10,xtol=1e-10,gtol=1e-10)
   d,e,cx,cy,roll=fit.x;p,depth,eye=project(points,d,e,az,side,(cx,cy),roll,f);valid=depth>.001;out=map_coordinates(dist,[p[:,1],p[:,0]],order=1,mode='constant',cval=800.);out[~valid]=800.;res=residual(fit.x)
   holdout,_,_=project(np.array([[0,.145,-.1165]]),d,e,az,side,(cx,cy),roll,f)
   grid.append({'focal_mm_render_assumption_sensor36mm':focal,'azimuth_degrees_render_assumption':azimuth,'eye_world_m_estimated':eye,'distance_to_front_origin_m_estimated':float(d),'elevation_degrees_estimated':math.degrees(e),'roll_degrees_estimated':math.degrees(roll),'principal_point_native_px_estimated':[float(cx),float(cy)],'aperture_conic_RMS_px':float(np.sqrt(np.mean(res**2))),'aperture_conic_max_abs_px':float(abs(res).max()),'projected_mesh_vertex_bbox_native_px':[float(p[:,0].min()),float(p[:,1].min()),float(p[:,0].max()),float(p[:,1].max())],'sampled_vertex_outside_black_mask_median_px':float(np.median(out)),'sampled_vertex_outside_black_mask_p95_px':float(np.quantile(out,.95)),'vertices_behind_or_before_nearclip_fraction':float((~valid).mean()),'central_rear_bridge_midpoint_proxy_projected_px':holdout[0].tolist(),'limits':'Outside-mask values are one-sided diagnostics with unbuilt pads/ribs/edge returns and threshold errors. Not a shape quality score or a camera/section measurement.'})
 grid.sort(key=lambda q:q['sampled_vertex_outside_black_mask_p95_px']);results.append({'photo':doc,'view_side_Y_sign_assumed':side,'camera_candidates':grid,'candidate_sort_is_camera_certification':False})
report={'schema':1,'source_geometry_file':G['file'],'source_geometry_export_sha256':G['sha256'],'source_geometry_changed':False,'sampled_actual_export_vertices':len(points),'assumed_front_clear_radius_m':radius,'radius_is_measured_RDC':False,'invalidated_manual_guides':[{'files':['rear-negative-spaces-plan-v2.json','rear-negative-spaces-plan-v3.json'],'field':'rear_scallops.coarse_manual_2D_guides_not_metric','reason':'Image padding/origin misread; ~190px Y error, original±8px bounds FALSE. Never used by recipes as calibration. Preserve as rejected history, never reuse.'},{'file':'central-keyhole-plan-v4.json','field':'coarse_native_guide.centre_px','reason':'Initial[400,55] is FALSE; actual openkeyhole near[394,244], native padding retained. No source4built.'}],'method':'White aperture island thresholds210..240; convex hull retainednative boundary, robust ellipse fit. Each view has an independent pinhole pose/focal-assumption sweep. Actual exported geometry projected without deformation. No camera principalpoint/crop/lensdistortion calibration or full contour fitting.','fixed_assumptions':['Sensor36mm is render convention, not known photographic sensor.','Eye azimuth fixedpergrid; rotation, distance and imageprincipalpoint fitted to the front conic only.','Projected centralpost is an unmeasured sourceproxy; actualrear mountingpost geometry still absent.','No inter-view physical scale or OEMdimension recovered.'],'fitted_conic_residual_is_not_native_photo_accuracy':True,'native_boundary_limits':'Convexhull is affected by occludingpads, thresholds, lens/crop and possiblegeometryvariante. Fittedconic errors nearzero only reproduce the estimatedellipse, not the truepixel contour. Thresholds do not bound allerrors.','two_actual_photos':results,'art_accepted':False}
(Q/'native-camera-exploration-v1.json').write_text(json.dumps(report,indent=2)+'\n')
for r in results:
 print(r['photo']['path']);print('ellipse',r['photo']['aperture_threshold_sensitivity'][2]);print('best_one_sided',r['camera_candidates'][:2])
