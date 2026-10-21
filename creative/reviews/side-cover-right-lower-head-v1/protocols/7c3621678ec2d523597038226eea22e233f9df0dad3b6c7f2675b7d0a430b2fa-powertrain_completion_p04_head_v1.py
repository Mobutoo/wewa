"""P04 independent lower visible head, bounded official00 scale; no invented drive or hidden retainer."""
import bpy,sys,json,math,bmesh
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source,bounds,sha,write
R=Path(__file__).resolve().parents[1];name='side-cover-right-lower-head-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True)
r=3*1.285/527
P={'schema':1,'package':'P04','component_id':'MOTO-SIDE-COVER-RIGHT-LOWER-HEAD-001','source':'creative/research/powertrain-completion-p04-v1/lower-head-plan-v2.json','reference_landmark_px':[455,399],'landmark_uncertainty_px':2,'selected_diameter_pixels':6,'pixel_range':[4,8],'meters_per_pixel':1.285/527,'diameter_m':2*r,'diameter_range_m':[.008,.024],'height_m':.003,'height_range_m':[.0015,.005],'rim_height_m':.0005,'rim_height_range_m':[.0002,.001],'angular_samples':192,'dome_steps':40,'all_dimensions_estimated':True,'scope':'Independently documented small lower circular right-cover feature. Shallow dome and rolled perimeter are explicit bounded interpretations; face drive unreadable, no slot, shaft, rear retainer or installed fit fabricated. Original skin v1 unchanged.','material':{'name':'Proposed satin round cover head','base_color_linear':[.18,.20,.22,1],'metallic':.65,'roughness':.38},'package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);N=192;V=[];F=[];profile=[(r-.0002,0),(r,.0002),(r,.0005)]
for k in range(1,40):
 a=math.pi/2*k/40;profile.append((r*math.cos(a),.0005+.0025*math.sin(a)))
for rr,z in profile:
 for i in range(N):a=i*math.tau/N;V.append((rr*math.cos(a),rr*math.sin(a),z))
for k in range(len(profile)-1):
 a=k*N;b=a+N
 for i in range(N):j=(i+1)%N;F.append((a+i,a+j,b+j,b+i))
pole=len(V);V.append((0,0,.003));a=(len(profile)-1)*N
for i in range(N):F.append((a+i,a+(i+1)%N,pole))
pole=len(V);V.append((0,0,0))
for i in range(N):F.append((i,pole,(i+1)%N))
ob=mesh_object('RIGHT_COVER_LOWER_ROUND_VISIBLE_HEAD_NO_DRIVE_CLAIM',V,F);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
for f in bm.faces:
 if max(v.co.z for v in f.verts)<1e-8:f.smooth=False
for e in bm.edges:e.smooth=not(e.is_manifold and e.calc_face_angle(0)>math.radians(40))
bm.to_mesh(ob.data);bm.free();ob.data.update();ob['scope']=P['scope'];finish_source(H,O,P)
c,size,lo,hi=bounds();bpy.context.scene.camera.data.ortho_scale=2.15*size;bpy.ops.wm.save_as_mainfile(filepath=str(H/'child-gray.blend'),compress=True);d=json.loads((O/'geometry-check.json').read_text());d['source_sha256']=sha(H/'child-gray.blend');write(O,'geometry-check.json',d)
