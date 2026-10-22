"""Original PF541109 left upper saddle land only; bounded finite underside, no whole-case cap."""
import bpy,sys,json,math,bmesh
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
from powertrain_continuation_shapes_v2 import cyl,boolean
from powertrain_continuation_loft_v4 import recalc,clean_smooth
R=Path(__file__).resolve().parents[1];name='crankcase-upper-land-lh-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
planpath='creative/research/powertrain-completion-p18-v1/lh-upper-land-plan-v55.json';S=json.loads((R/planpath).read_text());T=S['thickness_m'];scale=S['scale_m_px']
P=dict(schema=1,package='P18',component_id='MOTO-CRANKCASE-UPPER-LAND-LH-001',part_code='PF541109',source=planpath,outline_control_pixels=S['outline_control_pixels'],holes=S['holes'],thickness_m=T,edge_radius_m=.00022,all_dimensions_estimated=True,camera_calibrated=False,scope='Original visible machined LEFT upper saddle land fragment, open semicircular saddle and three observed aperture studies. Constant thickness and flat lower review cut are estimated, not whole-case wall depth or certified internal passages. Separate used-specimen plug, adjacent cast outer bulges/ribs/body, markings, hidden galleries and installed cylinder/cover fit excluded. No frozen RH land/LH output panel duplicated.',material=dict(name='Proposed clean silver machined left saddle land',base_color_linear=[.38,.40,.42,1],metallic=.65,roughness=.40),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
cs=[Vector(((u-300)*scale,(400-v)*scale))for u,v in S['outline_control_pixels']]
def bs(i,t):
 p=[cs[(i+j)%len(cs)]for j in range(4)];w=[(1-t)**3/6,(3*t**3-6*t*t+4)/6,(-3*t**3+3*t*t+3*t+1)/6,t**3/6];dw=[-(1-t)**2/2,(9*t*t-12*t)/6,(-9*t*t+6*t+3)/6,t*t/2]
 return tuple(sum((v*a for v,a in zip(p,q)),Vector((0,0)))for q in [w,dw])
curves=[bs(i,j/16)for i in range(len(cs))for j in range(16)];area=sum(p.x*q.y-q.x*p.y for (p,_),(q,__)in zip(curves,curves[1:]+curves[:1]))
if area<0:curves=[(p,-t)for p,t in reversed(curves)]
edge=.00022;sections=[]
# Rounded finite perimeter edges are constructed before bore booleans; planar land is real flat face.
for j in range(13):
 a=math.pi/2*j/12;sections.append((edge-edge*math.sin(a),-edge+edge*math.cos(a)))
sections.append((0,-T+edge))
for j in range(1,13):
 a=math.pi/2*j/12;sections.append((edge-edge*math.cos(a),-T+edge-edge*math.sin(a)))
V=[];F=[];N=len(curves)
for inset,z in sections:
 for c,t in curves:
  t=t.normalized();n=Vector((-t.y,t.x));q=c+n*inset;V.append((q.x,q.y,z))
for k in range(len(sections)-1):
 for j in range(N):F.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
F.extend([tuple(reversed(range(N))),tuple((len(sections)-1)*N+j for j in range(N))]);ob=mesh_object('LH_UPPER_SADDLE_LAND_FINITE_OPEN_FRAGMENT',V,F);recalc(ob)
for i,row in enumerate(S['holes']):
 u,v=row['center_pixels'];x,y=(u-300)*scale,(400-v)*scale;r=row['working_radius_m'];boolean(ob,cyl((x,y,-.02),(x,y,.02),r),'DIFFERENCE','Observed LH land aperture '+str(i))
 if i in [1,2]:
  boolean(ob,cyl((x,y,-.001),(x,y,.02),.0053),'DIFFERENCE','Visible stepped seat estimated depth '+str(i))
clean_smooth(ob)
# Truly planar machined faces retain flat normals; perimeter is smoothly sampled, no buffer-normal repair.
for f in ob.data.polygons:
 if abs(f.normal.z)>.999999:f.use_smooth=False
ob['scope']=P['scope'];finish_source(H,O,P)
