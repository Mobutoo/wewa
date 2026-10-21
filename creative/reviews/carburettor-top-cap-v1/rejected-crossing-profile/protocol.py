"""P19 separate ribbed top cap: continuous annular section, real entry/open seat, no thread invention."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
R=Path(__file__).resolve().parents[1];H=R/'assets-src/moto-components/carburettor-top-cap-v1';O=R/'creative/reviews/carburettor-top-cap-v1';H.mkdir(parents=True,exist_ok=True)
profile=[[.0175,0],[.0200,0],[.0210,.0006],[.0215,.0013],[.0210,.0023],[.0205,.0028],[.0205,.0085],[.0200,.0105],[.0185,.0117],[.0100,.0125],[.0075,.0125],[.0070,.0120],[.0070,.0102],[.0100,.0098],[.0170,.0090],[.0175,.0080]]
P={'schema':1,'package':'P19','component_id':'MOTO-CARBURETTOR-TOP-CAP-001','source':'creative/research/powertrain-completion-p19-v1/cap-child-plan-v1.json','profile_r_z_m':profile,'rib_count':12,'rib_count_range':[10,16],'rib_count_status':'Photo-inferred uncertain count, not OEM fact','rib_height_m':.0012,'rib_height_range_m':[.0007,.0018],'body_OD_range_m':[.034,.048],'height_range_m':[.009,.017],'entry_diameter_range_m':[.012,.019],'section_samples_per_span':8,'angular_samples':240,'all_dimensions_estimated':True,'scope':'Separate cap only, continuous rolled lip/crown, large outer grip ribs and open entry/basic annular seat. Hidden threads and exact seat not fabricated or certified.','material':{'name':'Proposed clean silver ribbed cap','base_color_linear':[.34,.36,.38,1],'metallic':.75,'roughness':.35},'package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);pts=[Vector(p)for p in profile];curve=[]
for i in range(len(pts)):
 a,b,c,d=[pts[j%len(pts)]for j in [i-1,i,i+1,i+2]]
 for j in range(8):t=j/8;curve.append(.5*(2*b+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
def orient(a,b,c):return (b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x)
for i in range(len(curve)):
 for j in range(i+2,len(curve)):
  if i==0 and j==len(curve)-1:continue
  a,b=curve[i],curve[(i+1)%len(curve)];c,d=curve[j],curve[(j+1)%len(curve)];assert not(orient(a,b,c)*orient(a,b,d)<-1e-22 and orient(c,d,a)*orient(c,d,b)<-1e-22),'Self-crossing section'
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
V=[];F=[];N=P['angular_samples']
for r,z in curve:
 assert r>0
 for i in range(N):
  angle=i*math.tau/N;phase=(angle%(math.tau/12))/(math.tau/12);dist=min(phase,1-phase);grip=(.5+.5*math.cos(math.pi*dist/.32))**2 if dist<.32 else 0;window=smooth((z-.0018)/.0012)*(1-smooth((z-.0092)/.0014)) if r>.019 else 0;rr=r+.0012*grip*window;V.append((rr*math.cos(angle),rr*math.sin(angle),z))
for k in range(len(curve)):
 a=k*N;b=((k+1)%len(curve))*N
 for i in range(N):j=(i+1)%N;F.append((a+i,a+j,b+j,b+i))
ob=mesh_object('CARB_TOP_CAP_CONTINUOUS_ANNULUS_WITH_LARGE_GRIPS',V,F);ob['scope']=P['scope'];finish_source(H,O,P)
