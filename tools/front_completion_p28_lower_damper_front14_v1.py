"""Original DS181009 observed top/edge/bore exterior skin only; underside remains open."""
from pathlib import Path
import bpy,runpy,math,json
R=Path('/workspace/wewa');K='front-completion-p28-lower-damper-front14-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;H.mkdir(exist_ok=False);O.mkdir(exist_ok=False);bpy.ops.wm.read_factory_settings(use_empty=True);u=runpy.run_path(str(R/'tools/front_completion_front10_mesh_helpers_v1.py'));N=256;ro=.017;ri=.006;h=.003;e=.00035
# Explicit author-estimated thickness: open cut is not a reconstructed hidden lower face.
profile=[(ro,0),(ro,h-e)]
for i in range(1,13):a=math.pi/2*i/12;profile.append((ro-e+e*math.cos(a),h-e+e*math.sin(a)))
profile +=[(.014,h),(.010,h),(ri+e,h)]
for i in range(1,13):a=math.pi/2*i/12;profile.append((ri+e-e*math.sin(a),h-e+e*math.cos(a)))
profile +=[(ri,0)]
v=[(r*math.cos(2*math.pi*j/N),r*math.sin(2*math.pi*j/N),z)for r,z in profile for j in range(N)];f=[]
for i in range(len(profile)-1):
 for j in range(N):a=i*N+j;b=i*N+(j+1)%N;f.append((a,b,b+N,a+N))
ob=u['mesh_object']('DS181009_VISIBLE_TOP_OUTER_EDGE_BORE_SKIN_OPEN_UNDERSIDE',v,f);audit=u['clean_audit'](ob,expected_boundary=2*N)
# Ensure top face outward, then keep planar annulus flat shaded.
faces=[p for p in ob.data.polygons if abs(p.center.z-h)<1e-8]
if sum(p.normal.z for p in faces)<0:
 for p in ob.data.polygons:p.flip()
 ob.data.update()
for p in ob.data.polygons:
 if abs(p.normal.z)>.999999:p.use_smooth=False
ob.data.update();(H/'parameters.json').write_text(json.dumps({'package':'P28','code':'DS181009','scope':'Observed top annulus, exterior edge and visible bore skin only; two intentional open lower review rings, no underside face or hidden bearing section','all_dimensions_estimated':True,'working_dimensions_m':{'outer_radius':ro,'bore_radius':ri,'visible_depth':h,'edge_radius':e},'bounds_m':{'outer_radius':[.014,.021],'bore_radius':[.0045,.008],'depth':[.0015,.006],'edge_radius':[.0001,.0008]},'source':'New exact-code Bajajonline photograph, one oblique pose only','not_a_complete_damper':True,'unresolved':['Underside/dishing/section','True dimensions and rubber specification','Preload and handlebar mounting contact'],'upper_damper_copied':False},indent=2));(O/'geometry-check.json').write_text(json.dumps({'objects':[audit],'intentional_open_boundary_loops':2,'hidden_underside_fabricated':False},indent=2));u['gray_save'](H,'lower-damper',[ob])
