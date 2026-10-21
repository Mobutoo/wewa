"""Separate lower main casting: asymmetric shell, bowl ledge, observed external seats."""
import bpy,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import finish_source
from powertrain_continuation_shapes_v2 import shell,cyl,boolean,clean
R=Path(__file__).resolve().parents[1];name='carburettor-lower-body-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
rings=[(.004,0,-.018,.016,.016),(.006,0,-.018,.018,.018),(.010,0,-.017,.023,.021),(.020,0,-.015,.026,.024),(.030,0,-.014,.027,.024),(.032,0,-.014,.029,.0255),(.034,0,-.014,.0295,.0255),(.036,0,-.014,.0295,.0255),(.036,0,-.014,.026,.022),(.033,0,-.014,.0255,.0215),(.028,0,-.014,.0235,.0205),(.018,0,-.016,.0215,.0185),(.011,0,-.018,.014,.013)]
P={'schema':1,'package':'P19','component_id':'MOTO-CARBURETTOR-LOWER-BODY-001','source':'creative/research/powertrain-completion-p19-v1/lower-body-plan-v4.json','ring_sections_x_cy_cz_ry_rz_m':rings,'section_exponent':2.8,'asymmetry':'1+.075*cos(theta)+.025*sin(2theta) in lateral coordinate','all_dimensions_estimated':True,'camera_calibrated':False,'scope':'Lower main casting only: asymmetric swollen shell and continuous bowl-joint ledge, two distinct visible side seats and two joint-ear bore studies. Basic cavity and upper back closure are estimated finite review boundaries. No float/galleries/threads or installed upper/body/bowl registration certified. Frozen upper casting and separate bowl unchanged/excluded.','material':{'name':'Proposed clean lower cast alloy','base_color_linear':[.31,.33,.35,1],'metallic':.65,'roughness':.43},'package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
ob=shell('LOWER_MAIN_CASTING_ASYMMETRIC_SHELL_AND_BOWL_LEDGE',rings)
for label,x,z,r,outer,inner,bore in [('Large side plug seat',.022,-.010,.006,-.036,-.017,.003),('Small external port seat',.013,.004,.0045,-.031,-.012,.002)]:
 boolean(ob,cyl((x,outer,z),(x,inner,z),r),'UNION',label+' root')
 boolean(ob,cyl((x,outer-.010,z),(x,.004,z),bore),'DIFFERENCE',label+' visible bore')
for i,y in enumerate([-.028,.027]):
 boolean(ob,cyl((.0292,y,-.018),(.0367,y,-.018),.0055),'UNION','Visible joint ear '+str(i))
 boolean(ob,cyl((.022,y,-.018),(.045,y,-.018),.002),'DIFFERENCE','Joint attachment bore '+str(i))
clean(ob);ob['scope']=P['scope'];finish_source(H,O,P)
