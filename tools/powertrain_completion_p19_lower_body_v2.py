"""New continuous finite-wall lower casting revision; frozen v1 remains unmodified."""
import bpy,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import finish_source
from powertrain_continuation_shapes_v2 import cyl,boolean
from powertrain_continuation_loft_v4 import wall,clean_smooth,soft_cyl
R=Path(__file__).resolve().parents[1];name='carburettor-lower-body-v2';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
# Outer casting -> rounded perimeter ledge -> inner finite wall -> rounded upper review rim.
controls=[(.004,.016,.016,0),(.004,.018,.018,0),(.010,.023,.021,0),(.020,.026,.024,0),(.028,.027,.024,0),(.032,.029,.0255,0),(.035,.030,.026,0),(.037,.029,.025,0),(.037,.026,.022,0),(.033,.025,.021,0),(.026,.023,.020,0),(.017,.020,.0175,0),(.008,.014,.0125,0),(.004,.013,.012,0)]
P=dict(schema=1,package='P19',component_id='MOTO-CARBURETTOR-LOWER-BODY-001',source='creative/research/powertrain-completion-p19-v1/lower-body-rework-plan-v9.json',control_sections_x_ry_rz_cy_m=controls,all_dimensions_estimated=True,camera_calibrated=False,scope='New C2 finite-wall lower casting envelope with rounded annular upper/bowl review boundaries, no large transverse closure disc. Visible seats and two separated attachments retained as source-limited exterior studies. Open interface boundaries and inner wall are estimates, NOT certified actual galleries or installed upper/body/bowl fit. Frozen v1 remains rework nonaccepted and unchanged.',material=dict(name='Proposed lower casting alloy v2',base_color_linear=[.31,.33,.35,1],metallic=.65,roughness=.43),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
ob,report=wall('LOWER_CASTING_C2_FINITE_WALL_OPEN_REVIEW_INTERFACES',controls);(O/'section-continuity-check.json').write_text(json.dumps(report,indent=2)+'\n')
for label,x,z,r,outer,inner,bore in [('Large side seat',.026,-.017,.006,-.036,-.017,.003),('Small visible seat',.018,-.003,.0045,-.031,-.012,.002)]:
 boolean(ob,soft_cyl(cyl,(x,outer,z),(x,inner,z),r),'UNION',label+' softened rim/root')
 boolean(ob,cyl((x,outer-.010,z),(x,.004,z),bore),'DIFFERENCE',label+' observed mouth')
for i,y in enumerate([-.028,.027]):
 boolean(ob,soft_cyl(cyl,(.0292,y,-.018),(.0367,y,-.018),.0055),'UNION','Joint ear '+str(i))
 boolean(ob,cyl((.022,y,-.018),(.045,y,-.018),.002),'DIFFERENCE','Attachment bore '+str(i))
clean_smooth(ob);ob['scope']=P['scope'];finish_source(H,O,P)
