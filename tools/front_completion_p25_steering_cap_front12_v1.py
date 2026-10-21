"""Original DS181015 steering-cap-nut exterior; not a fork-tube cap or clamp bolt."""
import bpy,math,json,runpy
from pathlib import Path
R=Path('/workspace/wewa');K='front-completion-p25-steering-cap-front12-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;H.mkdir(exist_ok=False);O.mkdir(exist_ok=False);bpy.ops.wm.read_factory_settings(use_empty=True);u=runpy.run_path(str(R/'tools/front_completion_front10_mesh_helpers_v1.py'));pi=math.pi;AF=.024;rad=AF/math.sqrt(3);edge=.00035;contour=[]
for k in range(6):
 a=k*pi/3;cx=(rad-edge/math.sin(pi/3))*math.cos(a);cy=(rad-edge/math.sin(pi/3))*math.sin(a)
 arc=[(cx+edge*math.cos(a-pi/6+pi/3*j/16),cy+edge*math.sin(a-pi/6+pi/3*j/16))for j in range(17)];contour+=arc;end=arc[-1];b=(k+1)*pi/3;nx=(rad-edge/math.sin(pi/3))*math.cos(b)+edge*math.cos(b-pi/6);ny=(rad-edge/math.sin(pi/3))*math.sin(b)+edge*math.sin(b-pi/6)
 for j in range(1,17):t=j/17;contour.append((end[0]*(1-t)+nx*t,end[1]*(1-t)+ny*t))
N=len(contour);rings=[]
for z,scale in [(0,.97),(.00015,.987),(.00035,1),(.001,1),(.004,1),(.0085,1)]:rings.append([(x*scale,y*scale,z)for x,y in contour])
for j in range(1,25):
 t=j/24;s=t*t*(3-2*t);row=[]
 for x,y in contour:a=math.atan2(y,x);r=math.hypot(x,y)*(1-s)+.0121*s;row.append((r*math.cos(a),r*math.sin(a),.0085+.0025*t))
 rings.append(row)
for z in [.012,.014,.016]:rings.append([(.0121*math.cos(math.atan2(y,x)),.0121*math.sin(math.atan2(y,x)),z)for x,y in contour])
for j in range(1,25):
 a=pi/2*j/24;r=.01145+.00065*math.cos(a);z=.016+.00065*math.sin(a);rings.append([(r*math.cos(math.atan2(y,x)),r*math.sin(math.atan2(y,x)),z)for x,y in contour])
for j in range(1,33):
 r=.01145*(1-j/33);z=.01665+.00035*(1-(r/.01145)**2);rings.append([(r*math.cos(math.atan2(y,x)),r*math.sin(math.atan2(y,x)),z)for x,y in contour])
v=[p for ring in rings for p in ring];f=[]
for i in range(len(rings)-1):
 for j in range(N):a=i*N+j;b=i*N+(j+1)%N;f.append((a,b,b+N,a+N))
base=len(v);v.append((0,0,0));top=len(v);v.append((0,0,.017))
for j in range(N):f.append((base,(j+1)%N,j));a=(len(rings)-1)*N+j;b=(len(rings)-1)*N+(j+1)%N;f.append((top,a,b))
ob=u['mesh_object']('DS181015_STEERING_CAP_EXTERIOR_NO_HIDDEN_THREAD',v,f);audit=u['clean_audit'](ob);(H/'parameters.json').write_text(json.dumps({'package':'P25','code':'DS181015','working_m':{'hex_across_flats':AF,'height':.017,'crown_radius':.0121,'hex_corner_radius':edge},'estimated_bounds_m':{'AF':[.020,.030],'height':[.013,.022],'crown_radius':[.010,.015]},'all_dimensions_estimated':True,'identity':'D04 UG front fork item8 steering cap nut, distinct from fork tube cap and lower clamp bolt','reference':'Exact supplier DS181015 two poses plus exposure repeat','underside':'Artificial plain finite review closure; no threaded inner socket, bearing seat, washer or installed fit','finish':'Uniform clean silver hypothesis; no measured chrome plating, scratches or stamps'},indent=2));(O/'geometry-check.json').write_text(json.dumps({'objects':[audit],'hidden_thread_fabricated':False,'art_accepted':False},indent=2));u['gray_save'](H,'steering-cap',[ob]);print(audit)
