import json,math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=Path(__file__).resolve().parent;V=O.parent/'engine-exterior-completion-v1';data=json.loads((O/'geometry-read.json').read_text());poses=json.loads((V/'poses-and-sources.json').read_text());source={r['key']:r for r in data};base={r['key']:np.array(r['matrix']) for r in poses['parents']}
a=math.radians(20);rot=np.eye(4);rot[1:3,1:3]=[[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]]
# LH source saddle bottom/cylinder axis is explicitly bounded in original G1 plan.
anchor=np.array([-.0506,.078,-.058,1]);world=base['conditional-lh']@anchor;target=np.array([0,.125,-.54,1]);delta=rot.copy();delta[:3,3]=target[:3]-(rot@world)[:3]
new={k:(delta@M if k.startswith('conditional') else M) for k,M in base.items()}
fig,axes=plt.subplots(1,2,figsize=(13,7),sharex=True,sharey=True)
for ax, label, mats in zip(axes,['v1 inherited poses','v2 rigid +20deg saddle alignment'],[base,new]):
 for key,color in [('WEWA_ENGINE_COVER_LEFT','#cc502b'),('WEWA_ENGINE_COVER_RIGHT','#aa5599'),('WEWA_ENGINE_CYLINDER','#222222'),('conditional-lh','#1e77ba'),('conditional-rh','#248b57'),('conditional-service-port','#d1a328')]:
  pts=np.array(source[key]['vertices']);p=np.c_[pts,np.ones(len(pts))]@mats[key].T;ax.scatter(p[::5,1],p[::5,2],s=.15,c=color,label=key)
 ax.set_title(label);ax.set_aspect('equal');ax.grid();ax.set_xlabel('global Y rear [m]');ax.set_xlim(-.02,.44);ax.set_ylim(-.79,-.43)
axes[0].set_ylabel('global Z up [m]');axes[1].legend(markerscale=9,fontsize=7);fig.tight_layout();fig.savefig(O/'rigid-pose-diagnostic.png',dpi=150)
out=[]
for r in poses['parents']:
 r=dict(r);r['matrix']=new[r['key']].tolist();out.append(r)
(O/'trial-poses.json').write_text(json.dumps(dict(parents=out,rigid_delta=delta.tolist(),source_saddle_anchor_m=anchor.tolist(),v1_world_anchor=world.tolist(),v2_target=target.tolist(),method='20degree native cylinder inclination; LH G1 estimated saddle bottom is source reference. RH common delta only a first trial, not certified paired donor.'),indent=2))
