"""Source-observed JZ561415 clamp ear extensions and visible hex head/seat only."""
import bpy,sys,json,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
from powertrain_continuation_loft_v4 import recalc,clean_smooth
R=Path(__file__).resolve().parents[1];name='gear-selector-clamp-ears-visible-head-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True);planpath='creative/research/powertrain-completion-p14-v1/clamp-ears-visible-head-plan-v112.json';plan=json.loads((R/planpath).read_text());bpy.ops.wm.read_factory_settings(use_empty=True)
black=dict(name='Proposed dark coated clamp ears',base_color_linear=[.018,.021,.024,1],metallic=.35,roughness=.36);gold=dict(name='Proposed yellow metallic visible head and round seat',base_color_linear=[.48,.32,.10,1],metallic=.85,roughness=.30)
P=dict(schema=1,package='P14',component_id=plan['component_id'],source=planpath,source_identity=plan['identity'],scope=plan['scope'],all_dimensions_estimated=True,camera_calibrated=False,estimates=plan['estimates'],material=black,material_regions={},package_complete=False,art_accepted=False)
for label,xmin,xmax in [('EAR_NEGATIVE_X',-.008,-.001),('EAR_POSITIVE_X',.001,.008)]:
 # Contour in XY; lower/root edge follows existing outer hub cylinder only, no second hub.
 C=[(xmin,.022),(xmax,.022)]+[(xmax+(xmin-xmax)*i/32,math.sqrt(.0135**2-(xmax+(xmin-xmax)*i/32)**2)-.00025) for i in range(33)]
 V=[(x,y,z)for z in [.0015,.022]for x,y in C];N=len(C);F=[tuple(reversed(range(N))),tuple(N+i for i in range(N))]
 for i in range(N):j=(i+1)%N;F.append((i,j,N+j,N+i))
 ob=mesh_object(label,V,F);recalc(ob);bpy.context.view_layer.objects.active=ob;m=ob.modifiers.new('Observed softened rectangular ear edges - estimated radius','BEVEL');m.width=.00045;m.segments=5;m.affect='EDGES';bpy.ops.object.modifier_apply(modifier=m.name);clean_smooth(ob);ob['scope']='External ear extension only; curved root is provisional contact to existing hub, hidden bolt bore omitted';P['material_regions'][ob.name]=black
# Integral visible-surface representation: flange vs separate washer not resolved.
# No shank, thread, reverse nut, cavity or hidden drive geometry.
N=96;V=[];F=[]
rings=[(.0080,.00625,'circle'),(.0082,.0065,'circle'),(.0088,.0065,'circle'),(.0090,.00625,'circle'),(.0090,.00485,'hex'),(.00925,.005,'hex'),(.0128,.005,'hex'),(.0132,.0046,'hex')]
for x,r,kind in rings:
 for i in range(N):
  a=math.tau*i/N
  rad=r if kind=='circle' else r/math.cos((a+math.pi/6)%(math.pi/3)-math.pi/6)
  V.append((x,.018+rad*math.cos(a),.0115+rad*math.sin(a)))
for k in range(len(rings)-1):
 for i in range(N):j=(i+1)%N;F.append((k*N+i,k*N+j,(k+1)*N+j,(k+1)*N+i))
for k,x,reverse in [(0,rings[0][0],True),(len(rings)-1,rings[-1][0],False)]:
 pole=len(V);V.append((x,.018,.0115))
 for i in range(N):
  j=(i+1)%N;F.append((pole,k*N+j,k*N+i)if reverse else(pole,k*N+i,k*N+j))
ob=mesh_object('VISIBLE_HEX_HEAD_AND_ROUND_SEAT_ONLY',V,F);recalc(ob);clean_smooth(ob);ob['scope']='Only visible hex crown/circular seat; flange-versus-washer identity unresolved, no hidden shaft or thread';P['material_regions'][ob.name]=gold
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');finish_source(H,O,P)
(O/'construction-check.json').write_text(json.dumps(dict(method='Original finite source-shaped ear extensions with softened edges and curved provisional hub contact; visible hex/circle head surface rings, no hidden shank',existing_hub_or_arm_rebuilt=False,ear_count=2,hidden_bolt_shaft_thread_or_nut=False,hidden_ear_bores=False,round_seat_identity='Integral flange versus separate washer unresolved; one visible representation only',source_identity=plan['identity'],all_dimensions_estimated=True,art_accepted=False),indent=2)+'\n')
