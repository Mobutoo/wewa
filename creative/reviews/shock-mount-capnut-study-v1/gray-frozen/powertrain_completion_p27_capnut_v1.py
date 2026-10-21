"""P27 domed mount capnut exterior, distinct from existing SNS; no hidden thread/pitch or installed fit claim."""
import bpy,sys,json,math,bmesh
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source,bounds,sha,write
R=Path(__file__).resolve().parents[1];H=R/'assets-src/moto-components/shock-mount-capnut-study-v1';O=R/'creative/reviews/shock-mount-capnut-study-v1';H.mkdir(parents=True,exist_ok=True)
P={'schema':1,'package':'P27','component_id':'MOTO-REAR-SNS-MOUNT-CAPNUT-STUDY-001','source':'creative/research/powertrain-completion-p27-v1/capnut-child-plan-v1.json','AF_m':.017,'AF_range_m':[.015,.019],'height_m':.0185,'height_range_m':[.014,.021],'dome_radius_m':.0085,'socket_radius_m':.0048,'socket_diameter_range_m':[.008,.012],'socket_depth_m':.009,'socket_depth_range_m':[.006,.012],'angular_samples':240,'dome_steps':40,'camera_size_ratio':2.15,'all_dimensions_estimated':True,'scope':'Related catalogue-form domed capnut exterior only, with real hex flats and plain blind socket. No hidden thread, pitch, certified M10/currentRDC fit or mount strength. Existing SNS candidates reused, not rebuilt; washers/bolts/anchors/installed suspension remain separate.','material':{'name':'Proposed clean bright mount nut','base_color_linear':[.42,.44,.46,1],'metallic':.85,'roughness':.28},'package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);N=240;V=[];F=[];rings=[]
def hexr(a,apothem):return apothem/math.cos((a+math.pi/6)%(math.pi/3)-math.pi/6)
for z,ap in [(0,.0080),(.0006,.0085),(.0085,.0085)]:rings.append([(hexr(i*math.tau/N,ap),z)for i in range(N)])
for k in range(1,13):
 t=k/12;sm=t*t*(3-2*t);z=.0085+.0015*t;rings.append([((1-sm)*hexr(i*math.tau/N,.0085)+sm*.0085,z)for i in range(N)])
for k in range(1,40):
 a=k*math.pi/2/40;rings.append([(.0085*math.cos(a),.010+.0085*math.sin(a))for i in range(N)])
for ring in rings:
 for i,(r,z)in enumerate(ring):a=i*math.tau/N;V.append((r*math.cos(a),r*math.sin(a),z))
for k in range(len(rings)-1):
 a=k*N;b=a+N
 for i in range(N):j=(i+1)%N;F.append((a+i,a+j,b+j,b+i))
pole=len(V);V.append((0,0,.0185));a=(len(rings)-1)*N
for i in range(N):F.append((a+i,a+(i+1)%N,pole))
inner=len(V)
for z,r in [(0,.0052),(.0005,.0048),(.009,.0048)]:
 for i in range(N):a=i*math.tau/N;V.append((r*math.cos(a),r*math.sin(a),z))
for k in range(2):
 a=inner+k*N;b=a+N
 for i in range(N):j=(i+1)%N;F.append((a+i,b+i,b+j,a+j))
F.append(tuple(reversed([inner+2*N+i for i in range(N)])))
for i in range(N):j=(i+1)%N;F.append((i,inner+i,inner+j,j))
ob=mesh_object('SNS_MOUNT_DOMED_HEX_CAPNUT_EXTERIOR_STUDY',V,F)
# Keep physical lower hex faces flat; dome and small shoulder blend smooth. No buffer-normal repair.
for f in ob.data.polygons:
 zs=[ob.data.vertices[i].co.z for i in f.vertices]
 if max(zs)<=.00851 or len(f.vertices)>4:f.use_smooth=False
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
for e in bm.edges:e.smooth=not(e.is_manifold and e.calc_face_angle(0)>math.radians(35))
bm.to_mesh(ob.data);bm.free();ob.data.update();ob['scope']=P['scope'];finish_source(H,O,P)
c,size,lo,hi=bounds();bpy.context.scene.camera.data.ortho_scale=2.15*size;bpy.ops.wm.save_as_mainfile(filepath=str(H/'child-gray.blend'),compress=True);report=json.loads((O/'geometry-check.json').read_text());report['source_sha256']=sha(H/'child-gray.blend');report['camera_ortho_scale_m']=2.15*size;write(O,'geometry-check.json',report)
