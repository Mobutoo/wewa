"""P16 one rider rubber sleeve: shaped mouth, closed tip and continuous exterior ribs; no support duplicate."""
import bpy,sys,json,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
R=Path(__file__).resolve().parents[1];H=R/'assets-src/moto-components/footrest-rubber-v1';O=R/'creative/reviews/footrest-rubber-v1';H.mkdir(parents=True,exist_ok=True)
P={'schema':1,'package':'P16','component_id':'MOTO-FOOTREST-RIDER-RUBBER-001','source':'creative/research/powertrain-completion-p16-v1/plan.json','length_m':.106,'length_range_m':[.085,.115],'outer_base_width_height_m':[.034,.027],'outer_range_m':[[.030,.042],[.025,.036]],'mouth_width_height_m':[.023,.016],'mouth_range_m':[[.019,.027],[.012,.020]],'blind_depth_m':.095,'blind_depth_range_m':[.075,.100],'rib_centres_m':[.015+i*.009 for i in range(9)],'rib_count_status':'Photo-inferred9, uncertainty8–11; do not treat as measured exact count','rib_half_width_m':.0031,'rib_height_m':.0018,'rib_height_range_m':[.001,.003],'section_exponent':4.0,'tip_status':'Rounded closed outer end; basic blind cavity depth estimated, no hidden retention lands invented','radial_samples':192,'length_samples':420,'all_dimensions_estimated':True,'scope':'Single original rider rubber sleeve only; no replication, no claim of fit on existing PF113000/001 supports','material':{'name':'Proposed clean black footrest rubber','base_color_linear':[.010,.011,.013,1],'metallic':0,'roughness':.64},'package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);V=[];F=[];N=P['radial_samples'];M=P['length_samples'];L=P['length_m']
def sstep(t):t=max(0,min(1,t));return t*t*(3-2*t)
def circle(a,w,h,e=4):c=math.cos(a);s=math.sin(a);return w*math.copysign(abs(c)**(2/e),c),h*math.copysign(abs(s)**(2/e),s)
for k in range(M+1):
 x=L*k/M;end=1-.92*sstep((x-.098)/.008);cuff=.0012*(1-sstep(x/.007));rib=sum(P['rib_height_m']*(.5+.5*math.cos(math.pi*(x-c)/P['rib_half_width_m']))**2 for c in P['rib_centres_m']if abs(x-c)<P['rib_half_width_m'])
 for j in range(N):
  a=j*math.tau/N;y,z=circle(a,.017,.0135);weight=sstep((z+.008)/.020);r=(rib*weight+cuff)*end;widen=.98-.06*z/.0135;V.append((x,(y*widen+math.copysign(r*abs(math.cos(a)),y))*end,z*end+r*math.sin(a)*weight))
for k in range(M):
 a=k*N;b=a+N
 for i in range(N):j=(i+1)%N;F.append((a+i,a+j,b+j,b+i))
F.append(tuple(M*N+i for i in range(N)))
# Visible shaped mouth plus plain bounded blind seat; hidden retention details intentionally absent.
inner_start=len(V);innerM=64
for k in range(innerM+1):
 x=P['blind_depth_m']*k/innerM
 for j in range(N):y,z=circle(j*math.tau/N,.0115,.008,3.8);V.append((x,y,z))
for k in range(innerM):
 a=inner_start+k*N;b=a+N
 for i in range(N):j=(i+1)%N;F.append((a+i,b+i,b+j,a+j))
F.append(tuple(reversed([inner_start+innerM*N+i for i in range(N)])))
for i in range(N):j=(i+1)%N;F.append((i,inner_start+i,inner_start+j,j))
ob=mesh_object('RIDER_RUBBER_NONCIRCULAR_RIBBED_SLEEVE',V,F);ob['scope']=P['scope'];finish_source(H,O,P)
