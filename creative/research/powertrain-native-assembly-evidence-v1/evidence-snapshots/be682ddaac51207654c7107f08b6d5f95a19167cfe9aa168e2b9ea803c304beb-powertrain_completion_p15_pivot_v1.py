"""P15 observed transverse pivot tube, independent open bore and bounded mouth chamfers."""
import bpy,sys,json,math,bmesh
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source,bounds,sha,write
R=Path(__file__).resolve().parents[1];name='brake-pedal-pivot-sleeve-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True)
P={'schema':1,'package':'P15','component_id':'MOTO-BRAKE-PEDAL-PIVOT-SLEEVE-001','source':'creative/research/powertrain-completion-p15-v1/pivot-child-plan-v2.json','outer_diameter_m':.021,'outer_diameter_range_m':[.017,.026],'plain_bore_diameter_m':.014,'bore_range_m':[.011,.018],'length_m':.032,'length_range_m':[.024,.041],'mouth_chamfer_m':.0005,'chamfer_range_m':[.0002,.001],'angular_samples':192,'all_dimensions_estimated':True,'scope':'Observed transverse tubular pivot form, real open bore and estimated end chamfers. No hidden bushing, lubrication groove, shaft, weld detail or certified fit. Unplaced independent child; unchanged pedal arm separately frozen.','material':{'name':'Proposed coated pedal pivot','base_color_linear':[.013,.015,.018,1],'metallic':.15,'roughness':.30},'package_complete':False,'art_accepted':False}
profile=[(.0075,0),(.0100,0),(.0105,.0005),(.0105,.0315),(.0100,.032),(.0075,.032),(.0070,.0315),(.0070,.0005)];P['section_r_z_m']=profile;(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);N=192;V=[];F=[]
for r,z in profile:
 for i in range(N):a=i*math.tau/N;V.append((r*math.cos(a),r*math.sin(a),z))
for k in range(len(profile)):
 a=k*N;b=((k+1)%len(profile))*N
 for i in range(N):j=(i+1)%N;F.append((a+i,a+j,b+j,b+i))
ob=mesh_object('BRAKE_PEDAL_TRANSVERSE_PIVOT_OPEN_TUBE',V,F);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
for f in bm.faces:f.smooth=abs(f.normal.z)<.9
for e in bm.edges:e.smooth=not(e.is_manifold and e.calc_face_angle(0)>math.radians(35))
bm.to_mesh(ob.data);bm.free();ob.data.update();ob['scope']=P['scope'];finish_source(H,O,P)
c,size,lo,hi=bounds();bpy.context.scene.camera.data.ortho_scale=2.15*size;bpy.ops.wm.save_as_mainfile(filepath=str(H/'child-gray.blend'),compress=True);d=json.loads((O/'geometry-check.json').read_text());d['source_sha256']=sha(H/'child-gray.blend');write(O,'geometry-check.json',d)
