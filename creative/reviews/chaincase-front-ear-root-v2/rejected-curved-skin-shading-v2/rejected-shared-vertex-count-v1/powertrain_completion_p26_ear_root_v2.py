"""Corrective original inboard ear/root revision from four NEW opposed/inside physical views."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
from powertrain_continuation_loft_v4 import recalc,clean_smooth
R=Path(__file__).resolve().parents[1];name='chaincase-front-ear-root-v2';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
controls=[[-.011,.032],[.011,.032],[.011,.025],[.008,.018],[.0075,.010],[.008,.004],[.0085,0],[.00785,-.00325],[.006,-.006],[.00325,-.00785],[0,-.0085],[-.00325,-.00785],[-.006,-.006],[-.00785,-.00325],[-.0085,0],[-.008,.004],[-.0075,.010],[-.008,.018],[-.011,.025]]
P=dict(schema=1,package='P26',component_id='MOTO-CHAINCASE-FRONT-EAR-ROOT-002',source='creative/research/powertrain-completion-p26-v1/front-ear-root-plan-v74.json',outline_control_m=controls,sheet_normal_thickness_m=.0012,bore_radius_m=.0035,root_out_of_plane_offset_m=.009,root_transition_y_m=[.007,.026],all_dimensions_estimated=True,camera_calibrated=False,axis_certified=False,supersedes_for_review='chaincase-front-ear-study-v1 ALTERNATIVE ONLY, not second physical ear',scope='Corrective compact inboard ear/lobe and continuous formed root from four new used-BM150 physical poses, plain real through-hole and finite normal thickness. Removes old wide-flare/raised-seat interpretation. Upper root edge is explicit parent-interface review cut: actual weld/contact/three-wall-axis registration/currentRDC fit unqualified. Historical shell/known3wall holes and frozen v1 remain untouched; do not mount both revisions.',material=dict(name='Proposed clean silver painted inboard ear root',base_color_linear=[.43,.45,.47,1],metallic=0,roughness=.32),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);cs=list(map(Vector,controls));curve=[]
for i in range(len(cs)):
 p=[cs[(i+j)%len(cs)]for j in range(4)]
 for k in range(24):
  t=k/24;w=[(1-t)**3/6,(3*t**3-6*t*t+4)/6,(-3*t**3+3*t*t+3*t+1)/6,t**3/6];curve.append(sum((a*b for a,b in zip(p,w)),Vector((0,0))))
def cross(a,b):return a.x*b.y-a.y*b.x
N=256;M=64;radii=[]
for i in range(N):
 d=Vector((math.cos(math.tau*i/N),math.sin(math.tau*i/N)));hits=[]
 for a,b in zip(curve,curve[1:]+curve[:1]):
  e=b-a;den=cross(d,e)
  if abs(den)<1e-14:continue
  t=cross(a,e)/den;u=cross(a,d)/den
  if t>0 and -1e-8<=u<=1+1e-8:hits.append(t)
 assert len(hits)==1,(i,hits);radii.append(hits[0])
assert min(radii)>.006

def height(y):
 t=max(0,min(1,(y-.007)/.019));f=t*t*t*(10+t*(-15+6*t));dy=.009*30*t*t*(1-t)*(1-t)/.019 if 0<t<1 else 0
 return .009*f,Vector((0,-dy,1)).normalized()
V=[];F=[]
for side in [1,-1]:
 for k in range(M+1):
  t=k/M
  for i,outer in enumerate(radii):
   a=math.tau*i/N;r=.0035*(1-t)+outer*t;x,y=r*math.cos(a),r*math.sin(a);z,n=height(y);V.append(tuple(Vector((x,y,z))+n*(side*.0006)))
S=(M+1)*N
for k in range(M):
 a=k*N;b=a+N
 for i in range(N):
  j=(i+1)%N;F.extend([(a+i,b+i,b+j,a+j),(S+a+i,S+a+j,S+b+j,S+b+i)])
for i in range(N):
 j=(i+1)%N;a=M*N;F.extend([(a+i,S+a+i,S+a+j,a+j),(i,j,S+j,S+i)])
ob=mesh_object('COMPACT_INBOARD_EAR_PLAIN_BORE_CONTINUOUS_FORMED_ROOT',V,F);recalc(ob);clean_smooth(ob);ob['scope']=P['scope'];finish_source(H,O,P)
(O/'root-construction-check.json').write_text(json.dumps(dict(outline_method='Original periodic cubic B-spline; unique uniform-angle ray intersections prevent folded radial cells',angular_samples=N,radial_samples=M,minimum_outer_radius_m=min(radii),root_height_method='Analytic quintic C2 transition, zero first/second derivatives at both joins',normal_offset_each_side_m=.0006,scope='Constructed envelope continuity only, not real pressing/weld/metric fit',art_accepted=False),indent=2)+'\n')
