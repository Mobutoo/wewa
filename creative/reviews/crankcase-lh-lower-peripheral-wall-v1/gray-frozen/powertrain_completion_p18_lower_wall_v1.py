"""Original finite lower case perimeter from newly recovered used-part poses, not a whole case."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
from powertrain_continuation_loft_v4 import clean_smooth
R=Path(__file__).resolve().parents[1];name='crankcase-lh-lower-peripheral-wall-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name
H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
planpath='creative/research/powertrain-completion-p18-v1/lh-lower-peripheral-wall-plan-v77.json';plan=json.loads((R/planpath).read_text())
P=dict(schema=1,package='P18',component_id=plan['component_id'],source=planpath,outline_control_pixels=plan['outline_control_pixels_65221'],working_scale_m_px=plan['working_scale_m_px'],working_depth_m=.055,normal_wall_thickness_m=.004,all_dimensions_estimated=True,camera_calibrated=False,scope=plan['scope'],variant='Used seller BM150; casting JE541038, currentRDC/finishedSKU equivalence unqualified',material=dict(name='Proposed clean cast aluminium lower peripheral wall',base_color_linear=[.33,.35,.37,1],metallic=.7,roughness=.44),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
# Clamped cubic de Boor curve preserves observed noncircular bottom and front rise.
C=[Vector(((x-350)*.00044,(805-y)*.00044)) for x,y in P['outline_control_pixels']];degree=3;n=len(C);knots=[0.0]*4+[i/(n-3) for i in range(1,n-3)]+[1.0]*4
assert len(knots)==n+4

def point(t):
 k=n-1 if t>=1 else next(i for i in range(3,n) if knots[i]<=t<knots[i+1]);d=[C[k-3+j].copy() for j in range(4)]
 for r in range(1,4):
  for j in range(3,r-1,-1):
   i=k-3+j;den=knots[i+4-r]-knots[i];a=(t-knots[i])/den if den else 0;d[j]=(1-a)*d[j-1]+a*d[j]
 return d[3]
N=384;M=72;V=[];F=[]
for side in [0,1]:
 for i in range(N+1):
  t=i/N;q=point(t);tangent=(point(min(1,t+1e-5))-point(max(0,t-1e-5))).normalized();inward=Vector((-tangent.y,tangent.x))
  for j in range(M+1):
   u=j/M
   # Two broad physical wall skins remain separate; mild cast crown only on exterior.
   # Crown vanishes smoothly at the two axial review edges, never closing the case cavity.
   crown=.0012*math.sin(math.pi*u)**2
   offset=(.004 if side else -crown);p=q+inward*offset
   V.append((p.x,p.y,-.055*u))
S=(N+1)*(M+1)
def idx(i,j):return i*(M+1)+j
for i in range(N):
 for j in range(M):
  a=idx(i,j);b=idx(i+1,j);F.extend([(a,b,b+1,a+1),(S+a,S+a+1,S+b+1,S+b)])
# Thickness-only edge faces, not an end-cap across the internal engine void.
for i in range(N):
 a=idx(i,0);b=idx(i+1,0);F.append((a,S+a,S+b,b));a=idx(i,M);b=idx(i+1,M);F.append((a,b,S+b,S+a))
for j in range(M):
 a=idx(0,j);F.append((a,a+1,S+a+1,S+a));a=idx(N,j);F.append((a,S+a,S+a+1,a+1))
ob=mesh_object('LH_LOWER_PERIPHERAL_CAST_WALL_OPEN_CASE_VOID',V,F);clean_smooth(ob);ob['scope']=P['scope'];finish_source(H,O,P)
(O/'wall-construction-check.json').write_text(json.dumps(dict(method='Clamped cubic de Boor source contour; finite normal paired wall skins across axial depth; smooth sin-squared exterior crown',contour_samples=N+1,axial_samples=M+1,thickness_m=.004,maximum_crown_m=.0012,source_contour_pixels=P['outline_control_pixels'],arbitrary_cavity_closure=False,explicit_review_cuts=['Both longitudinal contour terminals','Centre split-plane and outer cover-side depth boundaries'],scope='Geometric study of visible peripheral wall only; uncalibrated and variant-qualified'),indent=2)+'\n')
