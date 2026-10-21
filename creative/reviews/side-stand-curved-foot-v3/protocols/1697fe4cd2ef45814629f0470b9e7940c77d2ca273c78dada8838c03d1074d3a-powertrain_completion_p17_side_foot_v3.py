"""New physical-view curved round-to-flattened side-stand foot, original section loft."""
import bpy,bmesh,math,sys,json
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
R=Path(__file__).resolve().parents[1];name='side-stand-curved-foot-v3';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name
H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
C=[(.225,0,.0105,.0105,2),(.233,.0005,.009,.011,2.1),(.240,.002,.0068,.012,2.4),(.248,.006,.0048,.013,2.8),(.258,.016,.003,.014,3.5),(.272,.035,.0024,.0145,4),(.289,.059,.0022,.0145,4)]
def center(i,t):
 a=Vector(C[max(0,i-1)][:2]);b=Vector(C[i][:2]);c=Vector(C[i+1][:2]);d=Vector(C[min(len(C)-1,i+2)][:2]);return .5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)
def scalar(i,t,k):
 a=C[max(0,i-1)][k];b=C[i][k];c=C[i+1][k];d=C[min(len(C)-1,i+2)][k]
 def harmonic(x,y):return 2*x*y/(x+y) if x*y>0 else 0
 m0=c-b if i==0 else harmonic(b-a,c-b);m1=c-b if i==len(C)-2 else harmonic(c-b,d-c)
 return (2*t**3-3*t*t+1)*b+(t**3-2*t*t+t)*m0+(-2*t**3+3*t*t)*c+(t**3-t*t)*m1
sections=[]
for i in range(len(C)-1):
 for j in range(32):
  t=j/32;s=t*t*(3-2*t);c=center(i,t);dt=.0001;ta=max(0,t-dt);tb=min(1,t+dt);tangent=(center(i,tb)-center(i,ta)).normalized();nr=scalar(i,t,2);zr=scalar(i,t,3);e=scalar(i,t,4);sections.append((c,tangent,nr,zr,e))
c=Vector(C[-1][:2]);toe_t=(c-Vector(C[-2][:2])).normalized();sections.append((c,toe_t,*C[-1][2:]))
for j in range(1,64):
 a=math.pi/2*j/64;sections.append((c+toe_t*.0145*math.sin(a),toe_t,.0022*math.cos(a),.0145*math.cos(a),4))
pole=c+toe_t*.0145
P=dict(schema=1,package='P17',component_id='MOTO-SIDE-STAND-CURVED-FOOT-001',source='creative/research/powertrain-completion-p17-v1/side-foot-curved-plan-v13.json',control_sections_xy_normalradius_zradius_exponent_m=C,angular_samples=128,all_dimensions_estimated=True,scope='Separate original curved root transition into flattened broad rounded toe, now supported by second physical JA113202 view. Cross-sections morph from circular root to soft flattened plate envelope. Exact underside/camber, thickness/depth, out-of-plane axes and working registration remain estimated. Root overlaps retained straight-stem envelope: no fitted assembly claim or frozen stem modification; future registration/trim study required. No ground/operating or weld qualification. Rejected straight-edge v1 and wavy/toe-close v2 remain preserved, never delivered.',material=dict(name='Proposed black formed side foot coating',base_color_linear=[.012,.014,.017,1],metallic=.15,roughness=.34),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);V=[];F=[];N=P['angular_samples']
for c,t,nr,zr,e in sections:
 n=Vector((-t.y,t.x))
 for j in range(N):
  a=math.tau*j/N;u=math.copysign(abs(math.cos(a))**(2/e),math.cos(a));v=math.copysign(abs(math.sin(a))**(2/e),math.sin(a));q=c+n*nr*u;V.append((q.x,q.y,zr*v))
for k in range(len(sections)-1):
 for i in range(N):j=(i+1)%N;F.append((k*N+i,k*N+j,(k+1)*N+j,(k+1)*N+i))
F.append(tuple(reversed(range(N))));pole_index=len(V);V.append((pole.x,pole.y,0))
for j in range(N):F.append(((len(sections)-1)*N+j,(len(sections)-1)*N+(j+1)%N,pole_index))
ob=mesh_object('CURVED_ROUND_TO_FLATTENED_SIDE_FOOT_WITH_ROUNDED_TOE',V,F);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob['scope']=P['scope'];finish_source(H,O,P)
