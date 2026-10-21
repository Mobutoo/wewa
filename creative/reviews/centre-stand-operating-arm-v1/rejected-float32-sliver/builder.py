"""PF113224 separate curved operating arm/roof pedal/pierced gusset, no main frame duplication."""
import bpy,bmesh,sys,json,math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
from powertrain_continuation_sweep_v3 import round_wire,line
from powertrain_continuation_shapes_v2 import boolean,clean,cyl,recalc
R=Path(__file__).resolve().parents[1];name='centre-stand-operating-arm-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name
H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
plan=json.loads((R/'creative/research/powertrain-completion-p17-v1/centre-operating-arm-plan-v14.json').read_text())
def point(p):return Vector(((p[0]-590)*.00064,(490-p[1])*.00064,0))
P=dict(schema=1,package='P17',component_id='MOTO-CENTRE-STAND-OPERATING-ARM-001',source='creative/research/powertrain-completion-p17-v1/centre-operating-arm-plan-v14.json',arm_OD_m=.012,arm_depth_m=.010,pedal_width_m=.023,pedal_estimated_wall_m=.003,gusset_thickness_m=.003,gusset_round_hole_diameter_m=.0064,pixel_scale_m=.00064,all_dimensions_estimated=True,scope='Separate operating arm with original source-constrained bend, curved thin pedal roof and root gusset with round aperture and open triangular relief toward deferred main leg. Main frame/legs/crossbar/pivot/feet NOT duplicated. Working depth, roof underside and wall, root/relief shape and out-of-plane axes estimated; no weld, actual frame registration or installed ground/travel/operating qualification.',material=dict(name='Proposed black centre stand operating arm coating',base_color_linear=[.012,.014,.017,1],metallic=.15,roughness=.34),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
A=[point(p)for p in plan['arm_centreline_pixels']];path=[A[0]]
for i in range(1,len(A)-1):
 a,b,c=A[i-1:i+2];q=min(.008,(b-a).length*.20,(c-b).length*.20);p0=b-(b-a).normalized()*q;p1=b+(c-b).normalized()*q;path+=line(path[-1],p0)
 for j in range(1,33):
  t=j/32;path.append((1-t)**2*p0+2*(1-t)*t*b+t*t*p1)
path+=line(path[-1],A[-1]);ob,report=round_wire('CENTRE_OPERATING_ARM_ELLIPTIC_SECTION',path,.006)
for v in ob.data.vertices:v.co.z*=.010/.012
(O/'arm-centerline-clearance-check.json').write_text(json.dumps(report,indent=2)+'\n')
def extrude_poly(label,ps,half):
 ps=[point(p)for p in ps];N=len(ps);V=[(p.x,p.y,z)for z in [-half,half]for p in ps];F=[tuple(reversed(range(N))),tuple(N+i for i in range(N))]
 for i in range(N):j=(i+1)%N;F.append((i,j,N+j,N+i))
 o=mesh_object(label,V,F);recalc(o);return o
# Curved thin roof, following visible upper profile; no unseen return flanges.
Q=[point(p)for p in plan['pedal_roof_profile_pixels']];roof=[]
def cat(i,t):
 a,b,c,d=Q[max(0,i-1)],Q[i],Q[i+1],Q[min(len(Q)-1,i+2)];return .5*(2*b+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)
for i in range(len(Q)-1):
 for j in range(24):
  t=j/24;v=cat(i,t);u=cat(i,min(1,t+.0001))-cat(i,max(0,t-.0001));u.normalize();roof.append((v,Vector((-u.y,u.x,0))))
u=(Q[-1]-Q[-2]).normalized();roof.append((Q[-1],Vector((-u.y,u.x,0))))
V=[];F=[]
for c,n in roof:
 for a,z in [(-.0015,-.0115),(.0015,-.0115),(.0015,.0115),(-.0015,.0115)]:V.append(tuple(c+n*a+Vector((0,0,z))))
for i in range(len(roof)-1):
 for j in range(4):q=(j+1)%4;F.append((i*4+j,i*4+q,(i+1)*4+q,(i+1)*4+j))
F+=[(3,2,1,0),tuple((len(roof)-1)*4+j for j in range(4))];pedal=mesh_object('CURVED_TERMINAL_THIN_PEDAL_ROOF',V,F);recalc(pedal);bpy.context.view_layer.objects.active=pedal;m=pedal.modifiers.new('Small sheet edge softening','BEVEL');m.width=.0003;m.segments=3;m.limit_method='ANGLE';m.angle_limit=math.radians(25);bpy.ops.object.modifier_apply(modifier=m.name)
boolean(ob,pedal,'UNION','Roof joins arm end')
gusset=extrude_poly('SOURCE_ROOT_GUSSET',plan['gusset_outline_pixels'],.0015);boolean(ob,gusset,'UNION','Root gusset joins arm')
c=point(plan['gusset_round_hole_pixels']);boolean(ob,cyl((c.x,c.y,-.030),(c.x,c.y,.030),.0032),'DIFFERENCE','Visible round gusset aperture')
relief=extrude_poly('OPEN_TRIANGULAR_RELIEF_TOWARD_MAIN_LEG',plan['lower_relief_pixels'],.030);boolean(ob,relief,'DIFFERENCE','Visible triangular root relief')
clean(ob);ob.name='CENTRE_STAND_OPERATING_ARM_CURVED_ROOF_AND_PIERCED_ROOT_GUSSET';ob['scope']=P['scope'];finish_source(H,O,P)
