"""Original photo-bounded side-stand flattened foot edge; contact face is estimated."""
import bpy,bmesh,math,sys,json
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
R=Path(__file__).resolve().parents[1];name='side-stand-foot-edge-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name
H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
origin=Vector((.245,0));d=Vector((.048,.065)).normalized();n=Vector((-d.y,d.x));depth=.022
profile=[(-.008,0),(-.006,.0025),(.004,.00275),(.030,.0027),(.065,.0029),(.081,.0032),(.085,.0018),(.084,-.0022),(.078,-.0031),(.031,-.00275),(.005,-.00275),(-.006,-.0022)]
outline=[origin+d*t+n*w for t,w in profile]
P=dict(schema=1,package='P17',component_id='MOTO-SIDE-STAND-FOOT-EDGE-001',source='creative/research/powertrain-completion-p17-v1/side-foot-plan-v9.json',outline_t_normal_m=profile,working_root_xy_m=list(origin),working_axis_xy=list(d),depth_m=depth,depth_range_m=[.014,.036],typical_edge_width_m=.0055,edge_rounding_m=.0005,all_dimensions_estimated=True,scope='Separate elongated flattened terminal foot edge, supplying fourth side between retained stem and open deployment rod. Visible narrow contour bounded from JA113202 photo; broad contact face/depth, underside and camber unknown and represented only as estimated finite envelope. No invented measured stamping section, actual welds, ground contact or installed deployment qualification. Frozen center-stand terminal plates already exist and are not duplicated.',material=dict(name='Proposed clean black side foot coating',base_color_linear=[.012,.014,.017,1],metallic=.15,roughness=.34),package_complete=False,art_accepted=False)
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);V=[(p.x,p.y,z)for z in [-depth/2,depth/2]for p in outline];N=len(outline);F=[tuple(reversed(range(N))),tuple(N+i for i in range(N))]
for i in range(N):j=(i+1)%N;F.append((i,j,N+j,N+i))
ob=mesh_object('SIDE_STAND_ELONGATED_FLATTENED_FOOT_EDGE_ENVELOPE',V,F);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();bpy.context.view_layer.objects.active=ob
m=ob.modifiers.new('Small bounded exterior edge softening','BEVEL');m.width=.0005;m.segments=4;m.limit_method='ANGLE';m.angle_limit=math.radians(12);bpy.ops.object.modifier_apply(modifier=m.name)
if hasattr(ob.data,'set_sharp_from_angle'):ob.data.set_sharp_from_angle(angle=math.radians(35))
ob['scope']=P['scope'];finish_source(H,O,P)
