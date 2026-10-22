"""Original photographed LH reverse window catch and two visible taper gussets, not whole cover."""
import bpy,sys,json,math,bmesh
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
from powertrain_continuation_loft_v4 import clean_smooth,recalc
R=Path(__file__).resolve().parents[1];name='side-cover-left-window-catch-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
planpath='creative/research/powertrain-completion-p01-v1/left-reverse-window-catch-plan-v87.json';plan=json.loads((R/planpath).read_text());P=dict(schema=1,package='P01',component_id=plan['component_id'],source=planpath,scope=plan['scope'],variant=plan['variant'],all_dimensions_estimated=True,camera_calibrated=False,working_frame_width_m=.018,working_frame_height_m=.009,working_frame_thickness_m=.002,working_window_m=[.011,.0035],gusset_run_m=.030,gusset_thickness_m=.0016,material=dict(name='Proposed clean black injection moulded cover catch',base_color_linear=[.014,.016,.019,1],metallic=0,roughness=.42),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
def rectangle(w,h,r):
 out=[]
 for cx,cz,a in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
  for j in range(20):
   t=math.radians(a+j*90/20);out.append((cx+r*math.cos(t),.020+cz+r*math.sin(t)))
 return out
# Same angular corner indexing gives straight paired edge bridges through finite depth.
outer=rectangle(.018,.009,.0009);inner=rectangle(.011,.0035,.00055);N=len(outer);V=[(x,y,z) for y in [0,.002]for loop in [outer,inner]for x,z in loop];F=[]
for i in range(N):
 j=(i+1)%N;F.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
ob=mesh_object('LH_RECTANGULAR_WINDOW_CATCH_TWO_LONG_TAPER_GUSSETS',V,F);recalc(ob)
for x in [-.0075,.0075]:
 poly=[[-.030,0],[.001,.0145],[.001,.0178],[-.030,.0016]];n=len(poly);V=[(xx,y,z)for xx in [x-.0008,x+.0008]for y,z in poly];F=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]
 fin=mesh_object('Visible taper gusset construction',V,F);recalc(fin);bpy.context.view_layer.objects.active=ob;m=ob.modifiers.new('Actual finite overlap at frame side leg','BOOLEAN');m.operation='UNION';m.solver='EXACT';m.object=fin;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(fin,do_unlink=True)
bpy.context.view_layer.objects.active=ob;m=ob.modifiers.new('Bounded injection edge softening','BEVEL');m.width=.00018;m.segments=4;m.limit_method='ANGLE';m.angle_limit=.5;bpy.ops.object.modifier_apply(modifier=m.name);clean_smooth(ob);ob['scope']=P['scope'];finish_source(H,O,P)
(O/'catch-construction-check.json').write_text(json.dumps(dict(method='Finite rounded rectangular open frame with two observed longitudinal taper gussets boolean-united at visible side legs; small bounded edge rounding',window_open=True,hidden_tooth_built=False,full_backing_plate_built=False,root_boundary='Two finite thin parent-interface cuts; no registration to frozen shell',scope='Morphology from used black BM150 source only; exact redRDC variant and installed retention unqualified'),indent=2)+'\n')
