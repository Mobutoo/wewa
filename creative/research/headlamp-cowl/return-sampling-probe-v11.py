import ast,json,math,bisect,numpy as np
from pathlib import Path
H=Path('/workspace/wewa-github/assets-src/moto-components/headlamp/cowl');R=H.parents[3];profile=json.loads((H/'rear-profile-v5.json').read_text());rp=json.loads((R/'creative/research/headlamp-cowl/sixth-support-return-plan-v11.json').read_text())['P6_return_candidate'];W=.0025;tree=ast.parse((H/'build_raw_return_study_v11.py').read_text());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in['rear_profile','section','cat','mid','frame','point']];exec(compile(ast.Module(body=nodes,type_ignores=[]),'exact-current-parametric-functions','exec'))
for refine,nc in[(8,60),(16,120),(24,180)]:
 ang=np.array([math.tau*(j+k/refine)/256 for j in range(42,52)for k in range(refine)]+[math.tau*52/256]);pts=[];norms=[]
 for k in range(nc+1):
  a=math.pi*k/nc
  for th in ang:
   e=1e-5;dt=(point(th+e,('rear',1,a))-point(th-e,('rear',1,a)))/(2*e);da=(point(th,('rear',1,a+e))-point(th,('rear',1,a-e)))/(2*e);n=np.cross(dt,da);n/=np.linalg.norm(n);pts.append(point(th,('rear',1,a)));norms.append(n)
 pts=np.array(pts);norms=np.array(norms);na=len(ang);min_dot=1;bad=[]
 for k in range(nc):
  for j in range(na-1):
   ids=[k*na+j,k*na+j+1,(k+1)*na+j+1,(k+1)*na+j]
   for tid in[[ids[0],ids[1],ids[2]],[ids[0],ids[2],ids[3]]]:
    pa,pb,pc=pts[tid];cross=np.cross(pb-pa,pc-pa);cross/=np.linalg.norm(cross);d=min(norms[ix]@cross for ix in tid);min_dot=min(min_dot,d)
    if d<.9:bad.append([k,j,float(d)])
 print('ANALYTIC_PROBE',refine,nc,'mindot',min_dot,'bad',len(bad),'worst',sorted(bad,key=lambda x:x[2])[:3],flush=True)
