"""PF113002 left passenger stay original source-constrained candidate, no fitted assembly."""
import bpy,sys,json
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import finish_source
from powertrain_continuation_stay_shapes_v1 import arm,extrude,eye
from powertrain_continuation_shapes_v2 import cyl,boolean
from powertrain_continuation_loft_v4 import clean_smooth
R=Path(__file__).resolve().parents[1];name='passenger-footrest-stay-left-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name
H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
S=json.loads((R/'creative/research/powertrain-completion-p16-v1/passenger-stay-left-shape-choices-v45.json').read_text())
P=dict(schema=1,package='P16',component_id='MOTO-PASSENGER-FOOTREST-STAY-LEFT-001',part_code='PF113002',source='creative/research/powertrain-completion-p16-v1/passenger-stay-left-plan-v41.json',shape_choices=S,all_dimensions_estimated=True,camera_calibrated=False,scope='Separate left passenger stay exterior study: two unequal splayed formed arms with rounded flattened pierced ends, annular upper eye with interpreted fine internal relief, skew gusset, continuous U clevis with two true side holes and bounded rear root pockets. Tube interiors excluded; thread pitch/hand/flanks, pocket depth, terminal clocking and installed roles/fit uncertified. Not mirrored rider support or passenger peg.',material=dict(name='Proposed charcoal painted passenger support',base_color_linear=[.022,.025,.029,1],metallic=.25,roughness=.35),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
ob,h1,d1=arm('LONG_FORMED_ARM',S['long_arm_bezier_source_m'],0);short,h2,d2=arm('SHORT_CLOCKED_FORMED_ARM',S['short_arm_bezier_source_m'],45)
boolean(ob,short,'UNION','Two source splayed arms');boolean(ob,eye('UPPER_EYE_FINE_RELIEF',.3044),'UNION','Upper eye joins arms')
ps=[((x-547)*.0004,(880-y)*.0004)for x,y in S['gusset_source_pixels']]
boolean(ob,extrude('SOURCE_SKEW_GUSSET',ps,2,.0015,.0045),'UNION','Gusset joins arms')
y=-.0+.239
poly=[(y-.011,.0035),(y+.011,.0035),(y+.011,.022),(y+.008,.022),(y+.008,.0065),(y-.008,.0065),(y-.008,.022),(y-.011,.022)]
boolean(ob,extrude('CONTINUOUS_U_CLEVIS',poly,0,-.018,.006),'UNION','Clevis base overlaps gusset')
for i,(h,d)in enumerate([(h1,d1),(h2,d2)]):boolean(ob,cyl(h-d*.025,h+d*.025,.0044),'DIFFERENCE','Terminal actual aperture '+str(i))
boolean(ob,cyl((-.006,.21,.0145),(-.006,.27,.0145),.0044),'DIFFERENCE','Two cheek holes along Y')
for row in S['root_opening_studies']:
 x,y=row['center_xy_m'];boolean(ob,cyl((x,y,-.020),(x,y,row['working_back_pocket_floor_z_m']),row['radius_m']),'DIFFERENCE','Finite rear root pocket not certified drain')
clean_smooth(ob);ob.name='PF113002_LEFT_PASSENGER_STAY_FORMED_ARMS_EYE_GUSSET_U_CLEVIS';ob['scope']=P['scope'];finish_source(H,O,P)
