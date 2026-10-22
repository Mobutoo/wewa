import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
R=Path('/workspace/wewa');O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
QL=Matrix(((0,0,1),(-2**-.5,-2**-.5,0),(2**-.5,-2**-.5,0)))
QR=QL@Matrix(((-1,0,0),(0,1,0),(0,0,-1)))
def pose(q,anchor,target):m=q.to_4x4();m.translation=Vector(target)-q@Vector(anchor);return m
L=pose(QL,(-.006,.239,.0195),(.1,.65,-.555));RH=pose(QR,(.004,.239,.0195),(-.1,.65,-.555))
P=Matrix(((0,1,0,0),(0,0,1,0),(1,0,0,0),(0,0,0,1)))
def local(x,z):m=P.copy();m.translation=(x,.239,z);return m
srcs=[('passenger-LH-kit','passenger-footrest-left-exterior-context-v1/passenger-footrest-left-exterior-context-v1.blend','PASSENGER_FOOTREST_LEFT_EXTERIOR_CONTEXT_V1',None,L),('passenger-RH-stay','passenger-footrest-stay-right-v1/child-candidate.blend',None,'PF113003_RIGHT_PASSENGER_STAY_FORMED_ARMS_EYE_GUSSET_U_CLEVIS',RH),('passenger-RH-peg-DP161170','passenger-footpeg-metal-v1/child-candidate.blend',None,'PASSENGER_PEG_SHAPED_ROOT_FLANGE_AND_STOP_TAB',RH@local(.004,.0075)),('passenger-RH-rubber-JK113008','passenger-footrest-rubber-jk113008-v1/child-candidate.blend',None,'JK113008_PASSENGER_RUBBER_VISIBLE_ENVELOPE_ONLY',RH@local(.004,.0335))]
rows=[]
for key,file,col,obj,m in srcs:
 p=R/'assets-src/moto-components'/file;rows.append(dict(key=key,source=str(p.relative_to(R)),sha256=sha(p),collection=col,selected_objects=[obj]if obj else None,matrix_world=[list(v)for v in m],nested='three unchanged stay/peg/rubber wrappers in original LH collection'if col else[],source_class='documented_related_variant / estimated',provisional_visual_pose=True))
fragment={'id':O.name,'status':'revised-anchor rigid candidate; 3D and visual audit pending','convention':'native metres Xpilot-left Yrear Zup; row-major4x4 acts on column vector; glTF C=(X,Z,-Y), MglTF=C M C^-1','parents_to_remove':[],'additions':rows,'hinges_world_m':{'LH':[.1,.65,-.555],'RH':[-.1,.65,-.555]},'count':{'mesh_instances':6,'independent_stays':2,'documented_common_peg_quantity':2,'documented_common_rubber_quantity':2,'new_physical_meshes':0},'preserved_historical_limits':['5mm peg-vs-clevis axis offset; no pin','22mm nominal distal rubber overhang','90degree diagnostic rubber cut, not physical keyway'],'bounds':{'hinge_xyz_m':[.025,.06,.04],'stay_angle_deg':15,'note':'visual search allowance only, not OEM tolerance; RHS station inferred conditionally from opposite installed views'},'no_reflection':True,'no_hidden_pins_or_welds':True,'fit_qualified':False,'art_accepted':False}
(O/'integration-fragment.json').write_text(json.dumps(fragment,indent=2)+'\n')
plan={'sources':[],'hypothesis':fragment,'observations':['Official04 folded/upward rubber segment, not a calibrated hinge datum','Independent donor PF113002/PF113003 shape/dimensions are not exact RDC certification','Donor long/short terminals must be compared to actual frame; proximity cannot establish fixing role'],'next':'Evaluate actual native geometry against linked frame kitv2 and native SNS, then rigid folded-peg hypothesis with source limits unchanged'}
for n in ['03','04','05','07']:
 p=Path('/workspace/wewa-assets/references/exterior-completion-current')/(n+'.png');plan['sources'].append({'url':'https://www.bajajauto.com/fr-cd/-/media/globalbajajauto/common-media/360/boxer/boxer-125-hd-new/red-long-visor/'+n+'.png','sha256':sha(p),'source_class':'documented_exact_market_photo; dimensions estimated','actually_viewed':True,'observation':'Partly occluded passenger brace and folded rubber; no exact mounting stations identified'})
(O/'G0-G2-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
print('FRAGMENT_READY',json.dumps(rows))
