"""Distinct DJ151036 open two-cheek exterior with curved sheet return, finite hollow sleeve and cut rod."""
import bpy,math,json,runpy
from pathlib import Path
from math import sin,cos,pi
R=Path('/workspace/wewa');K='front-completion-p23-lh-adjuster-front10-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;H.mkdir(parents=True,exist_ok=False);O.mkdir(parents=True,exist_ok=False);bpy.ops.wm.read_factory_settings(use_empty=True)
U=runpy.run_path(str(R/'tools/front_completion_front10_mesh_helpers_v1.py'));globals().update({k:v for k,v in U.items()if not k.startswith('__')})
P=json.loads((R/'creative/research/front-completion-p23-v1/lh-adjuster-G0-G2.json').read_text());P.update({'frame':'X long axis; cheeks XY at Z +/-6..7.6mm, sleeve Z through eye; no installed pose','root':'Rod root open atX=-44.5mm; 2mm review gap to return outerback atX=-42.5mm; no guessed weld','return':'Source original radiused U return,1.6mm thickness, radius4mm outer/2.4mm inner, short positive overlap into cheeks then exactunion','sleeve':'R10mm open bore, R11.7mm exterior, ends contact inner cheek planes atZ+/-6mm; separate finite body, no inferred weld/bearing','stamps':'Photographed shallow indices deferred; unreadable exact imprint layout not duplicated','all_metric_values_estimated':True});(H/'parameters.json').write_text(json.dumps(P,indent=2))
cheeks=[]
for sign in [1,-1]:
 NX=241;NY=97;v=[];f=[]
 for z in [sign*.006,sign*.0076]:
  for i in range(NX):
   x=-.039+.078*i/(NX-1);w=.011+.005*math.exp(-(x/.013)**6)
   for j in range(NY):
    t=-1+2*j/(NY-1);xx=x
    if x>.037:xx-=.0008*abs(t)**8*smooth((x-.037)/.002)
    v.append((xx,w*t,z))
 L=NX*NY
 for off,rev in [(0,False),(L,True)]:
  for i in range(NX-1):
   for j in range(NY-1):a=off+i*NY+j;face=(a,a+NY,a+NY+1,a+1);f.append(face[::-1]if rev else face)
 loop=list(range(NY))+[i*NY+NY-1 for i in range(1,NX)]+list(range((NX-1)*NY+NY-2,(NX-1)*NY-1,-1))+[i*NY for i in range(NX-2,0,-1)]
 for a,b in zip(loop,loop[1:]+loop[:1]):f.append((a,b,b+L,a+L))
 ob=mesh_object('DJ151036_CHEEK_'+str(sign),v,f);bpy.ops.mesh.primitive_cylinder_add(vertices=192,radius=.010,depth=.06);boolean(ob,bpy.context.object);cheeks.append(ob)
# U return in XZ, extruded across narrow strip; never a filled box across the open gap.
outer=[(-.0385+.004*cos(pi/2+pi/2*i/48),.0036+.004*sin(pi/2+pi/2*i/48))for i in range(49)];outer += [(-.0425,-.0036)];outer += [(-.0385+.004*cos(pi+pi/2*i/48),-.0036+.004*sin(pi+pi/2*i/48))for i in range(1,49)]
inner=[(-.0385+.0024*cos(3*pi/2-pi/2*i/48),-.0036+.0024*sin(3*pi/2-pi/2*i/48))for i in range(49)];inner += [(-.0409,.0036)];inner += [(-.0385+.0024*cos(pi-pi/2*i/48),.0036+.0024*sin(pi-pi/2*i/48))for i in range(1,49)]
poly=outer+inner;n=len(poly);v=[(x,y,z)for y in [-.011,.011]for x,z in poly];f=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
for i in range(n):j=(i+1)%n;f.append((i,j,j+n,i+n))
bridge=mesh_object('DJ151036_CURVED_U_SHEET_RETURN',v,f);boolean(cheeks[0],bridge,'UNION');boolean(cheeks[0],cheeks[1],'UNION');body=cheeks[0];body.name='DJ151036_TWO_CHEEKS_AND_CURVED_RETURN'
# Sleeve closed annulus, true through bore, flush finite contacts on inner cheek faces.
profile=[(.010,-.006),(.0115,-.006),(.0117,-.0058),(.0117,.0058),(.0115,.006),(.010,.006)];n=192;v=[];f=[]
for r,z in profile:
 for j in range(n):a=2*pi*j/n;v.append((r*cos(a),r*sin(a),z))
for row in range(len(profile)):
 for j in range(n):a=row*n+j;b=row*n+(j+1)%n;c=((row+1)%len(profile))*n+(j+1)%n;d=((row+1)%len(profile))*n+j;f.append((a,b,c,d))
sleeve=mesh_object('DJ151036_VISIBLE_HOLLOW_SLEEVE_NO_BEARING_CLAIM',v,f);rod=helical_x('DJ151036_THREAD_OPEN_ROOT_REVIEW_CUT',-.1025,-.0445,r=.003,pitch=.001,depth=.00045)
reports=[clean_audit(body),clean_audit(sleeve),clean_audit(rod,128)];gray_save(H,'lh-adjuster',[body,sleeve,rod]);(O/'geometry-check.json').write_text(json.dumps({'objects':reports,'review_root_gap_m':.002,'sleeve_contact_planes_m':[-.006,.006],'sleeve_hidden_weld':False,'all_metric_values_estimated':True,'mounted_fit':False},indent=2));print(reports)
