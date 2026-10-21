"""Photo-informed separate toe rubber, continuous annular ribs, estimated plain blind seat."""
import bpy,sys,json,math,bmesh
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source,bounds,sha,write
R=Path(__file__).resolve().parents[1];name='gear-selector-toe-rubber-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True)
P={'schema':1,'package':'P14','component_id':'MOTO-GEAR-SELECTOR-TOE-RUBBER-001','source':'creative/research/powertrain-completion-p14-v1/toe-rubber-child-plan-v2.json','length_m':.040,'length_range_m':[.032,.050],'base_diameter_m':.021,'diameter_range_m':[.018,.028],'rib_count':11,'rib_count_range':[9,13],'rib_height_m':.001,'rib_height_range_m':[.0006,.0018],'plain_seat_diameter_m':.011,'seat_diameter_range_m':[.008,.014],'seat_depth_m':.036,'seat_depth_range_m':[.028,.038],'angular_samples':128,'rib_axial_samples':18,'all_dimensions_estimated':True,'scope':'Photo-observed cylindrical ribbed toe rubber only, rolled mouth and broad soft closed end. Plain blind seat is explicit working estimate; actual inner retention/end construction and terminal fit undocumented.','material':{'name':'Proposed clean dark rubber','base_color_linear':[.018,.020,.022,1],'metallic':0,'roughness':.62},'package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
profile=[(.0060,0),(.0100,0),(.0107,.0006),(.0107,.0012),(.0105,.002)]
for k in range(1,11*18+1):
 t=k/(11*18);z=.002+.034*t;phase=(t*11)%1;r=.0105+.001*math.sin(math.pi*phase)**4;profile.append((r,z))
# Broad end: half ellipse fillet from side to flat central end, not a pointed nipple.
for k in range(1,25):
 a=math.pi/2*k/24;profile.append((.0085+.002*math.cos(a),.036+.004*math.sin(a)))
profile.extend([(.0055,.040),(.002,.040)])
V=[];F=[];N=128
for r,z in profile:
 for i in range(N):a=math.tau*i/N;V.append((r*math.cos(a),r*math.sin(a),z))
for k in range(len(profile)-1):
 a=k*N;b=a+N
 for i in range(N):j=(i+1)%N;F.append((a+i,a+j,b+j,b+i))
pole=len(V);V.append((0,0,.040));a=(len(profile)-1)*N
for i in range(N):F.append((a+i,a+(i+1)%N,pole))
inner=len(V)
for z,r in [(.0005,.0055),(.0355,.0055),(.036,.0050)]:
 for i in range(N):a=math.tau*i/N;V.append((r*math.cos(a),r*math.sin(a),z))
for i in range(N):j=(i+1)%N;F.append((i,inner+i,inner+j,j))
for k in range(2):
 a=inner+k*N;b=a+N
 for i in range(N):j=(i+1)%N;F.append((a+i,b+i,b+j,a+j))
pole=len(V);V.append((0,0,.036));a=inner+2*N
for i in range(N):F.append((a+i,pole,a+(i+1)%N))
ob=mesh_object('SELECTOR_TOE_RUBBER_CONTINUOUS_ELEVEN_RIBS',V,F);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
for e in bm.edges:e.smooth=not(e.is_manifold and e.calc_face_angle(0)>math.radians(40))
bm.to_mesh(ob.data);bm.free();ob.data.update();ob['scope']=P['scope'];finish_source(H,O,P)
c,size,lo,hi=bounds();bpy.context.scene.camera.data.ortho_scale=2.15*size;bpy.ops.wm.save_as_mainfile(filepath=str(H/'child-gray.blend'),compress=True);d=json.loads((O/'geometry-check.json').read_text());d['source_sha256']=sha(H/'child-gray.blend');write(O,'geometry-check.json',d)
