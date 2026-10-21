"""DF161102 separately referenced hex-head shoulder bolt and visible helical terminal."""
import bpy,bmesh,sys,json,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
R=Path(__file__).resolve().parents[1];name='side-stand-pivot-bolt-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name
H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
N=192;pitch=.00125;start=.0195;end=.0325
P=dict(schema=1,package='P17',component_id='MOTO-SIDE-STAND-PIVOT-BOLT-001',source='creative/research/powertrain-completion-p17-v1/side-pivot-physical-plan-v11.json',head_AF_m=.017,head_height_m=.0055,shoulder_diameter_m=.012,shoulder_length_m=.014,thread_major_diameter_m=.010,thread_root_diameter_m=.0087,working_pitch_m=pitch,thread_length_m=.013,thread_form='Smooth finite helical crest approximation with two end runouts, not certified metric flank/pitch fit',angular_samples=N,all_dimensions_estimated=True,scope='DF161102 separately referenced bolt exterior: softened hex head, plain larger shoulder, narrower visibly helical terminal and tip chamfer. NominalM10 envelope inferred only from related D04 nut pairing. Pitch/head/shoulder dimensions estimated. Retained9mm eye conflicts: NO inserted/installed fit, adapter, bolt-grade/mark or mating thread claim. Frozen fork untouched.',material=dict(name='Proposed clean plain pivot bolt metal',base_color_linear=[.20,.22,.24,1],metallic=.8,roughness=.36),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
def hexrad(a,apothem):return apothem/math.cos((a+math.pi/6)%(math.pi/3)-math.pi/6)
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
rings=[]
for z,kind,r in [(0,'hex',.0078),(.0007,'hex',.0085),(.0048,'hex',.0085),(.0055,'hex',.0079),(.0056,'circle',.0063),(.0059,'circle',.0061),(.0062,'circle',.006),(.0191,'circle',.006),(.0195,'circle',.00435)]:rings.append((z,[hexrad(math.tau*j/N,r)if kind=='hex'else r for j in range(N)]))
steps=math.ceil((end-start)/pitch*32)
for i in range(1,steps+1):
 z=start+(end-start)*i/steps;window=smooth((z-start)/.001)*smooth((end-z)/.0008);root=.00435-.0003*smooth((z-(end-.0006))/.0006)
 rings.append((z,[root+.00065*(.5+.5*math.cos(math.tau*((z-start)/pitch)-math.tau*j/N))*window for j in range(N)]))
V=[];F=[]
for z,rs in rings:
 for j,r in enumerate(rs):a=math.tau*j/N;V.append((r*math.cos(a),r*math.sin(a),z))
for k in range(len(rings)-1):
 for j in range(N):q=(j+1)%N;F.append((k*N+j,k*N+q,(k+1)*N+q,(k+1)*N+j))
base_center=len(V);V.append((0,0,rings[0][0]));tip_center=len(V);V.append((0,0,rings[-1][0]))
for j in range(N):
 q=(j+1)%N;F.append((base_center,q,j));F.append((tip_center,(len(rings)-1)*N+j,(len(rings)-1)*N+q))
ob=mesh_object('SIDE_STAND_DISTINCT_HEX_SHOULDER_BOLT_WITH_HELICAL_TERMINAL',V,F);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob['scope']=P['scope'];finish_source(H,O,P)
