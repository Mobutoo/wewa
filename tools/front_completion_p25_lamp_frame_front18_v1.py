"""PF121024 observed two-sleeve/crossbar carrier; no PF121025 or legacy triangular-stay merge."""
import bpy,math,runpy,json
from pathlib import Path
R=Path('/workspace/wewa');K='front-completion-p25-lamp-frame-front18-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K
H.mkdir(exist_ok=False);O.mkdir(exist_ok=False);bpy.ops.wm.read_factory_settings(use_empty=True);u=runpy.run_path(str(R/'tools/front_completion_front10_mesh_helpers_v1.py'));objects=[];audits=[];N=192
def finish(ob,nb):
 u['orient'](ob);a=u['clean_audit'](ob,expected_boundary=nb);objects.append(ob);audits.append(a);return ob
def rev(name,profile,center,axis='Z'):
 v=[];f=[]
 for r,t in profile:
  for j in range(N):
   a=2*math.pi*j/N;q=(r*math.cos(a),r*math.sin(a),t) if axis=='Z' else (r*math.cos(a),t,r*math.sin(a))
   v.append(tuple(q[k]+center[k] for k in range(3)))
 for i in range(len(profile)-1):
  for j in range(N):a=i*N+j;b=i*N+(j+1)%N;f.append((a,b,b+N,a+N))
 return finish(u['mesh_object'](name,v,f),2*N)
# Independent source-observed sleeves. Short visible mouth returns only, no hidden full internal wall.
left=[(.0190,-.078),(.0190,-.0840),(.0193,-.0850),(.0201,-.0850),(.0205,-.0845),(.0205,.0835),(.0202,.0840),(.0192,.0840),(.0189,.0835),(.0189,.0775)]
right=[(.0191,-.079),(.0191,-.0850),(.0195,-.0855),(.0203,-.0855),(.0206,-.0850),(.0206,.0850),(.0202,.0855),(.0193,.0855),(.0190,.0850),(.0190,.0790)]
rev('PF121024_LEFT_OBSERVED_SLEEVE_OUTSIDE_AND_MOUTH_RETURNS',left,(-.0875,0,0))
rev('PF121024_RIGHT_OBSERVED_SLEEVE_OUTSIDE_AND_MOUTH_RETURNS',right,(.0875,0,0))
# Single visible transverse member outside skin. Source welding joins are not invented as weld beads.
v=[];f=[]
for x in [-.069,.069]:
 for j in range(N):a=2*math.pi*j/N;v.append((x,.0060*math.cos(a),-.012+.0060*math.sin(a)))
for j in range(N):a=j;b=(j+1)%N;f.append((a,b,b+N,a+N))
finish(u['mesh_object']('PF121024_SINGLE_TRANSVERSE_MEMBER_EXTERIOR_OPEN_JOIN_CUTS',v,f),2*N)
# Visible right-side mounting eyes: front ring/short visible bore only; two separately specified contours.
rev('PF121024_RIGHT_UPPER_EYE_VISIBLE_RING_NO_HIDDEN_ROOT',[(.0042,-.014),(.0042,-.018),(.0045,-.019),(.0076,-.019),(.0080,-.0185),(.0080,-.014)],(.063,0,.052),'Y')
rev('PF121024_RIGHT_LOWER_EYE_VISIBLE_RING_NO_HIDDEN_ROOT',[(.0045,-.014),(.0045,-.0185),(.0048,-.0195),(.0080,-.0195),(.0084,-.0190),(.0084,-.014)],(.0625,0,-.051),'Y')
# Separate visible upper lug silhouettes: single exposed sheet faces; unknown reverse section excluded.
for name,vv in [('PF121024_LEFT_UPPER_LUG_VISIBLE_FACE',[(-.099,-.004,.071),(-.094,-.004,.111),(-.088,-.004,.109),(-.081,-.004,.079)]),('PF121024_RIGHT_UPPER_LUG_VISIBLE_FACE',[(.075,-.004,.072),(.079,-.004,.119),(.086,-.004,.116),(.096,-.004,.080)])]:
 finish(u['mesh_object'](name,vv,[(0,1,2,3)]),4)
params={'package':'P25','code':'PF121024','source':'Winter physical complete two-sleeve/crossbar photograph actually read; D04PDF51 and BM150rev01MAR16PDF49 component identity corroboration','variant_separation':'PF121025 welded fairing structure and PF121015/16 triangular individual stays are separate components/variants, never merged here','scope':'Observed carrier main exterior: two independently authored open sleeves and exposed mouth returns, one transverse member, visible right mounting-ring surfaces, independent upper lug front silhouettes. Not a complete mounting/installed assembly.','all_working_dimensions_estimated':True,'working_m':{'sleeve_center_spacing':.175,'sleeve_outside_radii':[.0205,.0206],'sleeve_lengths':[.169,.171],'crossbar_radius':.0060,'crossbar_axis_z':-.012},'bounds_m':{'sleeve_center_spacing':[.145,.200],'sleeve_outer_radius':[.018,.025],'sleeve_length':[.14,.20],'mouth_gauge':[.0007,.002],'crossbar_radius':[.004,.008]},'hidden_omitted':['Continuous inner sleeve walls beyond short visible mouth returns','Hidden weld cross-sections and bar ends','Left occluded mounting eyes/root geometry; no blind mirroring of right rings','Hidden backs/thickness of upper lug faces, exact hole/thread/slot geometry','Bushes, grommets, fasteners, chrome fork, bellows and PF121025 structure'],'interfaces':'Open finite review cuts at occluded joins, source-relative layout only. No functional weld, bore fit or exact current RDC certification.','material':'Uniform black coating hypothesis without grain, weld bumps or measured finish','art_accepted':False,'mounted_fit':False}
(H/'parameters.json').write_text(json.dumps(params,indent=2));(O/'geometry-check.json').write_text(json.dumps({'objects':audits,'independent_meshes':len(objects),'source_supported_visible_surfaces_only':True,'weld_and_contact_receipt':False},indent=2));(O/'child-plan.json').write_text(json.dumps({'package':'P25','component_id':'MOTO-LAMP-FRAME-PF121024-VISIBLE-CARRIER-STUDY-001','child':'PF121024 observed two-sleeve headlamp carrier exterior','scope':params['scope']+' Hidden roots and inner sections omitted explicitly; dimensions and exact current RDC applicability estimated, not certified.','protocols':['front_completion_p25_lamp_frame_front18_v1.py','front_completion_front10_mesh_helpers_v1.py','front_completion_front14_render_v1.py','front_completion_front10_material_v1.py'],'remaining':params['hidden_omitted']+['Exact current motorcycle fit and assembly registration']},indent=2));u['gray_save'](H,'lamp-frame',objects)
