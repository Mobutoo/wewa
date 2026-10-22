"""Original annular cable-entry boot; no retained cap/elbow geometry modified."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
R=Path(__file__).resolve().parents[1];name='carburettor-entry-boot-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name
H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
profile=[(.010,0),(.0115,.0006),(.012,.0015),(.012,.003),(.011,.004),(.010,.005),(.009,.0075),(.0075,.009),(.007,.011),(.007,.013),(.0065,.014),(.00325,.014),(.00325,.010),(.004,.008),(.0055,.006),(.007,.004),(.007,0)]
P=dict(schema=1,package='P19',component_id='MOTO-CARBURETTOR-ENTRY-BOOT-001',source='creative/research/powertrain-completion-p19-v1/entry-boot-plan-v6.json',profile_r_z_m=profile,section_corner_rounding_m=.0002,angular_samples=144,all_dimensions_estimated=True,scope='Separate short stepped boot, rounded shoulder and finite annular wall with actual open passage. Hidden seat/retention, exact tube/cap fit and material chemistry unqualified.',material=dict(name='Proposed plain black flexible boot',base_color_linear=[.012,.013,.014,1],metallic=0,roughness=.55),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
pts=[Vector(p)for p in profile];corners=[];curve=[]
for i,b in enumerate(pts):
 a,c=pts[(i-1)%len(pts)],pts[(i+1)%len(pts)];q=min(.0002,(b-a).length*.25,(c-b).length*.25);corners.append((b-(b-a).normalized()*q,b,b+(c-b).normalized()*q))
for i,(a,b,c)in enumerate(corners):
 for j in range(6):
  t=j/6;curve.append((1-t)**2*a+2*(1-t)*t*b+t*t*c)
 for j in range(4):curve.append(c.lerp(corners[(i+1)%len(corners)][0],j/4))
def orient(a,b,c):return (b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x)
for i in range(len(curve)):
 for j in range(i+2,len(curve)):
  if i==0 and j==len(curve)-1:continue
  a,b=curve[i],curve[(i+1)%len(curve)];c,d=curve[j],curve[(j+1)%len(curve)];assert not(orient(a,b,c)*orient(a,b,d)<-1e-22 and orient(c,d,a)*orient(c,d,b)<-1e-22)
V=[];F=[];N=P['angular_samples']
for r,z in curve:
 for i in range(N):
  a=math.tau*i/N;V.append((r*math.cos(a),r*math.sin(a),z))
for k in range(len(curve)):
 a=k*N;b=((k+1)%len(curve))*N
 for i in range(N):j=(i+1)%N;F.append((a+i,a+j,b+j,b+i))
ob=mesh_object('ENTRY_BOOT_ROUNDED_STEPPED_ANNULAR_WALL',V,F);ob['scope']=P['scope'];finish_source(H,O,P)
