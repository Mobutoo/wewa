"""Original bounded upper carb casting; existing cap/elbow remain separate and untouched."""
import bpy,bmesh,math,sys,json
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
R=Path(__file__).resolve().parents[1];name='carburettor-upper-casting-v1'
H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name
H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
P={'schema':1,'package':'P19','component_id':'MOTO-CARBURETTOR-UPPER-CASTING-001','source':'creative/research/powertrain-completion-p19-v1/main-casting-child-plan-v3.json','all_dimensions_estimated':True,'camera_calibrated':False,'scope':'Upper main casting exterior study: continuous flared annular inlet, intersecting barrel and pierced noncircular side flange. Lower casting and bowl excluded. Hidden wall and bore junction approximate; no valve surfaces, threads, OEM dimensions, installed fit or functioning airflow claimed. Existing cap/elbow not duplicated.','material':{'name':'Proposed clean cast alloy','base_color_linear':[.31,.33,.35,1],'metallic':.65,'roughness':.43},'package_complete':False,'art_accepted':False}
# Closed cross section, outer neck to rounded bell lip and inner returning airway.
profile=[(.017,-.032),(.017,-.022),(.0176,-.014),(.019,-.006),(.022,.003),(.0255,.011),(.027,.015),(.0272,.017),(.027,.018),(.0264,.0185),(.0256,.0182),(.025,.0175),(.0248,.015),(.0233,.011),(.020,.003),(.0165,-.006),(.014,-.014),(.013,-.022),(.013,-.032)]
P['bell_profile_r_z_m']=profile;P['barrel_OD_m']=.036;P['barrel_axis']='X; working exterior coordinates, not vehicle coordinates';P['barrel_cap_cut_x_m']=-.048
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n')
bpy.ops.wm.read_factory_settings(use_empty=True)
# Rounded corners via bounded quadratic fillets; no overshooting spline.
pts=[Vector(p)for p in profile];corners=[];curve=[]
for i,b in enumerate(pts):
 a,c=pts[i-1],pts[(i+1)%len(pts)];q=min(.00035,(b-a).length*.22,(c-b).length*.22);corners.append((b-(b-a).normalized()*q,b,b+(c-b).normalized()*q))
for i,(a,b,c) in enumerate(corners):
 for j in range(5):
  t=j/5;curve.append((1-t)**2*a+2*(1-t)*t*b+t*t*c)
 end=c;next_start=corners[(i+1)%len(corners)][0]
 for j in range(3):curve.append(end.lerp(next_start,j/3))
N=192
# Start with a solid exterior loft, then cut the lumen once after the unions.
# This avoids coincident inner walls at the branch intersection.
curve=[Vector(p) for p in profile[:10]]
V=[(r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z)for r,z in curve for i in range(N)]
F=[tuple(reversed(range(N))),tuple((len(curve)-1)*N+i for i in range(N))]
for k in range(len(curve)-1):
 for i in range(N):
  a=k*N+i;b=k*N+(i+1)%N;c=((k+1)%len(curve))*N+(i+1)%N;d=((k+1)%len(curve))*N+i;F.append((a,b,c,d))
ob=mesh_object('UPPER_MAIN_CASTING_BELL_BARREL_AND_SIDE_FLANGE',V,F)
def boolean(cut,op,label):
 bpy.context.view_layer.objects.active=ob;m=ob.modifiers.new(label,'BOOLEAN');m.operation=op;m.solver='EXACT';m.object=cut;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True)
def cylinder(radius,depth,loc,axis):
 bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=radius,depth=depth,location=loc,rotation=axis);return bpy.context.object
# Cast barrel intersects the neck with a genuine union, then its open cap seat is cut.
boolean(cylinder(.018,.051,(-.0225,0,-.017),(0,math.pi/2,0)),'UNION','Cast barrel root union')
# Noncircular side flange traced as an oval upper shoulder plus lower pierced ear.
outline=[(-.010,.005),(-.013,-.001),(-.013,-.010),(-.009,-.016),(-.003,-.018),(.003,-.016),(.009,-.010),(.011,-.001),(.009,.005),(.005,.009),(-.004,.009)]
V=[(x-.020,y,z-.015)for y in [-.027,-.010]for x,z in outline];n=len(outline)
F=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]
flange=mesh_object('Side port flange union construction',V,F)
bm=bmesh.new();bm.from_mesh(flange.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(flange.data);bm.free()
boolean(flange,'UNION','Noncircular side flange union')
boolean(cylinder(.0138,.065,(-.024,0,-.017),(0,math.pi/2,0)),'DIFFERENCE','Estimated open slide barrel bore')
boolean(cylinder(.0065,.070,(-.020,-.011,-.014),(math.pi/2,0,0)),'DIFFERENCE','Visible side port')
boolean(cylinder(.002,.040,(-.023,-.023,-.027),(math.pi/2,0,0)),'DIFFERENCE','Visible lower flange ear bore')
# Remove internal union obstruction from axial neck only, preserving flared lip.
# Clear the entire flared airway through unioned branch walls; a straight neck
# cutter alone leaves false terraces inside the visible bell.
air=[(.01301,-.060),(.01301,-.022),(.01401,-.014),(.01651,-.006),(.02001,.003),(.02331,.011),(.02481,.015),(.02501,.0175),(.02561,.0182),(.02641,.0185),(.02641,.045)]
V=[(r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z)for r,z in air for i in range(N)]
F=[tuple(reversed(range(N))),tuple((len(air)-1)*N+i for i in range(N))]
for k in range(len(air)-1):
 for i in range(N):F.append((k*N+i,k*N+(i+1)%N,(k+1)*N+(i+1)%N,(k+1)*N+i))
boolean(mesh_object('Full flared airway cutter',V,F),'DIFFERENCE','Continuous flared airway clearance')
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
for f in bm.faces:f.smooth=True
for e in bm.edges:e.smooth=not(e.is_manifold and e.calc_face_angle(0)>math.radians(35))
bm.to_mesh(ob.data);bm.free();ob.data.update();ob['scope']=P['scope']
finish_source(H,O,P)
