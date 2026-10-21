"""Image-space working ellipse normalisation; no recovered metric camera."""
from pathlib import Path
import json,hashlib,numpy as np
from scipy.optimize import least_squares
HERE=Path(__file__).resolve().parent
points=np.array([[353,395],[382,398],[410,412],[430,435],[438,464],[435,489],[418,512],[392,526],[363,533],[332,528],[304,514],[285,494],[277,468],[281,442],[297,419],[324,402]],float)
def residual(p):
 cx,cy,a,b,theta=p;c=np.cos(theta);s=np.sin(theta);d=points-[cx,cy];x=d[:,0]*c+d[:,1]*s;y=-d[:,0]*s+d[:,1]*c;F=(x/a)**2+(y/b)**2-1;return F/np.maximum(2*np.sqrt(x*x/a**4+y*y/b**4),1e-8)
r=least_squares(residual,[358,464,82,68,.04]);cx,cy,a,b,theta=r.x;c=np.cos(theta);s=np.sin(theta)
# U points to screen-right, V upward in the photographed face. Unknown affine
# foreshortening is removed; exact perspective/lens distortion is not recovered.
U=np.array([a*c,a*s]);V=np.array([b*s,-b*c]);A=np.column_stack([U,V]);anchors=[(40,[283.5,442.25]),(60,[320,406.25]),(80,[377,397.75]),(100,[425.5,427.75]),(120,[437.5,473]),(140,[417.5,506.5])];deltas=[]
for speed,point in anchors:
 q=np.linalg.solve(A,np.array(point)-[cx,cy]);ang=np.degrees(np.arctan2(q[1],q[0]));old=225-speed*270/140;deltas.append((ang-old+180)%360-180)
offset=float(np.median(deltas));rot=np.deg2rad(offset);rotmat=np.array([[np.cos(rot),-np.sin(rot)],[np.sin(rot),np.cos(rot)]]);pixel_from_face_unit=A@rotmat;M=np.eye(3);M[:2,:2]=pixel_from_face_unit;M[:2,2]=[cx,cy]
rows=[]
for (speed,point),delta in zip(anchors,deltas):rows.append({'value_kmh':speed,'native_outer_mark_anchor_px_approx':point,'reading_uncertainty_px':3,'working_angle_error_after_median_rotation_degrees':float(delta-offset)})
report={'schema':1,'reference_private_path':'/workspace/wewa-assets/references/instruments/official-rdc-usb-meter.png','reference_sha256':'eb8e10531cbd7f37c1825044a535c07a8549872975440233d86d581b6e3c2663','native_size_px':[1000,600],'method':'Manual outer printed dial-boundary native landmarks, geometric ellipse fit, affine circle normalisation. Working in-plane rotation from six visible major marks relative to existing numerical-angle convention. No metric or projective camera is recovered.','landmarks_native_px':points.tolist(),'landmark_uncertainty_px_working':3,'ellipse_centre_px':[float(cx),float(cy)],'ellipse_semiaxes_px':[float(a),float(b)],'ellipse_rotation_degrees':float(np.degrees(theta)),'ellipse_geometric_residuals_px_approx':residual(r.x).tolist(),'max_ellipse_residual_px_approx':float(abs(residual(r.x)).max()),'working_face_unit_to_native_matrix':M.tolist(),'working_native_to_face_unit_matrix':np.linalg.inv(M).tolist(),'working_rotation_offset_degrees':offset,'outer_printed_radius_working_m':.0415,'radius_is_estimated_not_measured':True,'anchor_diagnostics':rows,'deliberately_not_fit':{'0':'Partially obscured by needle; exact tip/footprint reading unreliable','20':'Outer wedge/tip ambiguous at native pixels; excluded from rotation gauge'},'uses':['Local artwork footprint and band-width comparisons on the speed face only'],'not_valid_for':['Absolute dimensions','Whole cluster camera fit','USB plane or two-pod spacing correction','Lens thickness/curvature','A new speed/needle calibration'],'numeric_angular_positions_and_needle_pivots_will_be_preserved':True,'scope_limit':'The ellipse and rotation fit are a working shape comparison, not independent confirmation of the current v1 angular convention. Small local differences are retained as uncertainty.','art_accepted':False}
(HERE/'speed-dial-calage.json').write_text(json.dumps(report,indent=2)+'\n');print('DIAL_CALAGE',report['max_ellipse_residual_px_approx'],offset,'major angle residuals',[round(x['working_angle_error_after_median_rotation_degrees'],2)for x in rows])
