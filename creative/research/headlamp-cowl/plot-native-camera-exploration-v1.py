"""Original research plot from numerical contours/projections, no photo pixels exported."""
from pathlib import Path
import json,math,ast
import numpy as np
from PIL import Image
from scipy.ndimage import label,binary_erosion
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
Q=Path(__file__).resolve().parent
j=json.loads((Q/'native-camera-exploration-v1.json').read_text())
G=json.loads(Path('/tmp/wewa-cowl-source3-points.json').read_text())
points=np.array(G['points'],dtype=float)[::3]
source=ast.parse((Q/'native-camera-exploration-v1.py').read_text())
project=next(x for x in source.body if isinstance(x,ast.FunctionDef)and x.name=='project')
exec(compile(ast.Module(body=[project],type_ignores=[]),'read-only-projection','exec'))
fig,axes=plt.subplots(2,2,figsize=(11,11),layout='constrained')
for row,v in enumerate(j['two_actual_photos']):
 n=Path(v['photo']['path']).stem[-4:];az=7.5 if n=='8494'else-7.5
 a=np.array(Image.open(v['photo']['path']).convert('RGB'));L,_=label(a.min(axis=2)<180);counts=np.bincount(L.ravel());body=L==(np.argmax(counts[1:])+1);contour=np.argwhere(body&~binary_erosion(body))[::2]
 for col,focal in enumerate([24,50]):
  c=next(c for c in v['camera_candidates']if c['focal_mm_render_assumption_sensor36mm']==focal and c['azimuth_degrees_render_assumption']==az)
  p,depth,_=project(points,c['distance_to_front_origin_m_estimated'],math.radians(c['elevation_degrees_estimated']),math.radians(az),v['view_side_Y_sign_assumed'],c['principal_point_native_px_estimated'],math.radians(c['roll_degrees_estimated']),focal*800/36)
  ax=axes[row,col];ax.scatter(p[:,0],p[:,1],s=.35,alpha=.18,color='#e39022',label='Points du même maillage3')
  ax.scatter(contour[:,1],contour[:,0],s=1,color='#0072b2',alpha=.7,label='Contour natif réel, seuil180')
  if n=='8495':
   xy=c['central_rear_bridge_midpoint_proxy_projected_px'];ax.scatter(*xy,color='#d73027',marker='x',s=50,label='Repère arrière du modèle');ax.scatter(394,233,color='#0072b2',marker='+',s=60,label='Bord central natif (approx.)')
  ax.set(xlim=(0,800),ylim=(800,0),aspect='equal',xlabel='x pixel natif',ylabel='y pixel natif',title=f'Photo{n} — focale HYPOTHÈSE{focal}mm / pose estimée')
  ax.grid(alpha=.2);ax.legend(fontsize=7,loc='lower right')
fig.suptitle('Étude G2 — deux photos réelles, maillage3 strictement inchangé\nLa focale et la pose restent des hypothèses ; aucun calage dimensionnel ni réception de forme.',fontsize=11)
W=Path('/workspace/wewa-assets/work-in-progress/headlamp-cowl-shell-study-v3/native-cameras');W.mkdir(parents=True,exist_ok=True);fig.savefig(W/'native-contours-vs-source3.png',dpi=140);plt.close(fig)
