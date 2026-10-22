"""Major conditional-donor LH halfcase external walls from six matched used-part poses. No engine internals."""
import bpy,sys,json,math,bmesh
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
from powertrain_continuation_loft_v4 import clean_smooth,recalc
R=Path(__file__).resolve().parents[1];name='crankcase-lh-major-outer-envelope-donor-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
planpath='creative/research/powertrain-completion-p18-v1/lh-major-outer-envelope-donor-plan-v97.json';plan=json.loads((R/planpath).read_text());P=dict(schema=1,package='P18',component_id=plan['component_id'],source=planpath,source_identity=plan['source_identity'],scope=plan['scope'],relation_to_existing=plan['relation_to_existing'],all_dimensions_estimated=True,camera_calibrated=False,working_scale_m_px=.00044,working_axial_depth_m=.058,working_wall_m=.0045,working_broad_crown_m=.003,outline_controls_pixels=plan['outline_controls_pixels_65221'],material=dict(name='Proposed clean cast aluminium conditional donor case',base_color_linear=[.33,.35,.37,1],metallic=.7,roughness=.44),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
C=[Vector(((x-350)*.00044,(550-y)*.00044))for x,y in P['outline_controls_pixels']]
def spline(i,t):
 p=[C[(i+j)%len(C)]for j in range(4)];w=[(1-t)**3/6,(3*t**3-6*t*t+4)/6,(-3*t**3+3*t*t+3*t+1)/6,t**3/6];dw=[-(1-t)**2/2,(9*t*t-12*t)/6,(-9*t*t+6*t+3)/6,t*t/2];return [sum((a*b for a,b in zip(p,weights)),Vector((0,0)))for weights in [w,dw]]
curves=[spline(i,j/16)for i in range(len(C))for j in range(16)];N=len(curves);M=64;area=sum(q.x*r.y-r.x*q.y for (q,_),(r,__)in zip(curves,curves[1:]+curves[:1]));V=[];F=[]
for inner in [False,True]:
 for k in range(M+1):
  u=k/M;crown=.003*math.sin(math.pi*u)**2
  for q,t in curves:
   normal=Vector((-t.y,t.x)).normalized()*(1 if area>0 else -1);p=q+normal*(.0045 if inner else -crown);V.append((p.x,p.y,-.058*u))
S=(M+1)*N
for k in range(M):
 for i in range(N):
  j=(i+1)%N;a=k*N+i;b=k*N+j;c=(k+1)*N+j;d=(k+1)*N+i;F.extend([(a,b,c,d),(S+a,S+d,S+c,S+b)])
for i in range(N):
 j=(i+1)%N;F.extend([(i,S+i,S+j,j),(M*N+i,M*N+j,S+M*N+j,S+M*N+i)])
ob=mesh_object('MAJOR_LH_DONOR_EXTERIOR_PERIPHERAL_CAST_WALLS_OPEN_ENGINE_VOID',V,F);recalc(ob)
def cut_cylinder(label,r,depth,loc,rot=(0,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=192,radius=r,depth=depth,location=loc,rotation=rot);tool=bpy.context.object;recalc(tool);bpy.context.view_layer.objects.active=ob;m=ob.modifiers.new(label,'BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=tool;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(tool,do_unlink=True)
# Half cylinder-base saddle is open at the donor split plane, not a hidden cylinder bore.
cut_cylinder('Observed upper half-saddle opening, estimated donor interface',.039,.200,(-.0506,.178,-.058),(math.pi/2,0,0))
# Actual lower service aperture is separate from the neck child; no cap or unseen gallery.
cut_cylinder('Source-projected lower service neck clearance',.022,.20,(-.07436,-.0924,-.029))
clean_smooth(ob);ob['scope']=P['scope'];ob['identity']='CONDITIONAL_DONOR_NOT_EXACT_CURRENT_RDC125';finish_source(H,O,P)
(O/'envelope-construction-check.json').write_text(json.dumps(dict(method='Source-shaped periodic cubic perimeter and paired finite skin, smooth broad axial crown; genuine geometric top half-saddle and lower service clearance',perimeter_samples=N,axial_samples=M+1,arbitrary_engine_void_closure=False,internal_bearings_or_galleries=False,cover_cylinder_head_rebuilt=False,source_identity=plan['source_identity'],review_edges=['Centre split plane','Outboard cover/output-face interface'],remaining=['Outboard lip fastener details and additional mounting boss groups remain distinct studies','Existing lower wall is alternative subset, not second physical wall','Metric variant/installed fit unqualified']),indent=2)+'\n')
