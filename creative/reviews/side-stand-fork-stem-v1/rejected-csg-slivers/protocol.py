"""P17 attributed side-stand fork/stem; shaped pierced ears, actual gap, no generic complete-stand claim."""
import bpy,sys,json,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
R=Path(__file__).resolve().parents[1];H=R/'assets-src/moto-components/side-stand-fork-stem-v1';O=R/'creative/reviews/side-stand-fork-stem-v1';H.mkdir(parents=True,exist_ok=True)
P={'schema':1,'package':'P17','component_id':'MOTO-SIDE-STAND-FORK-STEM-001','source':'creative/research/powertrain-completion-p17-v1/plan.json','stem_length_m':.245,'stem_length_range_m':[.22,.29],'stem_OD_m':.021,'stem_OD_range_m':[.018,.026],'fork_gap_m':.008,'fork_gap_range_m':[.005,.013],'ear_thickness_m':.005,'ear_thickness_range_m':[.0035,.007],'ear_outer_radius_m':.012,'ear_bore_radius_m':.0045,'ear_bore_diameter_range_m':[.007,.011],'fork_eye_center_x_m':-.024,'ear_root_x_m':.014,'edge_radius_m':.0005,'all_dimensions_estimated':True,'scope':'Forked stem only, ending at deferred foot interface. Closed stem model is exterior solid-envelope representation, not a measured rod/tube interior. Actual fork gap/bores, no hidden stops or frame mount claimed.','material':{'name':'Proposed black stand coating','base_color_linear':[.012,.014,.017,1],'metallic':.15,'roughness':.32},'package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True);V=[];F=[];N=128;M=160
for k in range(M+1):
 x=.245*k/M;r=.0105-.0005*(k/M)
 for j in range(N):a=j*math.tau/N;V.append((x,r*math.cos(a),r*math.sin(a)))
for k in range(M):
 a=k*N;b=a+N
 for i in range(N):j=(i+1)%N;F.append((a+i,a+j,b+j,b+i))
F.append(tuple(reversed(range(N))));F.append(tuple(M*N+i for i in range(N)));stem=mesh_object('SIDE_STAND_SHAPED_FORK_AND_STEM',V,F)
def ear(zc):
 verts=[];faces=[];profiles=[]
 for dz,offset in [(-.0025,.0005),(-.0020,0),(.0020,0),(.0025,.0005)]:
  r=.012-offset;xmax=.014-offset;p=[(xmax,-r),(xmax,r)]+[(-.024+r*math.cos(math.pi/2+math.pi*i/64),r*math.sin(math.pi/2+math.pi*i/64))for i in range(65)];profiles.append(p)
  for x,y in p:verts.append((x,y,zc+dz))
 n=len(profiles[0])
 for k in range(3):
  a=k*n;b=a+n
  for i in range(n):j=(i+1)%n;faces.append((a+i,a+j,b+j,b+i))
 faces.append(tuple(reversed(range(n))));faces.append(tuple(3*n+i for i in range(n)));return mesh_object('Fork ear construction',verts,faces)
for zc in [-.0065,.0065]:
 e=ear(zc);bpy.context.view_layer.objects.active=stem;mod=stem.modifiers.new('Continuous pierced fork root union','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=e;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(e,do_unlink=True)
bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=.0045,depth=.06,location=(-.024,0,0));cut=bpy.context.object;bpy.context.view_layer.objects.active=stem;mod=stem.modifiers.new('Two real fork-eye bores','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
if hasattr(stem.data,'set_sharp_from_angle'):stem.data.set_sharp_from_angle(angle=math.radians(40))
stem['scope']=P['scope'];finish_source(H,O,P)
