"""P14 first child: documented two-arm bent steel body, not a generic single-toe lever."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
R=Path(__file__).resolve().parents[1];H=R/'assets-src/moto-components/gear-selector-arm-v1';O=R/'creative/reviews/gear-selector-arm-v1';H.mkdir(parents=True,exist_ok=True)
# X toe(-) to heel(+), Y up, Z outward. Working dimensions are estimated.
controls=[[-.145,.036,-.009,.018],[-.125,.035,-.009,.018],[-.080,.018,-.005,.020],[-.035,.003,-.002,.024],[0,0,0,.030],[.025,.001,.002,.026],[.060,.012,.006,.021],[.110,.037,.009,.018],[.140,.045,.009,.018]]
P={'schema':1,'package':'P14','component_id':'MOTO-GEAR-SELECTOR-ARM-001','controls_x_y_z_width_m':controls,'thickness_m':.005,'thickness_range_m':[.0035,.007],'edge_radius_m':.0008,'length_range_m':[.24,.33],'selected_length_m':.285,'center_clearance_radius_m':.0065,'center_clearance_radius_range_m':[.005,.009],'clearance_status':'Estimated visible through-clearance only, no spline/hub seat claim','section_samples_per_corner':12,'path_samples_per_span':18,'all_dimensions_estimated':True,'sources':'creative/research/powertrain-completion-p14-v1/plan.json','scope':'Bent metal body only. Split hub, rubbers and clamp hardware deferred. Root bore is estimated clearance, no spline count invented.','frame':'Unplaced local X toe(-)/heel(+), Y up, Z outward','material':{'name':'Proposed black painted steel','base_color_linear':[.012,.014,.017,1],'metallic':.15,'roughness':.33},'package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
pts=[Vector(v)for v in controls];path=[]
for i in range(len(pts)-1):
 a,b,c,d=[pts[max(0,min(len(pts)-1,j))]for j in [i-1,i,i+1,i+2]]
 for j in range(P['path_samples_per_span']):
  t=j/P['path_samples_per_span'];path.append(.5*(2*b+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
path.append(pts[-1]);N=48;V=[];F=[]
for k,p in enumerate(path):
 prev=path[max(k-1,0)];nxt=path[min(k+1,len(path)-1)];tan=Vector((nxt.x-prev.x,nxt.y-prev.y,0)).normalized();widthaxis=Vector((-tan.y,tan.x,0));r=P['edge_radius_m'];w=p.w/2;h=P['thickness_m']/2
 for cy,cz,start in [(w-r,h-r,0),(-w+r,h-r,90),(-w+r,-h+r,180),(w-r,-h+r,270)]:
  for j in range(12):
   a=math.radians(start+j*90/12);u=cy+r*math.cos(a);v=cz+r*math.sin(a);q=Vector(p[:3])+widthaxis*u+Vector((0,0,v));V.append(tuple(q))
for k in range(len(path)-1):
 a=k*N;b=a+N
 for i in range(N):j=(i+1)%N;F.append((a+i,a+j,b+j,b+i))
F.append(tuple(reversed(range(N))));F.append(tuple((len(path)-1)*N+i for i in range(N)))
ob=mesh_object('SELECTOR_TWO_BENT_ARMS_METAL',V,F)
# Cut tool is not exported; no spline or root coupling invented.
bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=P['center_clearance_radius_m'],depth=.08,location=(0,0,0));cutter=bpy.context.object;bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Estimated root through-clearance','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
if hasattr(ob.data,'set_sharp_from_angle'):ob.data.set_sharp_from_angle(angle=math.radians(40))
ob['scope']=P['scope'];finish_source(H,O,P)
