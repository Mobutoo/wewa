"""P19 visible cable elbow: unequal straight ends, true hollow quarter-bend, no thread/liner invention."""
import bpy,sys,json,math,bmesh
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
R=Path(__file__).resolve().parents[1];name='carburettor-cable-elbow-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True)
P={'schema':1,'package':'P19','component_id':'MOTO-CARBURETTOR-CABLE-ELBOW-001','source':'creative/research/powertrain-completion-p19-v1/cable-elbow-child-plan-v2.json','outer_diameter_m':.009,'outer_range_m':[.007,.012],'inner_diameter_m':.0056,'inner_range_m':[.004,.007],'bend_radius_m':.013,'bend_range_m':[.010,.020],'cap_straight_m':.010,'cap_straight_range_m':[.007,.016],'adjuster_straight_m':.017,'adjuster_straight_range_m':[.012,.025],'bend_angle_deg':90,'bend_angle_range_deg':[75,105],'bend_steps':48,'section_steps':128,'all_dimensions_estimated':True,'scope':'Photo-visible bright metal cable-entry elbow, unequal straight ends and hollow quarter-bend. Wall and plain cut seats are explicit working estimates. Boot, adjuster, threads, cable/liner and installed orientation separate/unqualified. Prior cap unchanged.','material':{'name':'Proposed bright cable elbow','base_color_linear':[.42,.44,.46,1],'metallic':.9,'roughness':.22},'package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
# Local XY bend plane. Exact tangents preserve circular sections at joins without coarse chord mitering.
path=[(Vector((0,0,0)),Vector((-1,0,0))),(Vector((-.010,0,0)),Vector((-1,0,0)))]
for j in range(1,49):
 a=math.pi/2*j/48;path.append((Vector((-.010-.013*math.sin(a),.013-.013*math.cos(a),0)),Vector((-math.cos(a),math.sin(a),0))))
path.append((Vector((-.023,.030,0)),Vector((0,1,0))))
N=128;V=[];F=[]
for radius in [.0045,.0028]:
 for p,t in path:
  n=Vector((-t.y,t.x,0))
  for i in range(N):a=i*math.tau/N;V.append(tuple(p+radius*(math.cos(a)*n+math.sin(a)*Vector((0,0,1)))))
L=len(path);offset=L*N
for inside in [False,True]:
 off=offset if inside else 0
 for k in range(L-1):
  a=off+k*N;b=a+N
  for i in range(N):j=(i+1)%N;f=(a+i,a+j,b+j,b+i);F.append(tuple(reversed(f))if inside else f)
for k in [0,L-1]:
 a=k*N;b=offset+a
 for i in range(N):j=(i+1)%N;F.append((a+i,b+i,b+j,a+j))
ob=mesh_object('CARB_CABLE_ELBOW_HOLLOW_UNEQUAL_END_QUARTER_BEND',V,F);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
for e in bm.edges:e.smooth=not(e.is_manifold and e.calc_face_angle(0)>math.radians(40))
bm.to_mesh(ob.data);bm.free();ob.data.update();ob['scope']=P['scope'];finish_source(H,O,P)
