"""Photo-informed mid-arm pierced lug; no root weld or pin fit invention."""
import bpy,sys,json,math,bmesh
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
R=Path(__file__).resolve().parents[1];name='brake-pedal-linkage-lug-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True)
outline=[[-.011,.013],[.011,.013],[.009,-.014],[-.009,-.014]]
P={'schema':1,'package':'P15','component_id':'MOTO-BRAKE-PEDAL-LINKAGE-LUG-001','source':'creative/research/powertrain-completion-p15-v1/linkage-lug-child-plan-v3.json','outline_xy_m':outline,'outline_corner_radius_m':.001,'width_range_m':[.017,.027],'height_range_m':[.020,.034],'sheet_thickness_m':.003,'thickness_range_m':[.002,.0045],'hole_center_xy_m':[0,-.005],'hole_diameter_m':.009,'hole_range_m':[.007,.011],'edge_bevel_m':.00025,'bevel_range_m':[.0001,.0005],'all_dimensions_estimated':True,'scope':'Photo-observed tapered flat mid-arm lug, real single through-hole, bounded rounded corners/edges. Root weld, opposite face details, actual offset and pin/rod fit unqualified. Separate unplaced child; prior arm and sleeve immutable.','material':{'name':'Proposed coated linkage lug','base_color_linear':[.013,.015,.018,1],'metallic':.15,'roughness':.30},'package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);pts=[Vector(p)for p in outline];curve=[]
for i,b in enumerate(pts):
 a,c=pts[(i-1)%len(pts)],pts[(i+1)%len(pts)];q=.001;u=b+(a-b).normalized()*q;v=b+(c-b).normalized()*q
 for j in range(12):t=j/12;curve.append((1-t)**2*u+2*(1-t)*t*b+t*t*v)
# Explicit ray-to-outline annular bands avoid a Boolean bridge seam across flat faces.
N=256;center=Vector((0,-.005));distances=[]
for i in range(N):
 a=i*math.tau/N;d=Vector((math.cos(a),math.sin(a)));hits=[]
 for j,p in enumerate(curve):
  q=curve[(j+1)%len(curve)];e=q-p;v=p-center;den=d.x*e.y-d.y*e.x
  if abs(den)<1e-12:continue
  t=(v.x*e.y-v.y*e.x)/den;u=(v.x*d.y-v.y*d.x)/den
  if t>0 and -.000001<=u<=1.000001:hits.append(t)
 assert hits;distances.append(min(hits))
V=[];F=[]
for mode,z in [('innerlip',-.0015),('outerlip',-.0015),('outer',-.00125),('outer',.00125),('outerlip',.0015),('innerlip',.0015),('inner',.00125),('inner',-.00125)]:
 for i,rmax in enumerate(distances):
  a=i*math.tau/N;r={'inner':.0045,'innerlip':.00475,'outer':rmax,'outerlip':rmax-.00025}[mode];V.append((r*math.cos(a),-.005+r*math.sin(a),z))
for k in range(8):
 a=k*N;b=((k+1)%8)*N
 for i in range(N):j=(i+1)%N;F.append((a+i,a+j,b+j,b+i))
ob=mesh_object('BRAKE_PEDAL_TAPERED_SINGLE_HOLE_LINKAGE_LUG',V,F);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
for f in bm.faces:
 zs=[v.co.z for v in f.verts];r=max((Vector((v.co.x,v.co.y+.005))).length for v in f.verts);f.smooth=abs(f.normal.z)<.999 and not(max(zs)-min(zs)>.0024 and r>.008)
for e in bm.edges:e.smooth=not(e.is_manifold and e.calc_face_angle(0)>math.radians(35))
bm.to_mesh(ob.data);bm.free();ob.data.update();P['section_method']='Explicit flat annular bands between observed hole and rounded tapered outline, bounded straight edge chamfer; no Boolean bridge or post-export repair';P['angular_samples']=N;P['edge_finish']='Straight chamfer estimate rather than rolled radius';(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');ob['scope']=P['scope'];finish_source(H,O,P)
