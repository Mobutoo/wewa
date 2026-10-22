"""Original DH161146 thin sleeve exterior; far mouth is explicit open review assumption."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
from powertrain_continuation_loft_v4 import clean_smooth,recalc
R=Path(__file__).resolve().parents[1];name='side-stand-spring-cover-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
P=dict(schema=1,package='P17',component_id='MOTO-SIDE-STAND-SPRING-COVER-001',part_code='DH161146',source='creative/research/powertrain-completion-p17-v1/side-spring-cover-plan-v53.json',length_m=.043,outer_radius_m=.0074,inner_radius_m=.0066,working_ovality=.02,all_dimensions_estimated=True,camera_calibrated=False,scope='Original isolated thin black sleeve exterior with visible finite near-mouth wall. Constant inner wall, slight ovality and UNOBSERVED far-end open review mouth are estimates, no certified real full passage/fit or durometer. No invented end disc, flange, internal retention or spring duplication. Source waviness/grain not measured or replicated as vendor pixels.',material=dict(name='Proposed black nonmetal spring sleeve',base_color_linear=[.016,.018,.020,1],metallic=0,roughness=.48),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
ps=[Vector(p)for p in[(.0074,0),(.0074,.043),(.0066,.043),(.0066,0)]];curve=[]
for i,b in enumerate(ps):
 a,c=ps[(i-1)%4],ps[(i+1)%4];q=.00012;p=b-(b-a).normalized()*q;e=b+(c-b).normalized()*q
 for j in range(12):t=j/12;curve.append((1-t)**2*p+2*t*(1-t)*b+t*t*e)
 nxt=c-(c-b).normalized()*q
 for j in range(32):curve.append(e.lerp(nxt,j/32))
N=192;V=[];F=[]
for r,z in curve:
 for j in range(N):a=math.tau*(j+.0137)/N;V.append((r*1.02*math.cos(a),r*.98*math.sin(a),z))
for k in range(len(curve)):
 for j in range(N):F.append((k*N+j,k*N+(j+1)%N,((k+1)%len(curve))*N+(j+1)%N,((k+1)%len(curve))*N+j))
ob=mesh_object('DH161146_FINITE_THIN_ANNULAR_SLEEVE_REVIEW_BOUNDARIES',V,F);recalc(ob);clean_smooth(ob);ob['scope']=P['scope'];finish_source(H,O,P)
