"""Plot actual triangle-plane section data, not a designed or photographic profile."""
from pathlib import Path
import json,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
H=Path(__file__).resolve().parent;O=H.parents[3]/'creative/reviews/rear-tyre-v2';P=O/'native-section-check.json';j=json.loads(P.read_text());fig,axs=plt.subplots(1,2,figsize=(10,6));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for row in j['rows']:
 a=row['section_xr_m']+[row['section_xr_m'][0]];x=[q[0]*1000 for q in a];y=[q[1]*1000 for q in a]
 for ax in axs:ax.plot(x,y,linewidth=.7,alpha=.55)
for ax in axs:ax.set_xlabel('X transversal (mm)');ax.set_ylabel('Rayon dans la coupe (mm)');ax.grid(alpha=.2);ax.set_aspect('equal')
axs[0].set(xlim=(-50,50),ylim=(210,305),title='8 coupes réelles du maillage candidat');axs[1].set(xlim=(-20,20),ylim=(283,302),title='Couronne et rainures natives');fig.suptitle('Pneu arrière : section estimée, sans mesure OEM ni simulation de pression',fontsize=10);fig.tight_layout();png=O/'native-sections.png';fig.savefig(png,dpi=150);plt.close(fig)
(O/'native-sections-plot.json').write_text(json.dumps({'source_sha256':j['source_sha256'],'export_sha256':j['export_sha256'],'section_data_sha256':sha(P),'plot_script_sha256':sha(Path(__file__)),'PNG_sha256':sha(png),'scope':'Plot of exact diagnostic section data, not a photograph, manufacturing section or pressure simulation.'},indent=2)+'\n')
