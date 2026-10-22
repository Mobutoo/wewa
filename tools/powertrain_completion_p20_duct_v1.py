"""P20 bounded catalogue-form duct study, not inferred installed hose routing or an exact part identity."""
import bpy,sys,json,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source,bounds,sha,write
R=Path(__file__).resolve().parents[1];H=R/'assets-src/moto-components/intake-duct-study-v1';O=R/'creative/reviews/intake-duct-study-v1';H.mkdir(parents=True,exist_ok=True)
P={'schema':1,'package':'P20','component_id':'MOTO-INTAKE-AIR-DUCT-STUDY-001','source':'creative/research/powertrain-completion-p20-v1/duct-child-plan-v1.json','length_m':.055,'length_range_m':[.040,.075],'peak_OD_range_m':[.040,.060],'wall_radial_m':.003,'wall_range_m':[.0018,.004],'bore_range_m':[.028,.046],'bore_range_note':'Expanded working bound includes rolled flange mouth; body and fold bore vary, not certified fit','fold_centres_m':[.016,.031],'fold_count_status':'Illustration-inferred2 broad folds, uncertain1–3; no physical opposite section acquired','fold_height_m':.0033,'fold_half_width_m':.006,'body_base_radius_m':.0205,'large_flange_height_m':.0045,'camera_size_ratio':2.15,'axial_samples':220,'angular_samples':192,'all_dimensions_estimated':True,'scope':'Short annular flanged/two-fold connector study only. Conditional D04 callout2 form; no exact JB/PF identity, no photographed surface claim, no installed axes/fit or generic unobserved hose path. Clamp and exhaust mounts separate.','material':{'name':'Proposed clean dark duct rubber','base_color_linear':[.012,.014,.017,1],'metallic':0,'roughness':.60},'package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
def sm(t):t=max(0,min(1,t));return t*t*(3-2*t)
def bump(x,c,w):return (.5+.5*math.cos(math.pi*(x-c)/w))**2 if abs(x-c)<w else 0
def outer(x):return .0205+.001*sm(x/.010)+.0045*bump(x,.002,.004)+sum(.0033*bump(x,c,.006)for c in [.016,.031])+.0012*sm((x-.042)/.006)+.0013*bump(x,.052,.003)
T=.003;L=.055;start=T/2;end=L-T/2;M=220;profile=[]
for k in range(M+1):x=start+(end-start)*k/M;profile.append((x,outer(x)))
rf=outer(end)-T/2
for j in range(1,17):a=j*math.pi/16;profile.append((end+T/2*math.sin(a),rf+T/2*math.cos(a)))
for k in range(1,M+1):x=end-(end-start)*k/M;profile.append((x,outer(x)-T))
rn=outer(start)-T/2
for j in range(1,16):a=math.pi-j*math.pi/16;profile.append((start-T/2*math.sin(a),rn+T/2*math.cos(a)))
V=[];F=[];N=192
for x,r in profile:
 assert r>.012
 for j in range(N):a=j*math.tau/N;V.append((x,r*math.cos(a),r*math.sin(a)))
for k in range(len(profile)):
 a=k*N;b=((k+1)%len(profile))*N
 for i in range(N):j=(i+1)%N;F.append((a+i,a+j,b+j,b+i))
ob=mesh_object('CATALOGUE_FORM_FLANGED_TWO_FOLD_DUCT_STUDY',V,F);ob['scope']=P['scope'];finish_source(H,O,P)

# Whole-piece camera correction; no geometry, clipping threshold or export-buffer change.
c,size,lo,hi=bounds();bpy.context.scene.camera.data.ortho_scale=2.15*size;bpy.ops.wm.save_as_mainfile(filepath=str(H/'child-gray.blend'),compress=True);report=json.loads((O/'geometry-check.json').read_text());report['source_sha256']=sha(H/'child-gray.blend');report['camera_ortho_scale_m']=2.15*size;write(O,'geometry-check.json',report)
