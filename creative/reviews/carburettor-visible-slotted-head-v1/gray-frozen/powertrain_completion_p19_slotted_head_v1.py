"""Original separate visible warm slotted fitting head, function and hidden shaft unassigned."""
import bpy,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import finish_source
from powertrain_continuation_lathe_v1 import solid_profile
from powertrain_continuation_loft_v4 import clean_smooth
from powertrain_continuation_shapes_v2 import boolean
R=Path(__file__).resolve().parents[1];name='carburettor-visible-slotted-head-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
profile=[(0,0),(.0039,0),(.0044,.00025),(.0045,.00055),(.0045,.00195),(.0042,.0024),(.0039,.0025),(0,.0025)]
P=dict(schema=1,package='P19',component_id='MOTO-CARBURETTOR-VISIBLE-SLOTTED-HEAD-001',source='creative/research/powertrain-completion-p19-v1/visible-slotted-head-plan-v12.json',source_clarification='creative/research/powertrain-completion-p19-v1/slotted-head-source-supplement-v14.json',profile_r_z_m=profile,slot_width_m=.0014,slot_depth_m=.0008,slot_bottom_rounding_m=.00012,all_dimensions_estimated=True,camera_calibrated=False,scope='Only separate visible warm round slotted fitting head below inlet on JV581204. Actual finite-depth straight slot; no full hidden shaft, thread, valve, fluid/adjustment function or engagement fabricated. Dark surrounding casting seat is separate lower body and excluded. Rear face is estimated finite review boundary. Frozen castings unchanged.',material=dict(name='Proposed warm plain fitting-head alloy',base_color_linear=[.40,.30,.12,1],metallic=.78,roughness=.29),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
ob=solid_profile('VISIBLE_WARM_ROUND_HEAD_FINITE_STRAIGHT_SLOT',profile,q=.00010)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,.0042));cut=bpy.context.object;cut.dimensions=(.016,.0014,.005);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);m=cut.modifiers.new('Bounded rounded slot bottom','BEVEL');m.width=.00012;m.segments=4;bpy.ops.object.modifier_apply(modifier=m.name)
boolean(ob,cut,'DIFFERENCE','Actual finite-depth slotted face');clean_smooth(ob);ob['scope']=P['scope'];finish_source(H,O,P)
