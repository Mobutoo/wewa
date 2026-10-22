"""New physical-view curved round-to-flattened side-stand foot, original section loft."""
import bpy,bmesh,math,sys,json
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
R=Path(__file__).resolve().parents[1];name='side-stand-foot-edge-v2';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name
H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
C=[(.225,0,.0105,.0105,2),(.233,.0005,.009,.011,2.1),(.240,.002,.0068,.012,2.4),(.248,.006,.0048,.013,2.8),(.258,.016,.003,.014,3.5),(.272,.035,.0024,.0145,4),(.289,.059,.0022,.0145,4),(.296,.069,.0022,.013,4),(.301,.076,.0018,.008,3),(.302,.0775,.0014,.003,2),(.3023,.078,.0008,.0008,2)]
def center(i,t):
 a=Vector(C[max(0,i-1)][:2]);b=Vector(C[i][:2]);c=Vector(C[i+1][:2]);d=Vector(C[min(len(C)-1,i+2)][:2]);return .5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)
sections=[]
for i in range(len(C)-1):
 for j in range(32):
  t=j/32;s=t*t*(3-2*t);c=center(i,t);dt=.0001;ta=max(0,t-dt);tb=min(1,t+dt);tangent=(center(i,tb)-center(i,ta)).normalized();nr=C[i][2]*(1-s)+C[i+1][2]*s;zr=C[i][3]*(1-s)+C[i+1][3]*s;e=C[i][4]*(1-s)+C[i+1][4]*s;sections.append((c,tangent,nr,zr,e))
c=Vector(C[-1][:2]);sections.append((c,(c-Vector(C[-2][:2])).normalized(),*C[-1][2:]))
P=dict(schema=1,package='P17',component_id='MOTO-SIDE-STAND-CURVED-FOOT-001',source='creative/research/powertrain-completion-p17-v1/side-foot-curved-plan-v12.json',control_sections_xy_normalradius_zradius_exponent_m=C,angular_samples=128,all_dimensions_estimated=True,scope='Separate original curved root transition into flattened broad rounded toe, now supported by second physical JA113202 view. Cross-sections morph from circular root to soft flattened plate envelope. Exact underside/camber, thickness/depth, out-of-plane axes and working registration remain estimated. Root overlaps retained straight-stem envelope: no fitted assembly claim or frozen stem modification; future registration/trim study required. No ground/operating or weld qualification. Rejected straight-edge v1 remains preserved, never delivered.',material=dict(name='Proposed black formed side foot coating',base_color_linear=[.012,.014,.017,1],metallic=.15,roughness=.34),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);V=[];F=[];N=P['angular_samples']
for c,t,nr,zr,e in sections:
 n=Vector((-t.y,t.x))
 for j in range(N):
  a=math.tau*j/N;u=math.copysign(abs(math.cos(a))**(2/e),math.cos(a));v=math.copysign(abs(math.sin(a))**(2/e),math.sin(a));q=c+n*nr*u;V.append((q.x,q.y,zr*v))
for k in range(len(sections)-1):
 for i in range(N):j=(i+1)%N;F.append((k*N+i,k*N+j,(k+1)*N+j,(k+1)*N+i))
F+=[tuple(reversed(range(N))),tuple((len(sections)-1)*N+j for j in range(N))]
ob=mesh_object('CURVED_ROUND_TO_FLATTENED_SIDE_FOOT_WITH_ROUNDED_TOE',V,F);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob['scope']=P['scope'];finish_source(H,O,P)
