"""Original39042215 metallic six-flat nut/rolled collar, finite inner helix and separate nylon annulus."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
from powertrain_continuation_loft_v4 import clean_smooth,recalc
R=Path(__file__).resolve().parents[1];name='side-stand-pivot-nyloc-nut-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
metal=dict(name='Proposed lightly plated metallic nut body',base_color_linear=[.42,.43,.40,1],metallic=.82,roughness=.30);nylon=dict(name='Proposed orange red nonmetal locking insert',base_color_linear=[.28,.035,.012,1],metallic=0,roughness=.43)
P=dict(schema=1,package='P17',component_id='MOTO-SIDE-STAND-PIVOT-NYLOC-NUT-001',part_code='39042215',source='creative/research/powertrain-completion-p17-v1/pivot-nyloc-nut-plan-v57.json',across_flats_m=.017,total_height_m=.010,working_pitch_m=.00125,pitch_range_m=[.00125,.0015],thread_root_radius_m=.0051,thread_crest_radius_m=.0045,insert_body_radial_review_clearance_m=.0001,all_dimensions_estimated=True,camera_calibrated=False,scope='Original separate39042215 six-flat nut body, entry chamfer, rolled circular collar, real interpreted internal metal helix and orange/red finite insert annulus from opposed physical poses. Metric pitch/hand/flanks/nylon bore/retention section and working body-insert clearance estimated. No actual bolt mating, preload/torque/prevailing-force/strength/currentRDC fit; retained12mm shoulder versus9mm eye contradiction unresolved. No duplicated washer/bolt.',material=metal,material_regions={'NYLOC_METALLIC_SIX_FLATS_ROLLED_COLLAR_INNER_HELIX':metal,'NYLOC_ORANGE_INSERT_REVIEW_SECTION':nylon},package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
N=192

def smooth(t):t=max(0,min(1,t));return t*t*t*(10+t*(-15+6*t))
def hexrad(a,A=.0085,q=.0004):
 delta=(a+math.pi/6)%(math.pi/3)-math.pi/6;r=A/math.cos(delta)
 if abs(r*math.sin(delta))<=(A-q)*math.tan(math.pi/6):return r
 vc=(A-q)/math.cos(math.pi/6);theta=(math.pi/6 if delta>=0 else -math.pi/6);dot=vc*math.cos(delta-theta);disc=max(0,q*q-vc*vc+dot*dot);return dot+math.sqrt(disc)
# Outer bottom chamfer, six flats, chamfer into raised circular collar, rounded rolled lip.
sections=[]
for j in range(9):t=j/8;sections.append(dict(z=.0005*t,hexscale=.94+.06*t,circle=None))
sections.append(dict(z=.0057,hexscale=1,circle=None))
for j in range(1,17):
 t=j/16;sections.append(dict(z=.0057+.001*t,blend=smooth(t)))
for j in range(1,17):
 t=j/16;sections.append(dict(z=.0067+.0027*t,r=.0076))
# Quadratic rolled upper edge into internal collar seat, explicit section not giant closing cap.
control=[(.0076,.0094),(.00755,.0098),(.00725,.010),(.0069,.010),(.00665,.0098),(.00665,.0067),(.0051,.0062)]
for a,b in zip(control,control[1:]):
 for j in range(1,9):t=j/8;sections.append(dict(z=a[1]*(1-t)+b[1]*t,r=a[0]*(1-t)+b[0]*t))
for j in range(1,177):sections.append(dict(z=.0062-(.0057*j/176),inner=True))
sections +=[dict(z=.0002,r=.00535),dict(z=0,r=.00555)]
V=[];F=[]
for s in sections:
 z=s['z']
 for j in range(N):
  a=math.tau*(j+.0137)/N
  if 'hexscale'in s:r=hexrad(a)*s['hexscale']
  elif 'blend'in s:r=hexrad(a)*(1-s['blend'])+.0076*s['blend']
  elif s.get('inner'):
   window=smooth((z-.0005)/.0006)*smooth((.0062-z)/.0006);r=.0051-.0006*(.5+.5*math.cos(math.tau*(z-.0005)/.00125-a))*window
  else:r=s['r']
  V.append((r*math.cos(a),r*math.sin(a),z))
for k in range(len(sections)):
 for j in range(N):F.append((k*N+j,k*N+(j+1)%N,((k+1)%len(sections))*N+(j+1)%N,((k+1)%len(sections))*N+j))
ob=mesh_object('NYLOC_METALLIC_SIX_FLATS_ROLLED_COLLAR_INNER_HELIX',V,F);recalc(ob);clean_smooth(ob)
# Insert has finite estimated smooth annular wall; no hidden nylon thread invented.
ps=[Vector(v)for v in[(.00655,.00665),(.00655,.0094),(.00455,.0094),(.00455,.00665)]];curve=[]
for i,b in enumerate(ps):
 a,c=ps[(i-1)%4],ps[(i+1)%4];q=.00012;p=b-(b-a).normalized()*q;e=b+(c-b).normalized()*q
 for j in range(8):t=j/8;curve.append((1-t)**2*p+2*t*(1-t)*b+t*t*e)
 nxt=c-(c-b).normalized()*q
 for j in range(8):curve.append(e.lerp(nxt,j/8))
V=[];F=[]
for r,z in curve:
 for j in range(N):a=math.tau*(j+.0137)/N;V.append((r*math.cos(a),r*math.sin(a),z))
for k in range(len(curve)):
 for j in range(N):F.append((k*N+j,k*N+(j+1)%N,((k+1)%len(curve))*N+(j+1)%N,((k+1)%len(curve))*N+j))
ob=mesh_object('NYLOC_ORANGE_INSERT_REVIEW_SECTION',V,F);recalc(ob);clean_smooth(ob);finish_source(H,O,P)
