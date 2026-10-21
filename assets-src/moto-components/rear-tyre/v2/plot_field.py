"""Scientific author-parameter field diagram, not a photographed tyre mould."""
from pathlib import Path
import json,hashlib,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from junction_field import JunctionField
H=Path(__file__).resolve().parent;O=H.parents[3]/'creative/reviews/rear-tyre-v2';P=json.loads((H/'parameters.json').read_text());F=JunctionField(P);arc,x=np.meshgrid(np.linspace(0,2*F.pitch,700),np.linspace(-.017,.017,400));a=F.fields(x,arc);b=F.fields(x,arc,True);d0=a.max(-1);d1=F.depth(x,arc,True);assert np.all(b<=a+1e-18)and not np.any((d0==0)&(d1>0));fig,axs=plt.subplots(1,3,figsize=(13,5))
for ax,depth,title in zip(axs,[d0,d1,d1-d0],['Champs v1 : queues sur couronne opposée','Terminaisons dans le fond existant','Variation de profondeur (mm)']):
 im=ax.pcolormesh(arc*1000,x*1000,depth*1000,shading='auto',cmap='coolwarm'if ax==axs[2]else'viridis');ax.contour(arc*1000,x*1000,a[:,:,0],levels=[1e-8],colors='white',linewidths=.55);ax.set_xlabel('Arc autour de la roue (mm)');ax.set_title(title,fontsize=9);ax.set_aspect('equal');fig.colorbar(im,ax=ax,shrink=.5)
axs[0].set_ylabel('X transversal (mm)');fig.suptitle('Construction originale estimée : uniquement les supports existants, aucune nouvelle gorge — pas un relevé OEM',fontsize=10);fig.tight_layout();p=O/'junction-field-termination.png';fig.savefig(p,dpi=150);plt.close(fig);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r={'PNG_sha256':sha(p),'script_sha256':sha(Path(__file__)),'field_script_sha256':sha(H/'junction_field.py'),'parameters_sha256':sha(H/'parameters.json'),'grid_shape':[400,700],'sampled_max_extra_depth_m':float((d1-d0).max()),'sampled_max_restoration_m':float((d0-d1).max()),'no_new_channel_support_on_grid':True,'scope':'Author scalar fields, not actual mesh section, measurement or known OEM mould. Source arrays and native macro are separate proofs.','art_accepted':False};(O/'junction-field-termination.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
