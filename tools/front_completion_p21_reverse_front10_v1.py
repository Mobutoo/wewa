"""NEW DS151068 reverse exterior sub-study only. Existing front gray/material and G4 hold untouched."""
import bpy,math,json,runpy
from pathlib import Path
from math import sin,cos,pi,sqrt
R=Path('/workspace/wewa');K='front-completion-p21-reverse-front10-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;H.mkdir(parents=True,exist_ok=False);O.mkdir(parents=True,exist_ok=False);bpy.ops.wm.read_factory_settings(use_empty=True)
U=runpy.run_path(str(R/'tools/front_completion_front10_mesh_helpers_v1.py'));globals().update({k:v for k,v in U.items()if not k.startswith('__')})
P=json.loads((R/'creative/research/front-completion-p21-opposite-v2/G0-G2-next-revision.json').read_text());P.update({'scope':'Independent photographed rear exterior, not a remake/replacement of front gray v3','frame':'Z up out of photographed rear; not installed or aligned to existing front frame','front_review_closure':'Artificial plain finite annular sheet atZ=-3mm; not a reconstructed front face, OEM wall or certified mounted section','bore':'Open central diameter37mm estimate; plain inner review continuation, not a bearing seat specification','witness_marks':'Rear round witnesses/lettering not interpreted as screws, caps or certified part stamps; excluded','finish':'Clean uniform silver hypothesis only; no cast grain or alloy measurement','all_metric_values_estimated':True});(H/'parameters.json').write_text(json.dumps(P,indent=2))
N=768;NR=241;v=[];f=[]
def height(r,a):
 # Rear stepped collar and outer circular bead independently constrained only as exterior.
 if r<=.0205:collar=.012
 elif r<.021:collar=.012+.003*smooth((r-.0205)/.0005)
 elif r<=.024:collar=.015
 else:collar=.015*(1-smooth((r-.024)/.0025))
 pad=0
 for t in [pi/4,3*pi/4,5*pi/4,7*pi/4]:
  x=r*cos(a-t);y=r*sin(a-t);dist=sqrt((x-min(.054,max(.036,x)))**2+y*y)-.0055;mask=1-smooth((dist+.0015)/.003);pad=max(pad,.020*mask)
 rim=.0025*smooth((r-.0615)/.0015)*(1-.25*smooth((r-.064)/.001))
 return max(collar,pad,rim)
for i in range(NR):
 r=.0185+(.065-.0185)*i/(NR-1)
 for j in range(N):a=2*pi*(j+.173)/N;v.append((r*cos(a),r*sin(a),height(r,a)))
# Outer edge continuation and artificial front review closure, not old front geometry.
for r,z in [(.065,-.0025),(.0645,-.003),(.0185,-.003)]:
 for j in range(N):a=2*pi*(j+.173)/N;v.append((r*cos(a),r*sin(a),z))
rows=NR+3
for i in range(rows):
 for j in range(N):a=i*N+j;b=i*N+(j+1)%N;c=((i+1)%rows)*N+(j+1)%N;d=((i+1)%rows)*N+j;f.append((a,b,c,d))
ob=mesh_object('DS151068_REVERSE_ONLY_PADS_COLLAR_RIM_REVIEW_CLOSURE',v,f)
for a in [0,pi/2,pi,3*pi/2]:
 bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=.0035,depth=.100,location=(.047*cos(a),.047*sin(a),.010));boolean(ob,bpy.context.object)
report=clean_audit(ob);gray_save(H,'carrier-reverse',[ob]);(O/'geometry-check.json').write_text(json.dumps({'objects':[report],'four_observed_rear_mouths':True,'four_observed_drive_pad_envelopes':True,'plain_front_review_closure_only':True,'current_RDC_identity':False,'mounted_fit':False,'all_metric_values_estimated':True},indent=2));print(report)
