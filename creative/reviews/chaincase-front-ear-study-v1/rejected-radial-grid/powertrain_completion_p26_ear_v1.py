"""P26 isolated forward attachment study. Historical upper case/three known axes stay immutable."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
R=Path(__file__).resolve().parents[1];H=R/'assets-src/moto-components/chaincase-front-ear-study-v1';O=R/'creative/reviews/chaincase-front-ear-study-v1';H.mkdir(parents=True,exist_ok=True)
outline=[[-.017,.014],[.017,.014],[.015,.006],[.010,-.003],[.011,-.010],[.007,-.019],[-.007,-.019],[-.011,-.010],[-.010,-.003],[-.015,.006]]
P={'schema':1,'package':'P26','component_id':'MOTO-CHAINCASE-FRONT-EAR-STUDY-001','source':'creative/research/powertrain-completion-p26-v1/front-ear-child-plan-v1.json','outline_controls_m':outline,'hole_center_xy_m':[0,-.010],'hole_radius_m':.0035,'hole_diameter_range_m':[.005,.010],'hole_position_uncertainty_m':.006,'sheet_normal_thickness_m':.0015,'thickness_range_m':[.001,.0022],'root_offset_m':.012,'root_offset_range_m':[.006,.020],'seat_pressing_height_m':.002,'seat_radius_m':.0065,'seat_radius_range_m':[.005,.009],'all_dimensions_estimated':True,'axis_certified':False,'scope':'Isolated shaped forward ear candidate inferred from related kit views. Estimated pierced seat is not a certified fourth mount axis. Upper root/back section and relation to historical wall holes unregistered. Do not modify or replace historical upper chaincase.','material':{'name':'Proposed clean silver painted ear','base_color_linear':[.43,.45,.47,1],'metallic':0,'roughness':.32},'package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);pts=[Vector(p)for p in outline];curve=[]
for i in range(len(pts)):
 a,b,c,d=[pts[k%len(pts)]for k in [i-1,i,i+1,i+2]]
 for j in range(16):t=j/16;curve.append(.5*(2*b+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
area=sum(a.x*b.y-b.x*a.y for a,b in zip(curve,curve[1:]+curve[:1]));
if area<0:curve.reverse()
C=Vector((0,-.010));N=len(curve);M=32;V=[];F=[]
def height_normal(x,y):
 t=max(0,min(1,(y+.004)/.018));root=.012*t*t*(3-2*t);dy=.012*6*t*(1-t)/.018 if 0<t<1 else 0;r=math.hypot(x,y+.010);q=(r-.0065)/.003;seat=.002*math.exp(-q*q);dr=-2*q/.003*seat;dx=dr*x/r if r else 0;dy+=dr*(y+.010)/r if r else 0;return root+seat,Vector((-dx,-dy,1)).normalized()
for side in [1,-1]:
 for k in range(M+1):
  t=k/M
  for p in curve:
   d=p-C;inner=C+d.normalized()*.0035;q=inner.lerp(p,t);z,n=height_normal(q.x,q.y);v=Vector((q.x,q.y,z))+n*(side*.0015/2);V.append(tuple(v))
S=(M+1)*N
for k in range(M):
 a=k*N;b=a+N
 for i in range(N):
  j=(i+1)%N;F.append((a+i,b+i,b+j,a+j));F.append((S+a+i,S+a+j,S+b+j,S+b+i))
for i in range(N):
 j=(i+1)%N;a=M*N;F.append((a+i,S+a+i,S+a+j,a+j));F.append((i,j,S+j,S+i))
ob=mesh_object('SHAPED_CHAINCASE_FORWARD_EAR_CANDIDATE',V,F);ob['scope']=P['scope'];finish_source(H,O,P)
