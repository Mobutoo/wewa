"""Original separate asymmetric float-bowl shell, no supplied mesh or photographed pixels."""
import bpy,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import finish_source
from powertrain_continuation_shapes_v2 import shell,cyl,boolean,clean
R=Path(__file__).resolve().parents[1];name='carburettor-float-bowl-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
rings=[(.063,.004,-.018,.018,.016),(.062,.004,-.018,.020,.018),(.059,.003,-.018,.023,.020),(.052,.002,-.017,.026,.022),(.045,.001,-.015,.0275,.024),(.043,0,-.014,.029,.0255),(.041,0,-.014,.0295,.0255),(.038,0,-.014,.0295,.0255),(.038,0,-.014,.0262,.0222),(.041,0,-.014,.0262,.0222),(.046,.001,-.015,.0245,.0205),(.052,.002,-.017,.022,.0185),(.057,.003,-.018,.018,.015),(.059,.004,-.018,.0145,.0125)]
P={'schema':1,'package':'P19','component_id':'MOTO-CARBURETTOR-FLOAT-BOWL-001','source':'creative/research/powertrain-completion-p19-v1/float-bowl-plan-v5.json','ring_sections_x_cy_cz_ry_rz_m':rings,'section_exponent':2.8,'all_dimensions_estimated':True,'camera_calibrated':False,'scope':'Separate asymmetric float-bowl shell with continuous joint ledge, two visible pierced screw seats and lower connector casting seat. Basic inner floor and unobserved back/underside are bounded approximations. No float, galleries, gasket, screws, drain fitting/plug, upper/lower body or installed fluid function included.','material':{'name':'Proposed clean float-bowl cast alloy','base_color_linear':[.31,.33,.35,1],'metallic':.65,'roughness':.43},'package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
ob=shell('FLOAT_BOWL_ASYMMETRIC_CUP_JOINT_LEDGE_AND_VISIBLE_SEATS',rings)
for i,y in enumerate([-.028,.027]):
 boolean(ob,cyl((.0372,y,-.018),(.0447,y,-.018),.0055),'UNION','Visible bowl attachment ear '+str(i))
 boolean(ob,cyl((.032,y,-.018),(.0453,y,-.018),.002),'DIFFERENCE','Visible bowl attachment bore '+str(i))
boolean(ob,cyl((.055,-.034,-.017),(.055,-.013,-.017),.006),'UNION','Lower connector casting seat')
boolean(ob,cyl((.055,-.050,-.017),(.055,.002,-.017),.003),'DIFFERENCE','Lower connector visible mouth')
clean(ob);ob['scope']=P['scope'];finish_source(H,O,P)
