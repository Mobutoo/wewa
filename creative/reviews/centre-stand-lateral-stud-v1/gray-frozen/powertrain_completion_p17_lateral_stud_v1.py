"""Original short observed lateral centre-stand stud, mechanical function unassigned."""
import bpy,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import finish_source
from powertrain_continuation_lathe_v1 import solid_profile
from powertrain_continuation_loft_v4 import clean_smooth
R=Path(__file__).resolve().parents[1];name='centre-stand-lateral-stud-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
profile=[(0,0),(.0034,0),(.00375,.0003),(.00375,.0107),(.004,.011),(.005,.011),(.0055,.0116),(.0055,.0132),(.0048,.014),(0,.014)]
P=dict(schema=1,package='P17',component_id='MOTO-CENTRE-STAND-LATERAL-STUD-001',source='creative/research/powertrain-completion-p17-v1/centre-lateral-stud-plan-v15.json',profile_r_z_m=profile,all_dimensions_estimated=True,camera_calibrated=False,scope='Separate short lateral stud observed near left leg/crossbar in PF113224 photo. Rounded enlarged terminal and smaller plain neck are bounded silhouette estimates; no spring-anchor/stop function certified. No unseen hole/thread, installed frame/root/weld or travel claimed. Existing frame, operating arm and side-stand anchor excluded unchanged.',material=dict(name='Proposed plain dark stand coating',base_color_linear=[.012,.014,.017,1],metallic=.15,roughness=.32),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);ob=solid_profile('OBSERVED_CENTRE_FRAME_LATERAL_STUD_UNASSIGNED_FUNCTION',profile,q=.00018);clean_smooth(ob);ob['scope']=P['scope'];finish_source(H,O,P)
