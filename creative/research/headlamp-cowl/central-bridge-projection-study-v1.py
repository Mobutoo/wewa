"""Conditional cross-view shape exploration, NOT measured triangulation."""
from pathlib import Path
import json,math,ast,hashlib
import numpy as np
from PIL import Image
from scipy.optimize import least_squares
Q=Path(__file__).resolve().parent
j=json.loads((Q/'native-camera-exploration-v1.json').read_text())
tree=ast.parse((Q/'native-camera-exploration-v1.py').read_text())
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='project')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'read-only-projection','exec'))
T=[];native=[]
for n,box in [('8494',[380,271,401,284]),('8495',[380,237,405,251])]:
 p=Path('/workspace/wewa-assets/references/headlamp/cowl-black-'+n+'.jpg')
 a=np.array(Image.open(p).convert('RGB'));x0,y0,x1,y1=box;centres=[]
 for threshold in [210,220,230,240]:
  y,x=np.where(a[y0:y1,x0:x1].min(axis=2)>threshold)
  centres.append({'threshold':threshold,'white_pixels':len(x),'native_ROI_white_moment_px':[float(x.mean()+x0),float(y.mean()+y0)]})
 T.append(np.array(centres[2]['native_ROI_white_moment_px']))
 native.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'ROI_xyxy_native_px':box,'threshold_centroids':centres,'meaning':'Visible white part of the small open keyhole, not a calibrated 3Dcircle centre. ROI truncation, neck, bevel and occlusion errors unbounded by threshold sensitivity.'})
rows=[]
for f1 in [24,50]:
 for f2 in [24,50]:
  for az1 in [0,7.5,12.5]:
   for az2 in [-12.5,-7.5,0]:
    cc=[]
    for view,f,az in zip(j['two_actual_photos'],[f1,f2],[az1,az2]):
     cc.append((next(c for c in view['camera_candidates']if c['focal_mm_render_assumption_sensor36mm']==f and c['azimuth_degrees_render_assumption']==az),view['view_side_Y_sign_assumed']))
    def fun(v):
     out=[]
     for (c,side),target in zip(cc,T):
      xy,_,_=project(np.array([v]),c['distance_to_front_origin_m_estimated'],math.radians(c['elevation_degrees_estimated']),math.radians(c['azimuth_degrees_render_assumption']),side,c['principal_point_native_px_estimated'],math.radians(c['roll_degrees_estimated']),c['focal_mm_render_assumption_sensor36mm']*800/36)
      out.extend(xy[0]-target)
     return out
    fit=least_squares(fun,[0,.08,-.13],bounds=([-.03,-.03,-.20],[.03,.20,-.05]));res=np.array(fun(fit.x))
    rows.append({'focals_mm_assumed':[f1,f2],'azimuths_degrees_assumed':[az1,az2],'conditional_point_Blender_xyz_m':fit.x.tolist(),'reprojection_RMS_px':float(np.sqrt(np.mean(res**2))),'reprojection_max_abs_px':float(abs(res).max()),'same_axes_as_component':True,'physical_dimensions_measured':False})
chosen=[r for r in rows if r['azimuths_degrees_assumed']==[7.5,-7.5]];allp=np.array([r['conditional_point_Blender_xyz_m']for r in rows]);cp=np.array([r['conditional_point_Blender_xyz_m']for r in chosen]);out={'schema':1,'native_features':native,'camera_exploration_sha256':hashlib.sha256((Q/'native-camera-exploration-v1.json').read_bytes()).hexdigest(),'fixed_pose_family_four_focal_combinations':chosen,'fixed_pose_family_xyz_bounds_m':[cp.min(axis=0).tolist(),cp.max(axis=0).tolist()],'all_36_unverified_pose_and_focal_combinations':rows,'all_unverified_family_xyz_bounds_m':[allp.min(axis=0).tolist(),allp.max(axis=0).tolist()],'bounds_are_confidence_intervals':False,'scope':'Conditional scaled point under unverified pinhole poses, assumedfront circle radius102.25mm and possiblebias from occluded aperture. A small residual is not a measuredpoint/camera/shape proof. Do not adopt as exactOEM value.','effect_on_next_candidate':'Existing centralrear Y145mm does not explain both views under the displayedpose/focal family. Explore a much shorter centralreturn and larger bottomradius, while separately flaring the lateralreturn; leave actual mounting geometry/dimensions open. Use intervals and rerender bothviews, never deform to onecamera alone.','source_changed':False,'art_accepted':False}
(Q/'central-bridge-projection-study-v1.json').write_text(json.dumps(out,indent=2)+'\n')
print('FIXED',out['fixed_pose_family_xyz_bounds_m']);print('ALL',out['all_unverified_family_xyz_bounds_m'])
