"""Original formed two-ear clevis with rounded U return, real gap and separate bores."""
import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
from powertrain_continuation_shapes_v2 import cyl,boolean,clean,recalc
R=Path(__file__).resolve().parents[1];name='brake-rod-clevis-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
P={'schema':1,'package':'P15','component_id':'MOTO-BRAKE-ROD-CLEVIS-001','source':'creative/research/powertrain-completion-p15-v1/rod-clevis-plan-v6.json','ear_thickness_m':.0025,'clear_gap_m':.007,'eye_bore_diameter_m':.006,'rod_entry_diameter_m':.0058,'outer_fold_radius_m':.006,'inner_fold_radius_m':.0035,'all_dimensions_estimated':True,'camera_calibrated':False,'scope':'Separate stamped U clevis with rounded widening ears, real inter-ear gap, two coaxial eye openings and basic root entry. Inner fold/rod joining method and actual offsets are estimates. Pin/retainer, weld/threads, existing rod and installed stack/travel excluded.','material':{'name':'Proposed clean plated clevis metal','base_color_linear':[.40,.39,.32,1],'metallic':.8,'roughness':.31},'package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
def prism(name,poly,z0,z1,axis='Z'):
 n=len(poly);V=[(x,y,z)if axis=='Z'else(x,z,y)for z in [z0,z1]for x,y in poly];F=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)];ob=mesh_object(name,V,F);recalc(ob);return ob
outline=[(-.0038,-.007),(.002,-.007),(.012,-.009)]
for i in range(65):a=-math.pi/2+math.pi*i/64;outline.append((.020+.009*math.cos(a),.009*math.sin(a)))
outline += [(.012,.009),(.002,.007),(-.0038,.007)]
pts=[Vector(p)for p in outline];poly=[]
for i,b in enumerate(pts):
 a,c=pts[i-1],pts[(i+1)%len(pts)];q=min(.0004,(b-a).length*.22,(c-b).length*.22);u=b-(b-a).normalized()*q;v=b+(c-b).normalized()*q
 for j in range(5):t=j/5;poly.append(tuple((1-t)**2*u+2*(1-t)*t*b+t*t*v))
ob=prism('FOLDED_BRAKE_ROD_CLEVIS_PIERCED_EARS_AND_REAL_GAP',poly,.0035,.006)
boolean(ob,prism('Lower ear construction',poly,-.006,-.0035),'UNION','Two separate ears awaiting root union')
# A curved U section, not a block filling the inter-ear gap.
fold=[(-.0015,-.006),(-.0035,-.006)]
for i in range(1,65):a=-math.pi/2-math.pi*i/64;fold.append((-.0035+.006*math.cos(a),.006*math.sin(a)))
fold += [(-.0015,.006),(-.0015,.0035),(-.0035,.0035)]
for i in range(1,65):a=math.pi/2+math.pi*i/64;fold.append((-.0035+.0035*math.cos(a),.0035*math.sin(a)))
fold += [(-.0015,-.0035)]
boolean(ob,prism('Rounded U return construction',fold,-.007,.007,axis='Y'),'UNION','Continuous formed root return')
boolean(ob,cyl((.020,0,-.025),(.020,0,.025),.003),'DIFFERENCE','Coaxial actual ear eye bores')
boolean(ob,cyl((-.020,0,0),(.008,0,0),.0029),'DIFFERENCE','Basic open rod-entry web')
clean(ob);ob['scope']=P['scope'];finish_source(H,O,P)
