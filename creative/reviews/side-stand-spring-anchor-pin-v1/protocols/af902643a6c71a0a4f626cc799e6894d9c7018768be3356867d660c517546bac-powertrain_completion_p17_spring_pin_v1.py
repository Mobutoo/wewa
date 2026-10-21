"""Separate photo-visible side-stand spring anchor pin; not the pivot bolt."""
import bpy,math,sys,json,bmesh
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
R=Path(__file__).resolve().parents[1];name='side-stand-spring-anchor-pin-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name
H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
profile=[(.009,.0035),(.0093,.0035),(.0097,.0032),(.010,.003),(.0265,.003),(.0268,.0033),(.027,.0047),(.0273,.005),(.0297,.005),(.030,.0047)]
P=dict(schema=1,package='P17',component_id='MOTO-SIDE-STAND-SPRING-ANCHOR-PIN-001',source='creative/research/powertrain-completion-p17-v1/side-spring-pin-plan-v10.json',profile_y_radius_m=profile,stem_axis_x_m=.110,axis='+Y',angular_samples=144,all_dimensions_estimated=True,scope='Separate short photo-visible spring anchor pin with smaller neck and wider terminal head. Working location in retained stem axes is estimated only. Simple root envelope and head rounding not a measured weld/retaining section; no actual spring hook engagement, clocking/preload or installed fit. Not pivot bolt, no invented cross-hole.',material=dict(name='Proposed black coated spring anchor pin',base_color_linear=[.012,.014,.017,1],metallic=.15,roughness=.32),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);V=[];F=[];N=P['angular_samples']
for y,r in profile:
 for j in range(N):
  a=math.tau*j/N;V.append((.110+r*math.cos(a),y,r*math.sin(a)))
for k in range(len(profile)-1):
 for i in range(N):j=(i+1)%N;F.append((k*N+i,k*N+j,(k+1)*N+j,(k+1)*N+i))
F+=[tuple(reversed(range(N))),tuple((len(profile)-1)*N+j for j in range(N))]
ob=mesh_object('SIDE_STAND_TRANSVERSE_SPRING_ANCHOR_NECK_AND_WIDER_HEAD',V,F);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob['scope']=P['scope'];finish_source(H,O,P)
