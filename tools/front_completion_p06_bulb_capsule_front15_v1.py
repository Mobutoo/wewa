"""CL201023 observed capsule exterior only, open lower review cut; no guessed wall or hidden seal."""
import bpy,runpy,math,json
from pathlib import Path
R=Path('/workspace/wewa');K='front-completion-p06-bulb-capsule-front15-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;H.mkdir(exist_ok=False);O.mkdir(exist_ok=False);bpy.ops.wm.read_factory_settings(use_empty=True);u=runpy.run_path(str(R/'tools/front_completion_front10_mesh_helpers_v1.py'));N=192
# Two material regions of one observed exterior: no duplicate coincident coating surface.
glass=[(.0077,0),(.0080,.001),(.00822,.0025),(.00825,.004),(.00825,.028),(.00823,.030),(.00815,.0315)]
cap=[(.00815,.0315),(.00805,.0325),(.0077,.0335),(.007,.0345),(.0059,.0353),(.0045,.0359),(.0028,.0363),(.0018,.0368),(.00155,.0378),(.00135,.0388),(.0009,.0395),(.0004,.0399)]
def skin(name,profile,apex=False):
 verts=[(r*math.cos(2*math.pi*j/N),r*math.sin(2*math.pi*j/N),z)for r,z in profile for j in range(N)];faces=[]
 for i in range(len(profile)-1):
  for j in range(N):a=i*N+j;b=i*N+(j+1)%N;faces.append((a,b,b+N,a+N))
 if apex:
  top=len(verts);verts.append((0,0,.040))
  for j in range(N):a=(len(profile)-1)*N+j;b=(len(profile)-1)*N+(j+1)%N;faces.append((a,b,top))
 ob=u['mesh_object'](name,verts,faces);audit=u['clean_audit'](ob,expected_boundary=N if apex else 2*N)
 if sum(p.normal.x*p.center.x+p.normal.y*p.center.y for p in ob.data.polygons)<0:
  for p in ob.data.polygons:p.flip()
  ob.data.update()
 return ob,audit
body,a=skin('CL201023_CLEAR_CAPSULE_OUTER_SKIN_NO_INNER_WALL',glass);tip,b=skin('CL201023_OPAQUE_TIP_REGION_AND_EXHAUST_NIPPLE',cap,True);(H/'parameters.json').write_text(json.dumps({'package':'P06','code':'CL201023','scope':'Observed external glass capsule tube and opaque domed tip/exhaust nipple only. One lower review cut at collar; material seam divides one exterior surface, not a physical split capsule. No hidden pinch seal, inner wall, gas fill, unsupported filament or prescription.','source':'Same exact-code three-pose supplier photographs actually read, corroborating Osram HS1 class reference separately','all_dimensions_estimated':True,'working_m':{'body_radius':.00825,'visible_length':.040,'coating_begin_z':.0315},'bounds_m':{'radius':[.0075,.009],'length':[.036,.045],'coating_start':[.028,.034]},'true_wall_thickness':'Unknown, not fabricated. Single exterior surface, not a solid glass rod.','material':'Thin transmission surface hypothesis only, not calibrated physical optics or received light output','complete_bulb':False},indent=2));(O/'geometry-check.json').write_text(json.dumps({'objects':[a,b],'open_boundary_scope':'Body lower cut plus duplicated material seam boundary; tip closes at actual-shaped exhaust nipple. No inner wall.','physical_gas_or_optical_function':False},indent=2));u['gray_save'](H,'bulb-capsule',[body,tip])
