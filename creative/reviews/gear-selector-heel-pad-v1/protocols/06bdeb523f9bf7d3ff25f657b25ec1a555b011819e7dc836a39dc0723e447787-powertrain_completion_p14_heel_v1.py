"""Distinct broad heel pad, asymmetric rounded outline and seven real tread bands; plain back estimate."""
import bpy,sys,json,math,bmesh
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
R=Path(__file__).resolve().parents[1];name='gear-selector-heel-pad-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True)
P={'schema':1,'package':'P14','component_id':'MOTO-GEAR-SELECTOR-HEEL-PAD-001','source':'creative/research/powertrain-completion-p14-v1/heel-pad-child-plan-v3.json','width_m':.050,'width_range_m':[.042,.065],'depth_m':.035,'depth_range_m':[.028,.045],'body_height_m':.009,'height_range_m':[.006,.014],'tread_height_m':.0008,'tread_height_range_m':[.0005,.0015],'tread_count':7,'count_range':[6,8],'tread_pitch_m':.0065,'tread_halfwidth_m':.0025,'outline_superellipse_exponent':3.3,'outline_asymmetry':{'y_taper':-.08,'x_bias':.025,'x_shear_m':.001},'angular_samples':256,'top_radial_steps':100,'all_dimensions_estimated':True,'scope':'Broad separate heel pad exterior, asymmetric rounded profile and seven broad real tread bands, not cylindrical toe rubber. Back closure plain estimate; underside retention, metal terminal fit and exact tread termination undocumented.','material':{'name':'Proposed dark heel pad rubber','base_color_linear':[.018,.020,.022,1],'metallic':0,'roughness':.62},'package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);N=256;V=[];F=[]
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def outline(a):
 c,s=math.cos(a),math.sin(a);r=(abs(c/.025)**3.3+abs(s/.0175)**3.3)**(-1/3.3);q=1-.08*s+.025*c;x=r*c*q;y=r*s*q;return x+.001*y/.0175,y
def topz(x,rho):
 band=max(1-smooth((abs(x-k*.0065)-.0015)/.001)for k in range(-3,4));fade=1-smooth((rho-.78)/.22);return .009+.0008*band*fade
V.append((0,0,topz(0,0)));rings=[]
for k in range(1,101):
 rho=k/100;idx=len(V);rings.append(idx)
 for i in range(N):x,y=outline(i*math.tau/N);x*=.90*rho;y*=.90*rho;V.append((x,y,topz(x,rho)))
for i in range(N):F.append((0,rings[0]+i,rings[0]+(i+1)%N))
for a,b in zip(rings,rings[1:]):
 for i in range(N):j=(i+1)%N;F.append((a+i,b+i,b+j,a+j))
# Rounded shoulder -> full shaped wall -> rounded underside perimeter, all continuous geometry.
prev=rings[-1]
for scale,z in [(.94,.00885),(.975,.0084),(.994,.0077),(1,.0068),(1,.002),(.985,.001),(.95,.0003),(.92,0)]:
 idx=len(V)
 for i in range(N):x,y=outline(i*math.tau/N);V.append((scale*x,scale*y,z))
 for i in range(N):j=(i+1)%N;F.append((prev+i,idx+i,idx+j,prev+j))
 prev=idx
pole=len(V);V.append((0,0,0))
for i in range(N):F.append((prev+i,pole,prev+(i+1)%N))
ob=mesh_object('SELECTOR_BROAD_HEEL_PAD_SEVEN_TRANSVERSE_TREADS',V,F);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
for e in bm.edges:e.smooth=not(e.is_manifold and e.calc_face_angle(0)>math.radians(40))
bm.to_mesh(ob.data);bm.free();ob.data.update();ob['scope']=P['scope'];finish_source(H,O,P)
