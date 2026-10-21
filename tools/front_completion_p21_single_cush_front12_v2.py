# Parent SHA256 c6f74d787c10accb0d2766de44a2c539f4a0d826dff9c9315b8c8a9e93737ff2; actual lobe trace and broad flat face replace unsupported pillow.
"""Single asymmetric observed cush lobe exterior only; never repeats the unreceived ring."""
import bpy,math,json,runpy
from pathlib import Path
R=Path('/workspace/wewa');K='front-completion-p21-single-cush-front12-v2';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;H.mkdir(exist_ok=False);O.mkdir(exist_ok=False);bpy.ops.wm.read_factory_settings(use_empty=True);u=runpy.run_path(str(R/'tools/front_completion_front10_mesh_helpers_v1.py'));pixels=[(240,416),(247,424),(249,470),(249,505),(244,515),(225,515),(210,510),(195,494),(174,481),(165,470),(169,458),(200,434),(222,420)];controls=[((x-210)*.00025,(465-y)*.00025)for x,y in pixels];contour=[]
# Explicit private-photo2 bottom-left single lobe trace; original geometry, no photo redistribution.
for k in range(len(controls)):
 a,b,c,d=[controls[(k+i)%len(controls)]for i in [-1,0,1,2]]
 for j in range(16):
  t=j/16;contour.append(tuple(.5*(2*b[q]+(-a[q]+c[q])*t+(2*a[q]-5*b[q]+4*c[q]-d[q])*t*t+(-a[q]+3*b[q]-3*c[q]+d[q])*t**3)for q in [0,1]))
N=len(contour);profile=[(.001*(1-math.cos(math.pi/2*j/16)),.94+.06*math.sin(math.pi/2*j/16))for j in range(17)];profile +=[(.002,1),(.0028,1),(.0031,1.012),(.0034,1),(.007,1),(.0105,1)];profile +=[(.0105+.001*math.sin(math.pi/2*j/24),.9+.1*math.cos(math.pi/2*j/24))for j in range(1,25)];profile +=[(.0115,.9*(1-j/16))for j in range(1,16)];v=[(x*s,y*s,z)for z,s in profile for x,y in contour];f=[]
for i in range(len(profile)-1):
 for j in range(N):a=i*N+j;b=i*N+(j+1)%N;f.append((a,b,b+N,a+N))
base=len(v);v.append((0,0,0));top=len(v);v.append((0,0,.0115))
for j in range(N):f.append((base,(j+1)%N,j));a=(len(profile)-1)*N+j;b=(len(profile)-1)*N+(j+1)%N;f.append((top,a,b))
ob=u['mesh_object']('DK151094_SINGLE_ASYMMETRIC_CUSH_LOBE_NO_RING_NO_WEBS',v,f);audit=u['clean_audit'](ob)
for face in ob.data.polygons:
 zs=[ob.data.vertices[i].co.z for i in face.vertices]
 if max(zs)-min(zs)<1e-10 and abs(face.normal.z)>.999:face.use_smooth=False
ob.data.update();(H/'parameters.json').write_text(json.dumps({'package':'P21','code':'DK151094','unit':'One representative front-most asymmetric lobe exterior; no eightfold repetition or fabricated connection webs','source':'Supplier exact DK151094 multiple physical front/back/top views, related UG coupling rubber','outline_control_m':controls,'working_depth_m':.0115,'trace_pixels_private_photo2':pixels,'trace_scale_estimate_m_per_pixel':.00025,'depth_bounds_m':[.008,.017],'all_dimensions_estimated':True,'rear':'Plain finite artificial review back, not a reconstructed reverse pocket or current bearing/rubber stack','parting_ridge':'Small bounded0.12mm exterior ridge hypothesis from visible molding line, not measured molding flash or wear','contact':'No carrier contact, compression, durometer, count acceptance or ring positioning','material':'Uniform clean dark nonmetal appearance hypothesis only; no measured rubber species or grain'},indent=2));(O/'geometry-check.json').write_text(json.dumps({'objects':[audit],'lobe_count':1,'repeated_ring':False,'webs_fabricated':False,'art_accepted':False},indent=2));u['gray_save'](H,'cush-lobe',[ob]);print(audit)
