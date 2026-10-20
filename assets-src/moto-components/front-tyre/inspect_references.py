"""Read-only contour observations from original documentary files, not calibrated CAD."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.optimize import least_squares

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=Path('/workspace/wewa-assets/references/dimensions-verified')
settings=[('rotation-00.png','front',690,905),('rotation-00.png','rear',145,365),('rotation-04.png','front',95,320),('rotation-04.png','rear',640,855)]
observations=[]
for filename,wheel,x0,x1 in settings:
 p=BASE/filename
 a=np.array(Image.open(p).convert('RGBA'))
 pts=[]
 for x in range(x0,x1,4):
  column=a[:,x]
  candidates=np.where((column[:,3]>235)&(column[:,:3].mean(axis=1)<120)&(np.arange(len(column))>540)&(np.arange(len(column))<640))[0]
  if len(candidates):pts.append([x,int(candidates.max())])
 pts=np.array(pts)
 fit=least_squares(lambda q:np.linalg.norm(pts-q[:2],axis=1)-q[2],[(x0+x1)/2,490,122],loss='soft_l1')
 observations.append({'image':filename,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'wheel':wheel,
  'method':'Bottom-most high-alpha neutral-dark pixel in restricted visible lower arc; robust circle fit as diagnostic only',
  'roi':{'x':[x0,x1],'y':[540,640]},'observed_points_px':pts.tolist(),
  'diagnostic_circle_cx_cy_radius_px':fit.x.tolist(),
  'fit_residual_rms_px':float(np.sqrt(np.mean(fit.fun**2))),
  'working_contour_uncertainty_px':2,
  'uncertainty_note':'Working minimum allowance for masks/compression and segmentation; not statistical camera calibration confidence',
  'limitations':['Wheel projection not proven circular','Occlusion and cut-out artefacts','Fitting only lower arc can bias centre and radius','Hub centre not measured by this fit']})
report={'schema':1,'observations':observations,
 'known_constraint':{'wheelbase_m':1.285,'source':'RDC manufacturer specification'},
 'camera_status':'Not calibrated: focal length, commercial crop and pose unresolved',
 'dimensional_status':'No uniform pixel-to-millimetre conversion adopted',
 'tyre_candidate':'Outside diameter0.580m and width0.071m remain bounded working estimates in parameters.json',
 'comparison_protocol':{'side':'Orthographic geometric inspection at known working scale, not a solved documentary camera','quarter':'Matched studio cameras for neutral/cinematic material comparison, not calibration to an official photo','next':'Fit wheel/axle and other independent landmarks across views before adopting exact vehicle shape'},
 'manufacturer_photographs_republished':False,'original_images_edited':False,'geometric_fidelity_certified':False}
(HERE/'reference-observations.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'arcs_observed':len(observations),'original_images_edited':False,'photo_cameras_calibrated':False}))
