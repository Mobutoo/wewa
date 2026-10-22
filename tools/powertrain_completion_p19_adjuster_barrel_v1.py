"""Original separate cable-entry barrel: two fine grip bands and actual annular lumen."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
R=Path(__file__).resolve().parents[1];name='carburettor-cable-adjuster-barrel-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name
H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
profile=[(.0064,0),(.0068,.0005),(.0068,.0024),(.0064,.003),(.0067,.0035),(.007,.004),(.007,.0118),(.0068,.0123),(.0062,.0127),(.0062,.0137),(.0068,.0142),(.007,.0147),(.007,.0265),(.0068,.0274),(.0064,.028),(.0028,.028),(.0028,0)]
P=dict(schema=1,package='P19',component_id='MOTO-CARBURETTOR-CABLE-ADJUSTER-BARREL-001',source='creative/research/powertrain-completion-p19-v1/cable-adjuster-barrel-plan-v8.json',profile_r_z_m=profile,angular_samples=256,working_grip_count=32,grip_count_range=[24,40],grip_depth_m=.00015,section_corner_rounding_m=.00012,all_dimensions_estimated=True,scope='Separate visible entry-adjuster exterior envelope with two fine axial grip bands, circumferential relief and real open annular lumen. The seam may separate actual subparts; count, grip section, internal threads/slot/retention and all dimensions unqualified. Plain bore only, no unseen full-depth cable slot or certified mating engagement. Underlying hex locknut, elbow and boot excluded; frozen sources untouched.',material=dict(name='Proposed bright plain cable adjuster metal',base_color_linear=[.38,.40,.42,1],metallic=.85,roughness=.28),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);pts=[Vector(p)for p in profile];corners=[];curve=[]
for i,b in enumerate(pts):
 a,c=pts[(i-1)%len(pts)],pts[(i+1)%len(pts)];q=min(.00012,(b-a).length*.25,(c-b).length*.25);corners.append((b-(b-a).normalized()*q,b,b+(c-b).normalized()*q))
for i,(a,b,c)in enumerate(corners):
 for j in range(4):
  t=j/4;curve.append((1-t)**2*a+2*(1-t)*t*b+t*t*c)
 for j in range(4):curve.append(c.lerp(corners[(i+1)%len(corners)][0],j/4))
def orient(a,b,c):return (b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x)
for i in range(len(curve)):
 for j in range(i+2,len(curve)):
  if i==0 and j==len(curve)-1:continue
  a,b=curve[i],curve[(i+1)%len(curve)];c,d=curve[j],curve[(j+1)%len(curve)];assert not(orient(a,b,c)*orient(a,b,d)<-1e-22 and orient(c,d,a)*orient(c,d,b)<-1e-22)
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
V=[];F=[];N=P['angular_samples']
for r,z in curve:
 band=smooth((z-.004)/.0007)*(1-smooth((z-.011)/.0008))+smooth((z-.0147)/.0007)*(1-smooth((z-.0258)/.0008))
 for j in range(N):
  a=math.tau*j/N;rr=r-(.00015*(.5-.5*math.cos(32*a))**2*band if r>.0066 else 0);V.append((rr*math.cos(a),rr*math.sin(a),z))
for k in range(len(curve)):
 for j in range(N):q=(j+1)%N;F.append((k*N+j,k*N+q,((k+1)%len(curve))*N+q,((k+1)%len(curve))*N+j))
ob=mesh_object('CABLE_ENTRY_ADJUSTER_ANNULUS_TWO_GRIP_BANDS_AND_RELIEF',V,F);ob['scope']=P['scope'];finish_source(H,O,P)
