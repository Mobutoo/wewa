"""Original JB161002 cylindrical rod barrel pin with central actual transverse bore."""
import bpy,sys,json,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import finish_source
from powertrain_continuation_shapes_v2 import cyl,boolean
from powertrain_continuation_lathe_v1 import solid_profile
from powertrain_continuation_loft_v4 import clean_smooth
R=Path(__file__).resolve().parents[1];name='brake-rod-barrel-pin-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
profile=[(0,0),(.00475,0),(.005,.00025),(.005,.01975),(.00475,.020),(0,.020)]
P=dict(schema=1,package='P15',component_id='MOTO-BRAKE-ROD-BARREL-PIN-001',part_code='JB161002',source='creative/research/powertrain-completion-p15-v1/rod-barrel-pin-plan-v13.json',profile_r_z_m=profile,central_transverse_bore_diameter_m=.0062,bore_centre_z_m=.010,entry_edge_softening_m=.00012,all_dimensions_estimated=True,camera_calibrated=False,scope='Separate JB161002 short cylindrical barrel from Crosland physical image of three poses: solid finite circular ends and one central transverse passage with softened mouth. Plain bore, no unseen internal thread/pitch certification. Distinct30191038 headed pin, clevis/rod/springs/adjuster nut and installed stack excluded unchanged; metric fit unqualified.',material=dict(name='Proposed plain lightly plated rod barrel',base_color_linear=[.40,.40,.37,1],metallic=.8,roughness=.30),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);ob=solid_profile('JB161002_SHORT_CYLINDER_SOLID_ENDS_CENTRAL_TRANSVERSE_BORE',profile)
boolean(ob,cyl((-.015,0,.010),(.015,0,.010),.0031),'DIFFERENCE','Central actual transverse passage')
bpy.context.view_layer.objects.active=ob;m=ob.modifiers.new('Small visible bore-entry edge break','BEVEL');m.width=.00012;m.segments=3;m.limit_method='ANGLE';m.angle_limit=math.radians(35);m.use_clamp_overlap=True;bpy.ops.object.modifier_apply(modifier=m.name)
clean_smooth(ob);ob['scope']=P['scope'];finish_source(H,O,P)
