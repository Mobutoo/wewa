"""Original constant-round actuation shank; perspective narrowing is not a measured taper."""
import bpy,bmesh,sys,math,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
R=Path(__file__).resolve().parents[1];name='brake-actuation-rod-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
L=.490;r=.00275;q=.00015;N=128;profile=[]
for j in range(13):a=j*math.pi/24;profile.append((q*(1-math.cos(a)),r-q+q*math.sin(a)))
profile.append((L-q,r))
for j in range(1,13):a=j*math.pi/24;profile.append((L-q+q*math.sin(a),r-q+q*math.cos(a)))
P={'schema':1,'package':'P15','component_id':'MOTO-BRAKE-ACTUATION-ROD-001','source':'creative/research/powertrain-completion-p15-v1/actuation-rod-plan-v5.json','length_m':L,'length_range_m':[.43,.57],'diameter_m':2*r,'diameter_range_m':[.004,.007],'edge_radius_m':q,'section_x_r_m':profile,'all_dimensions_estimated':True,'camera_calibrated':False,'scope':'Constant-round long external shank with softly ended plain terminal study only. Photo perspective narrowing not copied as taper. Thread pitch/end bend, actual clevis joint/attachment, spring/adjuster and installed clocking/travel unresolved. Separate clevis and existing pedal components excluded.','material':{'name':'Proposed clean bright rod metal','base_color_linear':[.42,.43,.45,1],'metallic':.8,'roughness':.27},'package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
V=[(x,rr*math.cos(i*math.tau/N),rr*math.sin(i*math.tau/N))for x,rr in profile for i in range(N)];F=[tuple(reversed(range(N))),tuple((len(profile)-1)*N+i for i in range(N))]
for k in range(len(profile)-1):
 for i in range(N):F.append((k*N+i,k*N+(i+1)%N,(k+1)*N+(i+1)%N,(k+1)*N+i))
ob=mesh_object('BRAKE_ACTUATION_ROUND_SHANK_PLAIN_TERMINAL_STUDY',V,F);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
for f in bm.faces:f.smooth=abs(f.normal.x)<.999
for e in bm.edges:e.smooth=not(e.is_manifold and e.calc_face_angle(0)>math.radians(35))
bm.to_mesh(ob.data);bm.free();ob.data.update();ob['scope']=P['scope'];finish_source(H,O,P)
