"""Original rounded finite-wall cup with analytic poles and open rounded mating rim."""
import bpy,sys,json,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
from powertrain_continuation_shapes_v2 import cyl,boolean
from powertrain_continuation_loft_v4 import clean_smooth,recalc,soft_cyl
R=Path(__file__).resolve().parents[1];name='carburettor-float-bowl-v2';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
P=dict(schema=1,package='P19',component_id='MOTO-CARBURETTOR-FLOAT-BOWL-001',source='creative/research/powertrain-completion-p19-v1/float-bowl-rework-plan-v10.json',outer_mouth_radii_m=[.0295,.0255],inner_mouth_radii_m=[.026,.022],outer_depth_m=.025,inner_depth_m=.022,rim_axial_rounding_m=.0015,all_dimensions_estimated=True,camera_calibrated=False,scope='New rounded finite-wall bowl: analytic convex outer and concave inner cup with true point poles, continuous tangent around finite annular rolled mouth; no arbitrary large planar closure disc/NGON. Rounded square mouth perturbation fades toward smooth poles. Hidden belly/cavity and exact source contour estimated, no actual galleries/float/gasket/body fit or artistic acceptance. Frozen v1 unchanged nonaccepted rework.',material=dict(name='Proposed bowl casting alloy v2',base_color_linear=[.31,.33,.35,1],metallic=.65,roughness=.43),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
N=192;K=72;rows=[]
for j in range(K-1,-1,-1):
 t=math.pi/2*j/K;rows.append((.040+.025*math.sin(t),.0295*math.cos(t),.0255*math.cos(t),.004*math.sin(t)**2,-.014-.004*math.sin(t)**2,math.cos(t)))
for j in range(1,48):
 p=math.pi*j/48;rows.append((.040-.0015*math.sin(p),.02775+.00175*math.cos(p),.02375+.00175*math.cos(p),0,-.014,1))
for j in range(K):
 t=math.pi/2*j/K;rows.append((.040+.022*math.sin(t),.026*math.cos(t),.022*math.cos(t),.004*math.sin(t)**2,-.014-.004*math.sin(t)**2,math.cos(t)))
V=[(.065,.004,-.018)];F=[]
for x,ry,rz,cy,cz,fade in rows:
 for j in range(N):
  a=math.tau*j/N;c,s=math.cos(a),math.sin(a);q=1-.045*math.cos(4*a)*fade**2
  V.append((x,cy+ry*c*q*(1+.045*c*fade+.015*math.sin(2*a)*fade**2),cz+rz*s*q))
for j in range(N):F.append((0,1+j,1+(j+1)%N))
for k in range(len(rows)-1):
 for j in range(N):F.append((1+k*N+j,1+k*N+(j+1)%N,1+(k+1)*N+(j+1)%N,1+(k+1)*N+j))
pole=len(V);V.append((.062,.004,-.018));base=1+(len(rows)-1)*N
for j in range(N):F.append((base+j,pole,base+(j+1)%N))
ob=mesh_object('ROUNDED_FLOAT_BOWL_FINITE_WALL_REAL_POLES_OPEN_ROLLED_RIM',V,F);recalc(ob)
for i,y in enumerate([-.028,.027]):
 boolean(ob,soft_cyl(cyl,(.0372,y,-.018),(.0447,y,-.018),.0055),'UNION','Visible bowl attachment '+str(i))
 boolean(ob,cyl((.032,y,-.018),(.046,y,-.018),.002),'DIFFERENCE','Attachment mouth '+str(i))
boolean(ob,soft_cyl(cyl,(.055,-.034,-.017),(.055,-.013,-.017),.006),'UNION','Lower observed connector seat')
boolean(ob,cyl((.055,-.050,-.017),(.055,.002,-.017),.003),'DIFFERENCE','Lower connector mouth')
clean_smooth(ob);ob['scope']=P['scope']
(O/'section-construction-check.json').write_text(json.dumps(dict(method='Analytic ellipsoidal cup walls, finite rolled annulus, two explicit point pole triangle fans',pre_boolean_rings=len(rows),samples_per_ring=N,pole_faces_each=N,arbitrary_ngon_closure_faces=0,section_tangent_joins='Outer/inner cup at t=0 and annular rim at phi=0/pi all axial tangent; curvature may change at real rolled rim transition',pole_regularization='Transverse shape perturbation fades to zero as cos(t)^2; no angular square singularity at poles',outer_pole_m=[.065,.004,-.018],inner_pole_m=[.062,.004,-.018],axial_floor_m=.003,source_cavity_certified=False,art_accepted=False),indent=2)+'\n');finish_source(H,O,P)
