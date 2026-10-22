"""Separate original30191038 exterior pin: rounded head, plain shank and true cross drill."""
import bpy,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import finish_source
from powertrain_continuation_shapes_v2 import cyl,boolean
from powertrain_continuation_lathe_v1 import solid_profile
from powertrain_continuation_loft_v4 import clean_smooth
R=Path(__file__).resolve().parents[1];name='brake-linkage-headed-pin-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
profile=[(0,0),(.0028,0),(.003,.0002),(.003,.0176),(.0032,.018),(.0039,.018),(.0042,.0183),(.0042,.0192),(.0038,.0198),(0,.0198)]
P=dict(schema=1,package='P15',component_id='MOTO-BRAKE-LINKAGE-HEADED-PIN-001',part_code='30191038',source='creative/research/powertrain-completion-p15-v1/clevis-pin-plan-v12.json',profile_r_z_m=profile,cross_drill_diameter_m=.0024,cross_drill_centre_z_m=.0028,all_dimensions_estimated=True,camera_calibrated=False,scope='Separate original30191038 visible exterior from two physical photos: constant plain shank, shallow rounded head and actual transverse hole. Not JB161002, not threaded rod terminal. Metric scale, head crown, stack/cotter and installed currentRDC fit unqualified. Existing clevis/rod unchanged and excluded.',material=dict(name='Proposed plain lightly plated linkage pin',base_color_linear=[.40,.40,.37,1],metallic=.8,roughness=.30),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
ob=solid_profile('LINKAGE_PIN_30191038_ROUNDED_HEAD_PLAIN_SHANK_CROSS_DRILL',profile)
boolean(ob,cyl((-.010,0,.0028),(.010,0,.0028),.0012),'DIFFERENCE','Actual transverse pin opening')
clean_smooth(ob);ob['scope']=P['scope'];finish_source(H,O,P)
