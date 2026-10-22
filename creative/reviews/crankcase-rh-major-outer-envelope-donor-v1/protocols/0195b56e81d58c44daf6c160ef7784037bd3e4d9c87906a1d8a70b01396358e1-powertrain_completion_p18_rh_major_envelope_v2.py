"""Independent photographed BM150 RH peripheral casting study, never mirrored LH geometry."""
import bpy,sys,json,math,bmesh
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
from powertrain_continuation_loft_v4 import recalc,clean_smooth
R=Path(__file__).resolve().parents[1];name='crankcase-rh-major-outer-envelope-donor-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(exist_ok=True,parents=True);O.mkdir(exist_ok=True,parents=True)
planpath='creative/research/powertrain-completion-p18-v1/rh-major-outer-envelope-donor-plan-v100.json';plan=json.loads((R/planpath).read_text());scale=plan['working_scale_m_px'];N=384;M=48;depth=plan['working_depth_m'];wall=plan['working_radial_wall_m']
P=dict(schema=1,package='P18',component_id=plan['component_id'],source=planpath,source_identity=plan['source_identity'],scope=plan['scope'],all_dimensions_estimated=True,camera_calibrated=False,working_depth_m=depth,working_radial_wall_m=wall,material=dict(name='Proposed clean conditional BM150 cast aluminium',base_color_linear=[.33,.35,.37,1],metallic=.7,roughness=.44),package_complete=False,art_accepted=False)
bpy.ops.wm.read_factory_settings(use_empty=True)
def outline(points,split=False):
 C=[]
 for x,y in points:
  if split:x,y=779.3-1.0186*x,.9565*y-8.3
  C.append(Vector(((x-350)*scale,(550-y)*scale)))
 curve=[]
 for i in range(len(C)):
  p=[C[(i+j)%len(C)] for j in range(4)]
  for k in range(24):
   t=k/24;w=[(1-t)**3/6,(3*t**3-6*t*t+4)/6,(-3*t**3+3*t*t+3*t+1)/6,t**3/6];curve.append(sum((a*b for a,b in zip(p,w)),Vector((0,0))))
 radii=[]
 for i in range(N):
  a=math.tau*i/N;d=Vector((math.cos(a),math.sin(a)));hits=[]
  for p,q in zip(curve,curve[1:]+curve[:1]):
   e=q-p;det=d.x*e.y-d.y*e.x
   if abs(det)<1e-15:continue
   r=(p.x*e.y-p.y*e.x)/det;t=(p.x*d.y-p.y*d.x)/det
   if r>0 and 0<=t<1:hits.append(r)
  assert len(hits)==1,(i,hits)
  radii.append(hits[0])
 return radii
A=outline(plan['front_perimeter_pixels_65202']);B=outline(plan['split_perimeter_pixels_65203'],True)
bosses=[]
for i,(x,y) in enumerate(plan['visible_exterior_boss_centres_pixels_65202']):
 q=Vector(((x-350)*scale,(550-y)*scale));bosses.append(dict(centre_source_m=[q.x,q.y],angle=math.atan2(q.y,q.x),radius=q.length,outer_radius_m=[.009,.010,.0105,.011,.0105][i],bore_radius_m=[.0048,.005,.0052,.0054,.005][i],axial_fraction=[1,1,1,.62,1][i]))
def smoothmax(a,b,k=.0025):
 h=max(k-abs(a-b),0)/k;return max(a,b)+h*h*k*.25
V=[];F=[]
for inner in [False,True]:
 for k in range(M+1):
  u=k/M;s=u*u*(3-2*u)
  for i in range(N):
   a=math.tau*i/N;baseline=A[i]*(1-s)+B[i]*s;r=baseline-wall if inner else baseline+.0018*math.sin(math.pi*u)**2
   if inner:
    for b in bosses:
     delta=math.atan2(math.sin(a-b['angle']),math.cos(a-b['angle']));protect=b['bore_radius_m']+.004
     # Visible boss/root material around the bore; bounded inner return, not a bearing web.
     reach=b['radius']-protect;r=-smoothmax(-r,-(baseline-max(0,baseline-reach)*math.exp(-(delta/.16)**2)),.001)
   if not inner:
    for b in bosses:
     delta=math.atan2(math.sin(a-b['angle']),math.cos(a-b['angle']));width=.13;root=math.exp(-(delta/width)**2)
     # Broad observed root: estimated continuous cast transition, not hidden rib architecture.
     axial=1 if b['axial_fraction']==1 else max(0,min(1,(b['axial_fraction']+.12-u)/.18));axial=axial*axial*(3-2*axial)
     reach=b['radius']+b['outer_radius_m'];r=smoothmax(r,baseline+(reach-baseline)*root*axial)
   V.append((r*math.cos(a),r*math.sin(a),-depth*u))
S=(M+1)*N
for k in range(M):
 for i in range(N):
  j=(i+1)%N;a=k*N+i;b=k*N+j;c=(k+1)*N+j;d=(k+1)*N+i;F.extend([(a,b,c,d),(S+a,S+d,S+c,S+b)])
for i in range(N):
 j=(i+1)%N;F.extend([(i,S+i,S+j,j),(M*N+i,M*N+j,S+M*N+j,S+M*N+i)])
ob=mesh_object('RH_DONOR_MAJOR_PERIPHERAL_WALLS_OBSERVED_ROOT_COLUMNS_OPEN_VOID',V,F);recalc(ob)
# Only actual visible exterior boss bores: no bearing seats or internal passages.
for i,b in enumerate(bosses):
 x,y=b['centre_source_m'];bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=b['bore_radius_m'],depth=depth+.04,location=(x,y,-depth/2));tool=bpy.context.object;recalc(tool);bpy.context.view_layer.objects.active=ob;m=ob.modifiers.new('Observed external bore '+str(i+1),'BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=tool;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(tool,do_unlink=True)
clean_smooth(ob);ob['identity']='CONDITIONAL_DONOR_RH_BM150_NOT_EXACT_CURRENT_RDC125';ob['scope']='Peripheral walls and five observed external boss root stations; no internal bearing floor or galleries.'
P['bosses']=bosses;P['relation_to_existing']='Not paired with LH JE541038; existing RH upper land and engine-cover-right remain separate, registration unqualified. No mirror or merged125 identity.';P['upper_saddle']='Opposed split contour retains photographed concave upper opening; no cylinder interior/gallery reconstructed.'
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');finish_source(H,O,P)
(O/'envelope-construction-check.json').write_text(json.dumps(dict(method='Independent source front/split periodic contours, angular-ray correspondence, finite paired peripheral wall, smooth axial loft and bounded broad cast-root elevations at five observed bored stations',perimeter_samples=N,axial_samples=M+1,arbitrary_engine_void_closure=False,internal_bearings_or_galleries=False,source_identity=plan['source_identity'],remaining=['Unmeasured cast-root dimensions/section and short-boss end depth','CurrentRDC125 fit, donor pairing and RH upper-land registration unknown','Upper saddle only bounded observed peripheral contour, no hidden cylindrical bore/gallery']),indent=2)+'\n')
