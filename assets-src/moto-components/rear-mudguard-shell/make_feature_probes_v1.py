"""Local intended mouth and adjacent finitewall probes; not installedfit tests."""
from pathlib import Path
import json,sys,numpy as np
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H));from shell_surface_v1 import P,base,base_normal,frames
probes=[]
for m in P['observed_mouths_estimated']:
 q,J,inv=frames[m['id']];c=base(q);n=base_normal(q);probes.append({'name':m['id']+' actually open','origin':(c+n*.03).tolist(),'direction':(-n).tolist(),'expected_hits':0,'max_distance':.06})
 wallq=q+inv@np.array([m['mean_edge_radius_m']+.005,0]);c=base(wallq);n=base_normal(wallq);probes.append({'name':m['id']+' adjacent finitewall','origin':(c+n*.03).tolist(),'direction':(-n).tolist(),'expected_hits':2,'max_distance':.06})
probes+=[{'name':'wheelspace remains unfilled','origin':[0,.08,-.055],'direction':[1,0,0],'expected_hits':0,'max_distance':.05},{'name':'fronttray finitefloor','origin':[0,-.22,.05],'direction':[0,0,-1],'expected_hits':2,'max_distance':.3}]
(H/'features-intended-probes-v1.json').write_text(json.dumps({'probes':probes,'scope':'Actual local mouth/finitewall probes only, not certified contact geometry or globalselfintersection'},indent=2)+'\n')
