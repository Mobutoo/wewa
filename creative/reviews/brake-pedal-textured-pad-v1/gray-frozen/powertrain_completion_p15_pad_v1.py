"""P15 terminal pad with real mesh grip relief and rounded perimeter; no vendor pixels."""
import bpy,sys,json,math,bmesh
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
R=Path(__file__).resolve().parents[1];name='brake-pedal-textured-pad-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True)
P={'schema':1,'package':'P15','component_id':'MOTO-BRAKE-PEDAL-TEXTURED-PAD-001','source':'creative/research/powertrain-completion-p15-v1/textured-pad-plan-v4.json','width_m':.045,'width_range_m':[.035,.055],'depth_m':.040,'depth_range_m':[.032,.050],'body_thickness_m':.0035,'thickness_range_m':[.002,.006],'tread_pitch_m':.0025,'pitch_range_m':[.0018,.0035],'tread_height_m':.0004,'height_range_m':[.0002,.0008],'outline_superellipse_exponent':4,'top_grid_steps':[160,144],'outline_taper':.04,'source_triangulation':'Explicit before crease normals; 35 degree sharp boundaries on actual relief triangles','all_dimensions_estimated':True,'scope':'Photo-visible broad rounded terminal pad and dense grip pattern, real mesh relief not a normal map. Pattern/pitch/count and rolled die section approximate. Plain back closure only; backside weld, arm contact, installed angle/travel and actual grip not certified. Prior arm/sleeve/lug unchanged.','material':{'name':'Proposed coated pedal pad','base_color_linear':[.013,.015,.018,1],'metallic':.15,'roughness':.34},'package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);nx,ny=160,144;V=[];F=[]
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def pos(u,v):
 rho=max(abs(u),abs(v))
 if rho<1e-12:return 0,0,rho
 a=math.atan2(v,u);c,s=math.cos(a),math.sin(a);r=(abs(c/.0225)**4+abs(s/.020)**4)**(-.25);q=1-.04*s;return rho*r*c*q,rho*r*s,rho
def near(t):return abs(t-round(t))
for j in range(ny+1):
 for i in range(nx+1):
  x,y,rho=pos(-1+2*i/nx,-1+2*j/ny);u=(x+y)/math.sqrt(2)/.0025;v=(y-x)/math.sqrt(2)/.0025;relief=max(0,1-(near(u)+near(v))/.42);fade=1-smooth((rho-.86)/.14);z=.003+.0005*smooth((1-rho)/.08)+.0004*relief*fade;V.append((x,y,z))
for j in range(ny):
 for i in range(nx):a=j*(nx+1)+i;F.append((a,a+1,a+nx+2,a+nx+1))
# CCW boundary reuses the grid, with two formed lower perimeter bands then a plain back.
boundary=list(range(nx+1))+[j*(nx+1)+nx for j in range(1,ny+1)]+[ny*(nx+1)+i for i in range(nx-1,-1,-1)]+[j*(nx+1)for j in range(ny-1,0,-1)];prev=boundary;N=len(prev)
for scale,z in [(1,.0007),(.985,.0002),(.965,0)]:
 cur=[]
 for idx in boundary:x,y,_=V[idx];cur.append(len(V));V.append((scale*x,scale*y,z))
 for i in range(N):j=(i+1)%N;F.append((prev[i],cur[i],cur[j],prev[j]))
 prev=cur
pole=len(V);V.append((0,0,0))
for i in range(N):F.append((prev[i],pole,prev[(i+1)%N]))
ob=mesh_object('BRAKE_PEDAL_ROUNDED_PAD_WITH_REAL_DIAMOND_RELIEF',V,F);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
for f in bm.faces:
 if max(v.co.z for v in f.verts)<1e-8 or max(v.co.z for v in f.verts)-min(v.co.z for v in f.verts)>.002:f.smooth=False
for e in bm.edges:e.smooth=not(e.is_manifold and e.calc_face_angle(0)>math.radians(35))
bm.to_mesh(ob.data);bm.free();ob.data.update();ob['scope']=P['scope'];finish_source(H,O,P)
