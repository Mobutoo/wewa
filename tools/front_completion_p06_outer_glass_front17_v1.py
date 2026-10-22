"""DJ201051 continuous visible outer glazing envelope, no reflector or hidden glass wall."""
from pathlib import Path
import bpy,runpy,math,json
R=Path('/workspace/wewa');K='front-completion-p06-outer-glass-front17-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K
H.mkdir(exist_ok=False);O.mkdir(exist_ok=False);bpy.ops.wm.read_factory_settings(use_empty=True);u=runpy.run_path(str(R/'tools/front_completion_front10_mesh_helpers_v1.py'))
N=256;nr=48;radius=.085;sag=.0035;v=[(0,0,sag)];f=[]
# Single continuous shallow convex front surface crosses both projected reflector apertures.
# No opening is cut through the glazing, no back wall or invented optical relief.
for i in range(1,nr+1):
 r=radius*i/nr;z=sag*(1-(r/radius)**2)
 for j in range(N):a=2*math.pi*j/N;v.append((r*math.cos(a),r*math.sin(a),z))
for j in range(N):f.append((0,1+j,1+(j+1)%N))
for i in range(nr-1):
 for j in range(N):a=1+i*N+j;b=1+i*N+(j+1)%N;f.append((a,a+N,b+N,b))
ob=u['mesh_object']('DJ201051_CONTINUOUS_OUTER_GLASS_ENVELOPE_NO_OPTICAL_RELIEF',v,f);u['orient'](ob)
# Keep the visible front normals positive Z for a surface with one intentional peripheral boundary.
if sum(p.normal.z for p in ob.data.polygons)<0:
 for p in ob.data.polygons:p.flip()
audit=u['clean_audit'](ob,expected_boundary=N)
params={'package':'P06','code':'DJ201051','scope':'Continuous exposed front glazing envelope only. Both visible white circles belong behind the glazing, not holes through it. No hidden inner wall, glass thickness, peripheral striae, optical relief, reflector, chrome ring duplication or frame invented.','primary':'Exact supplier DJ201051 front Prom and restored Crosland oblique physical image with original SHA match','related':'PF401007 Mundimotos oblique used only to assess envelope plausibility, not exact OEM covariance','working_radius_m':radius,'working_sag_m':sag,'all_absolute_dimensions_estimated':True,'uncertainty_m':{'radius':[.075,.100],'sag':[0,.0085]},'sag_bounds_status':'Broad modeling hypothesis spanning flat to weak convex front; not measured or uniquely recovered from perspective photographs','profile':'z=sag*(1-(r/R)^2), low-order interpolation of visible front envelope, not an optical prescription','hidden_glass_wall':'not modeled','G1':'partial','G2':'estimated uncalibrated','G4':'held, single exterior transmission surface','mounted_fit':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(params,indent=2));(O/'geometry-check.json').write_text(json.dumps({'objects':[audit],'intentional_boundary_loops':1,'continuous_over_projected_apertures':True,'center_vertex_present':True},indent=2))
(O/'child-plan.json').write_text(json.dumps({'package':'P06','component_id':'MOTO-HEADLAMP-DJ201051-OUTER-GLASS-ENVELOPE-STUDY-001','child':'DJ201051 visible continuous outer glazing envelope','scope':params['scope']+' Radius and weak convexity broad working hypotheses, not measured section or fitted current motorcycle.','protocols':['front_completion_p06_outer_glass_front17_v1.py','front_completion_front10_mesh_helpers_v1.py','front_completion_front14_render_v1.py','front_completion_front15_capsule_material_v1.py'],'remaining':['Glazing inner surface/thickness, actual sag and edge profile','Ownership and depth of horizontal lines/peripheral striae','Separate source-led reflector facets and bowl contour','Actual current motorcycle dimensions, placement and assembled optics']},indent=2))
u['gray_save'](H,'outer-glass',[ob])
