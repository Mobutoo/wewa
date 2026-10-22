"""Original lower LH access neck, finite visible thread zone; no cap or hidden gallery."""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source,bounds
from powertrain_continuation_loft_v4 import clean_smooth
R=Path(__file__).resolve().parents[1];name='crankcase-lh-lower-service-port-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
planpath='creative/research/powertrain-completion-p18-v1/lh-lower-service-port-plan-v91.json';plan=json.loads((R/planpath).read_text());P=dict(schema=1,package='P18',component_id=plan['component_id'],source=planpath,scope=plan['scope'],variant=plan['variant'],all_dimensions_estimated=True,camera_calibrated=False,working_bore_radius_m=.0145,working_thread_pitch_m=.0015,working_thread_height_m=.00045,visible_thread_zone_m=[-.009,-.001],thread_hand='Working right-hand, not certified from uncalibrated source',hidden_passage='Finite rear review cut, not inferred gallery',material=dict(name='Proposed clean cast aluminium service neck',base_color_linear=[.33,.35,.37,1],metallic=.7,roughness=.44),package_complete=False,art_accepted=False)
# Periodic C2 annular profile: Z, radius, inner-visible-thread mask, rear-root asymmetry mask.
C=[[.001,.0208,0,0],[0,.0215,0,0],[-.002,.0215,0,0],[-.006,.0218,0,0],[-.012,.0224,0,.25],[-.020,.0245,0,.6],[-.027,.0255,0,1],[-.028,.0255,0,1],[-.028,.022,0,.6],[-.028,.018,0,0],[-.028,.0148,0,0],[-.026,.0145,0,0],[-.020,.0145,0,0],[-.014,.0145,0,0],[-.010,.0145,0,0],[-.009,.0145,1,0],[-.006,.0145,1,0],[-.003,.0145,1,0],[-.001,.0145,1,0],[0,.0145,0,0],[.001,.015,0,0],[.001,.017,0,0],[.001,.019,0,0]]
P['meridian_controls_z_radius_thread_root']=C;(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
def spline(i,t):
 p=[Vector(C[(i+j)%len(C)])for j in range(4)];w=[(1-t)**3/6,(3*t**3-6*t*t+4)/6,(-3*t**3+3*t*t+3*t+1)/6,t**3/6];return sum((a*b for a,b in zip(p,w)),Vector((0,0,0,0)))
curves=[spline(i,j/36)for i in range(len(C))for j in range(36)];N=256;V=[];F=[]
for z,r,inner,root in curves:
 for j in range(N):
  a=math.tau*j/N;phase=a-math.tau*z/.0015;thread=.00045*((1+math.cos(phase))/2)**4*inner;asym=.003*root*(.5+.5*math.sin(a));rr=r-thread+asym;V.append((rr*math.cos(a),rr*math.sin(a),z))
for k in range(len(curves)):
 for j in range(N):F.append((k*N+j,k*N+(j+1)%N,((k+1)%len(curves))*N+(j+1)%N,((k+1)%len(curves))*N+j))
ob=mesh_object('LH_LOWER_SERVICE_ACCESS_NECK_VISIBLE_SHORT_INNER_HELIX',V,F);clean_smooth(ob);ob['scope']=P['scope'];finish_source(H,O,P)
bpy.context.scene.camera.data.ortho_scale=bounds()[1]*2.15;bpy.ops.wm.save_as_mainfile(filepath=str(H/'child-gray.blend'),compress=True);d=json.loads((O/'geometry-check.json').read_text());d['source_sha256']=hashlib.sha256((H/'child-gray.blend').read_bytes()).hexdigest();d['whole_camera_size_ratio']=2.15;(O/'geometry-check.json').write_text(json.dumps(d,indent=2)+'\n')
(O/'port-construction-check.json').write_text(json.dumps(dict(method='Original C2 annular cast-neck meridian, mild bounded root asymmetry; continuous actual inner helical relief masked to visible mouth zone only',axial_meridian_samples=len(curves),angular_samples=N,working_pitch_m=.0015,actual_threaded_geometry=True,cap_disc=False,hidden_gallery=False,scope='Near-mouth morphology and visible thread study only; true pitch/hand/fit/hidden end unqualified'),indent=2)+'\n')
