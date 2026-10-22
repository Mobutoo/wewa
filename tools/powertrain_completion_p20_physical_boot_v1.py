"""Original finite boot revision based on actual assembled PF581003 airbox photographs."""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source,bounds
from powertrain_continuation_loft_v4 import clean_smooth
R=Path(__file__).resolve().parents[1];name='airbox-carb-boot-physical-study-v2';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
planpath='creative/research/powertrain-completion-p20-v1/physical-airbox-boot-plan-v81.json';plan=json.loads((R/planpath).read_text());P=dict(schema=1,package='P20',component_id=plan['component_id'],source=planpath,all_dimensions_estimated=True,camera_calibrated=False,scope=plan['scope'],alternative_to=plan['alternative_to'],working_length_m=.060,working_wall_m=.0025,shallow_band_centres_m=[-.012,.009],visible_near_land_angles_rad=[.1,1.1],hidden_land_count='Unknown: do not repeat inferred lands on far side',material=dict(name='Proposed clean dark intake rubber',base_color_linear=[.012,.014,.017,1],metallic=0,roughness=.58),package_complete=False,art_accepted=False)
# Closed C2 meridian wraps the finite wall, never spanning either mouth with a cap.
# Triples are axial station X, radius and physical outer-surface mask.
C=[[-.030,.0188,0],[-.030,.020,1],[-.0285,.020,1],[-.026,.020,1],[-.022,.0202,1],[-.017,.0208,1],[-.012,.0213,1],[-.006,.0218,1],[.001,.0224,1],[.008,.023,1],[.014,.0235,1],[.019,.0235,1],[.022,.0235,1],[.023,.0255,1],[.0245,.027,1],[.028,.027,1],[.030,.027,1],[.030,.0257,0],[.030,.0245,0],[.028,.0245,0],[.025,.0245,0],[.024,.023,0],[.021,.021,0],[.017,.021,0],[.010,.0205,0],[.003,.020,0],[-.005,.0193,0],[-.012,.0188,0],[-.020,.0178,0],[-.026,.0175,0],[-.030,.0175,0]]
P['meridian_control_m_outer_mask']=C;(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
def spline(i,t):
 p=[Vector(C[(i+j)%len(C)])for j in range(4)];w=[(1-t)**3/6,(3*t**3-6*t*t+4)/6,(-3*t**3+3*t*t+3*t+1)/6,t**3/6];return sum((a*b for a,b in zip(p,w)),Vector((0,0,0)))
def bump(q):return math.exp(-q*q*q*q) if abs(q)<3 else 0
curves=[spline(i,j/20)for i in range(len(C))for j in range(20)];N=192;V=[];F=[]
for x,r,outer in curves:
 for j in range(N):
  a=math.tau*j/N;band=.0011*sum(bump((x-c)/.0025)for c in [-.012,.009]);axial=bump((x+.003)/.019)
  land=.0007*axial*sum(bump(math.atan2(math.sin(a-c),math.cos(a-c))/.10)for c in [.1,1.1]);rr=r+outer*(band+land);V.append((x,rr*math.cos(a),rr*math.sin(a)))
for k in range(len(curves)):
 for j in range(N):F.append((k*N+j,k*N+(j+1)%N,((k+1)%len(curves))*N+(j+1)%N,((k+1)%len(curves))*N+j))
ob=mesh_object('PHYSICAL_SHORT_TAPER_BOOT_TWO_SHALLOW_BANDS_VISIBLE_NEAR_LANDS',V,F);clean_smooth(ob);ob['scope']=P['scope'];finish_source(H,O,P)
# Chunky annular geometry needs a wider whole-part frame in the fixed oblique protocol.
bpy.context.scene.camera.data.ortho_scale=bounds()[1]*2.15
bpy.ops.wm.save_as_mainfile(filepath=str(H/'child-gray.blend'),compress=True)
check=json.loads((O/'geometry-check.json').read_text());check['source_sha256']=hashlib.sha256((H/'child-gray.blend').read_bytes()).hexdigest();check['whole_camera_size_ratio']=2.15;(O/'geometry-check.json').write_text(json.dumps(check,indent=2)+'\n')
(O/'boot-construction-check.json').write_text(json.dumps(dict(method='Original periodic cubic meridian finite annular wall, two analytic shallow outer shoulders, two observed-side smooth moulding lands; mask excludes interior',meridian_samples=len(curves),angular_samples=N,cap_faces=False,hidden_airbox_end='Explicit finite review trim only; actual hidden retention unbuilt',scope='Photographed exterior study; C2 construction is not a fit or complete hidden section claim'),indent=2)+'\n')
