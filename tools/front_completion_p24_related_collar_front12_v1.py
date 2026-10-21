"""DU151005 related4gear observed collar/sleeve exterior, never substituted for UG DS151061."""
import bpy,math,json,runpy
from pathlib import Path
R=Path('/workspace/wewa');K='front-completion-p24-related-collar-front12-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;H.mkdir(exist_ok=False);O.mkdir(exist_ok=False);bpy.ops.wm.read_factory_settings(use_empty=True);u=runpy.run_path(str(R/'tools/front_completion_front10_mesh_helpers_v1.py'));N=256
white=[(.009,0),(.0153,0)]
for j in range(1,17):a=math.pi/2*j/16;white.append((.0153+.0007*math.sin(a),.0007*(1-math.cos(a))))
white.append((.016,.004))
for j in range(1,17):a=math.pi/2*j/16;white.append((.0153+.0007*math.cos(a),.004+.0007*math.sin(a)))
white +=[(.0148,.0047),(.0144,.0049),(.0135,.0056),(.0123,.0072),(.0119,.0082),(.0118,.009),(.0118,.0111)]
for j in range(1,17):a=math.pi/2*j/16;white.append((.0111+.0007*math.cos(a),.0111+.0007*math.sin(a)))
white +=[(.0093,.0118),(.009,.0115)]
metal=[(.0087,0),(.009,.0003),(.009,.0137),(.0087,.014),(.0048,.014),(.0045,.0137),(.0045,.0003),(.0048,0)]
def lathe(name,profile):
 v=[(r*math.cos(2*math.pi*j/N),r*math.sin(2*math.pi*j/N),z)for r,z in profile for j in range(N)];f=[]
 for i in range(len(profile)):
  for j in range(N):a=i*N+j;b=i*N+(j+1)%N;c=((i+1)%len(profile))*N+(j+1)%N;d=((i+1)%len(profile))*N+j;f.append((a,b,c,d))
 return u['mesh_object'](name,v,f)
body=lathe('DU151005_OBSERVED_OFFWHITE_STEPPED_COLLAR',white);sleeve=lathe('DU151005_OBSERVED_DARK_SLEEVE_OPEN_BORE',metal);audits=[u['clean_audit'](o)for o in [body,sleeve]]
(H/'parameters.json').write_text(json.dumps({'package':'P24','code':'DU151005','variant':'D04 plate32 item5 related4gear collar assembly; UG5gear DS151061 different identity, not replaced','working_dimensions_m':{'outer_radius':.016,'white_height':.0118,'sleeve_outer_radius':.009,'bore_radius':.0045,'height':.014},'estimated_bounds_m':{'outer_radius':[.012,.020],'height':[.010,.020],'sleeve_radius':[.007,.012],'bore_radius':[.0035,.006]},'all_dimensions_estimated':True,'observed':'Quarter/top views establish stepped flared offwhite body, dark sleeve annulus and open bore. Relative section proportions only, no physical measurement.','white_section_profile_m':white,'sleeve_profile_m':metal,'finite_review_closures':'Lower annuli and inner interface continuation authored finite estimates, not observed bearing seats or certified manufactured wall','contact':'Author coaxial collar/sleeve radius9mm contact only; true fit/tolerance/retention unknown, no wheel/fork/axle stack','material':'Two clean appearance hypotheses, offwhite nonmetal and dark metal; no measured polymer species, alloy, grain or finish'},indent=2));(O/'geometry-check.json').write_text(json.dumps({'objects':audits,'independent_closed_bodies':2,'bore_open':True,'author_contact_radius_m':.009,'actual_mounted_fit':False,'current_RDC_identity':False},indent=2));u['gray_save'](H,'front-collar',[body,sleeve]);print(audits)
