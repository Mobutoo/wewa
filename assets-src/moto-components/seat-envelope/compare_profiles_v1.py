"""Private native image overlays and descriptive projection residuals; no camera fit."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_erosion,distance_transform_edt
R=Path(__file__).resolve().parents[3];O=R/'creative/reviews/seat-envelope-study-v1';W=Path('/workspace/wewa-assets/work-in-progress/seat-envelope-study-v1');j=json.loads((W/'actual-export-positions.json').read_text());cs=json.loads((R/'creative/research/reference-camera-studies/camera-studies.json').read_text());lm=json.loads((R/'creative/research/body-powertrain-18/profile-landmarks.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();report={'source_sha256':json.loads((O/'build-report.json').read_text())['source_sha256'],'export_sha256':j['export_sha256'],'camera_input_sha256':sha(R/'creative/research/reference-camera-studies/camera-studies.json'),'landmarks_sha256':sha(R/'creative/research/body-powertrain-18/profile-landmarks.json'),'no_camera_or_guide_moved':True,'views':[],'no_calibrated_tolerance_or_reception':True,'art_accepted':False}
for v in cs['views']:
 ann=next(a for a in lm['views']if a['id']==v['id'])
 for c,name in [(v['selected_working_camera'],'fixed-ORTHO'),(next(h for h in v['perspective_comparison']['hypotheses']if h['lens_mm']==50),'fixed-PERSP50')]:
  mat=np.array(c['rotation_matrix_local_to_world']);loc=np.array(c['location_m']);mask=Image.new('1',(1000,700));draw=ImageDraw.Draw(mask)
  for p in j['primitives']:
   coords=(np.array(p['positions_blender'])-loc)@mat
   if c['kind']=='ORTHO':xy=coords[:,:2]*(1000/c['ortho_scale_m'])
   else:xy=coords[:,:2]/(-coords[:,2,None])*(1000*c['lens_mm']/c['sensor_width_mm'])
   pix=np.stack([500+xy[:,0],350-xy[:,1]],1)
   for tri in np.array(p['indices']).reshape((-1,3)):draw.polygon([tuple(q)for q in pix[tri]],fill=1)
  a=np.asarray(mask,dtype=bool);edge=a^binary_erosion(a);dist=distance_transform_edt(~edge);ys,xs=np.nonzero(a);overlay=Image.open(v['reference_private_path']).convert('RGB');od=ImageDraw.Draw(overlay);ey,ex=np.nonzero(edge)
  for x,y in zip(ex,ey):od.point((int(x),int(y)),fill=(0,255,255))
  points=[]
  for k,p in ann['points'].items():
   if not k.startswith('seat_'):continue
   x,y=p['uv_px'];od.ellipse((x-2,y-2,x+2,y+2),fill=(255,0,255));points.append({'id':k,'uv_px':[x,y],'image_reading_plus_minus_px':p['reading_uncertainty_plus_minus_px'],'distance_to_candidate_silhouette_px':float(dist[y,x]),'kind':p['kind'],'not_a_physical_surface_distance':True})
  path=W/(v['id']+'-'+name+'-private-overlay.png');overlay.save(path)
  report['views'].append({'id':v['id'],'camera_case':name,'camera_is_calibrated':False,'candidate_projected_bbox_px':[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],'reference_pixels_not_public':True,'overlay_private_path':str(path),'overlay_sha256':sha(path),'points':points,'preexisting_guide_residuals':c['fit']['signed_residual_uv_px'],'limits':'Silhouette distance from rasterized actual GLB, includes unknown camera/section/depth and occlusion error. No threshold/pass; not correspondence to a physical point.'})
(O/'profile-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print([(v['id'],v['camera_case'],v['candidate_projected_bbox_px'],max(p['distance_to_candidate_silhouette_px']for p in v['points']))for v in report['views']])
