"""Original JA113201 tubular stand shaft, fine visible striated band and true side drill."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
from powertrain_continuation_shapes_v2 import cyl,boolean
from powertrain_continuation_loft_v4 import clean_smooth,recalc
R=Path(__file__).resolve().parents[1];name='centre-stand-pivot-shaft-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
profile=[(.0095,0),(.010,.0005),(.010,.0018),(.0094,.0023),(.00725,.0023),(.007,.0027),(.007,.030),(.007,.034),(.00715,.035),(.00715,.069),(.007,.070),(.007,.101),(.00675,.1015),(.00675,.103),(.007,.1035),(.007,.1115),(.0066,.112),(.00495,.112),(.00475,.1118),(.00475,.0002),(.00495,0)]
P=dict(schema=1,package='P17',component_id='MOTO-CENTRE-STAND-PIVOT-SHAFT-001',part_code='JA113201',source='creative/research/powertrain-completion-p17-v1/centre-pivot-shaft-plan-v16.json',profile_r_z_m=profile,band_z_m=[.035,.069],working_striation_count=48,striation_count_range=[32,80],radial_striation_depth_m=.00010,cross_drill_diameter_m=.0035,cross_drill_z_m=.106,all_dimensions_estimated=True,camera_calibrated=False,scope='Separate original JA113201 hollow shaft with shallow flange, visible stepped lands, fine central circumferential grip/retention study and real side drill at observed open tip. Band not certified helical thread/function. Working inner wall and UNOBSERVED flange-end mouth are explicit open review assumptions, no inferred hidden cap or certified full passage topology. No fit/insertion into retained estimated14mm frame bore or actual cotter/grade/preload claimed.',material=dict(name='Proposed plain lightly plated tubular stand shaft',base_color_linear=[.40,.40,.37,1],metallic=.8,roughness=.30),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);pts=[Vector(p)for p in profile];corners=[]
for i,b in enumerate(pts):
 a,c=pts[(i-1)%len(pts)],pts[(i+1)%len(pts)];q=min(.00012,(b-a).length*.22,(c-b).length*.22);corners.append((b-(b-a).normalized()*q,b,b+(c-b).normalized()*q))
curve=[];pitch=.034/48
for i,(a,b,c)in enumerate(corners):
 for j in range(6):t=j/6;curve.append((1-t)**2*a+2*(1-t)*t*b+t*t*c)
 d=corners[(i+1)%len(corners)][0];dense=c.x>.006 and d.x>.006 and max(c.y,d.y)>.035 and min(c.y,d.y)<.069;count=max(6,math.ceil(abs(d.y-c.y)/(pitch/16)))if dense else 6
 for j in range(count):curve.append(c.lerp(d,j/count))
def smooth(t):t=max(0,min(1,t));return t*t*t*(10+t*(-15+6*t))
V=[];F=[];N=128
for r,z in curve:
 window=smooth((z-.035)/.0015)*smooth((.069-z)/.0015);rr=r+(.00010*(.5+.5*math.cos(math.tau*(z-.035)/pitch))*window if r>.006 else 0)
 for j in range(N):a=math.tau*(j+.0137)/N;V.append((rr*math.cos(a),rr*math.sin(a),z))
for k in range(len(curve)):
 for j in range(N):F.append((k*N+j,k*N+(j+1)%N,((k+1)%len(curve))*N+(j+1)%N,((k+1)%len(curve))*N+j))
ob=mesh_object('JA113201_TUBULAR_SHAFT_FLANGE_FINE_BAND_AND_SIDE_DRILL',V,F);recalc(ob);boolean(ob,cyl((-.020,0,.106),(.020,0,.106),.00175),'DIFFERENCE','Observed cross-drill near open tip');clean_smooth(ob);ob['scope']=P['scope'];finish_source(H,O,P)
