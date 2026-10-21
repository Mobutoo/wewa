"""Single asymmetric observed cush lobe exterior only; never repeats the unreceived ring."""
import bpy,math,json,runpy
from pathlib import Path
R=Path('/workspace/wewa');K='front-completion-p21-single-cush-front12-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;H.mkdir(exist_ok=False);O.mkdir(exist_ok=False);bpy.ops.wm.read_factory_settings(use_empty=True);u=runpy.run_path(str(R/'tools/front_completion_front10_mesh_helpers_v1.py'));controls=[(-.010,-.008),(-.006,-.011),(.006,-.010),(.012,-.005),(.010,.002),(.002,.013),(-.004,.012),(-.008,.005)];contour=[]
# Original asymmetric rounded outline from the isolated front-most visible lobe, not a generic sector copy.
for k in range(len(controls)):
 a,b,c,d=[controls[(k+i)%len(controls)]for i in [-1,0,1,2]]
 for j in range(24):
  t=j/24;w=[(1-t)**3/6,(3*t**3-6*t*t+4)/6,(-3*t**3+3*t*t+3*t+1)/6,t**3/6];contour.append(tuple(sum(w[i]*p[axis]for i,p in enumerate([a,b,c,d]))for axis in [0,1]))
N=len(contour);profile=[(0,.87),(.0004,.94),(.0012,1),(.0028,1),(.0031,1.012),(.0034,1),(.0087,1),(.010,.985),(.011,.94),(.0116,.83),(.012,.62),(.01225,.3)];v=[(x*s,y*s,z)for z,s in profile for x,y in contour];f=[]
for i in range(len(profile)-1):
 for j in range(N):a=i*N+j;b=i*N+(j+1)%N;f.append((a,b,b+N,a+N))
base=len(v);v.append((0,0,0));top=len(v);v.append((0,0,.0123))
for j in range(N):f.append((base,(j+1)%N,j));a=(len(profile)-1)*N+j;b=(len(profile)-1)*N+(j+1)%N;f.append((top,a,b))
ob=u['mesh_object']('DK151094_SINGLE_ASYMMETRIC_CUSH_LOBE_NO_RING_NO_WEBS',v,f);audit=u['clean_audit'](ob);(H/'parameters.json').write_text(json.dumps({'package':'P21','code':'DK151094','unit':'One representative front-most asymmetric lobe exterior; no eightfold repetition or fabricated connection webs','source':'Supplier exact DK151094 multiple physical front/back/top views, related UG coupling rubber','outline_control_m':controls,'working_depth_m':.0123,'depth_bounds_m':[.008,.017],'all_dimensions_estimated':True,'rear':'Plain finite artificial review back, not a reconstructed reverse pocket or current bearing/rubber stack','parting_ridge':'Small bounded0.12mm exterior ridge hypothesis from visible molding line, not measured molding flash or wear','contact':'No carrier contact, compression, durometer, count acceptance or ring positioning','material':'Uniform clean dark nonmetal appearance hypothesis only; no measured rubber species or grain'},indent=2));(O/'geometry-check.json').write_text(json.dumps({'objects':[audit],'lobe_count':1,'repeated_ring':False,'webs_fabricated':False,'art_accepted':False},indent=2));u['gray_save'](H,'cush-lobe',[ob]);print(audit)
