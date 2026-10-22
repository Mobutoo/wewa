"""CL201023 observed metal base exterior only; no hidden interior or flange duplicate."""
import bpy,runpy,math,json
from pathlib import Path
R=Path('/workspace/wewa');K='front-completion-p06-bulb-base-front16-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K
H.mkdir(exist_ok=False);O.mkdir(exist_ok=False);bpy.ops.wm.read_factory_settings(use_empty=True)
u=runpy.run_path(str(R/'tools/front_completion_front10_mesh_helpers_v1.py'));N=256
# Outside contour from opposite oblique supplier photographs; all values estimated.
# No inward return at review cuts: this is an exterior skin, not an invented sheet section.
profile=[(.0140,-.0070),(.0143,-.0066),(.0145,-.0060),(.0145,-.0040),(.0143,-.0034),(.0136,-.0030),(.0125,-.0025),(.0120,-.0018),(.0118,-.0010),(.0118,.0028),(.0120,.0035),(.0126,.0040),(.0133,.0045),(.0136,.0050),(.0136,.0055),(.0132,.0059),(.0125,.0062),(.0094,.0062)]
v=[(r*math.cos(2*math.pi*j/N),r*math.sin(2*math.pi*j/N),z)for r,z in profile for j in range(N)];f=[]
for i in range(len(profile)-1):
 for j in range(N):a=i*N+j;b=i*N+(j+1)%N;f.append((a,b,b+N,a+N))
ob=u['mesh_object']('CL201023_OBSERVED_STEPPED_METAL_BASE_OUTSIDE_SKIN_ONLY',v,f);u['orient'](ob);audit=u['clean_audit'](ob,expected_boundary=2*N)
for q in ob.data.polygons:
 if abs(q.normal.z)>.999999:q.use_smooth=False
params={'package':'P06','code':'CL201023','source':'Crosland poses0and2 opposite oblique, pose1 front, OSRAM product front class crosscheck','scope':'Single observed stepped metal base exterior skin, not locating flange, glass, insulator, contacts or internal joining. Two intentional open review cuts at rear and capsule mouth. Observed local mouth crimp cuts omitted pending local contour study, not silently repeated around circumference.','profile_r_z_m':profile,'all_working_dimensions_estimated':True,'bounds_m':{'maximum_radius':[.012,.016],'axial_span':[.010,.017],'mouth_cut_radius':[.008,.011]},'inference':'Axially symmetric smooth envelope constrained by opposite source silhouettes, local stamped irregularities excluded explicitly','hidden_inner_wall':'unknown and not fabricated','material':'Clean silver appearance hypothesis, no target plating or roughness measured','mounted_fit':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(params,indent=2));(O/'geometry-check.json').write_text(json.dumps({'objects':[audit],'boundary_loop_count':2,'expected_boundary_edges':512,'not_a_closed_sheet_solid':True},indent=2))
(O/'child-plan.json').write_text(json.dumps({'package':'P06','component_id':'MOTO-HS1-BULB-BASE-CL201023-OUTER-STUDY-001','child':'CL201023 stepped metal bulb-base exterior envelope','scope':params['scope'],'protocols':['front_completion_p06_bulb_base_front16_v1.py','front_completion_front10_mesh_helpers_v1.py','front_completion_front14_render_v1.py','front_completion_front10_material_v1.py'],'remaining':['Hidden sheet section and joins','Local mouth crimp-slot contours, not full rotational repetition','Calibrated dimensions and actual socket fit']},indent=2))
u['gray_save'](H,'bulb-base',[ob])
