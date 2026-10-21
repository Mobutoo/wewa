"""Read actual GLB section against author's estimated runout function; no edits."""
import json,struct,hashlib,math
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'creative/reviews/handlebar-mount-nyloc-v3/lower-entry-diagnostic';OUT.mkdir(exist_ok=True);path=HERE/'handlebar-mount-nyloc-v3-inspection.glb';data=path.read_bytes();jlen,_=struct.unpack_from('<II',data,12);d=json.loads(data[20:20+jlen]);binary=data[20+jlen+8:]
def accessor(index):
 a=d['accessors'][index];v=d['bufferViews'][a['bufferView']];dtype={5126:'<f4',5125:'<u4',5123:'<u2'}[a['componentType']];count={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];size=np.dtype(dtype).itemsize;return np.ndarray((a['count'],count),dtype=dtype,buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',size*count),size)).astype(float)
def radial(z,a):
 phase=(z/.0015-a/math.tau)%1;f=0 if phase<.125 else(phase-.125)/.3125 if phase<.4375 else 1 if phase<.5625 else(.875-phase)/.3125 if phase<.875 else 0;minor=.00506-5*math.sqrt(3)*.0015/16;nominal=minor+(.00506-minor)*f;ease=max(0,min(1,(z-.00035)/.00055,(.0069-z)/.00055));return nominal*ease+.0052*(1-ease)
rows=[]
for plane in[.0009,.00095,.0010,.00635]:
 points={};crossing=0
 for primitive in d['meshes'][0]['primitives']:
  p=accessor(primitive['attributes']['POSITION']);tri=p[accessor(primitive['indices']).astype(int).ravel()].reshape((-1,3,3));r=np.linalg.norm(tri[:,:,[0,2]],axis=2);chosen=tri[(tri[:,:,1].min(1)<plane)&(tri[:,:,1].max(1)>plane)&(r.max(1)<.00531)]
  crossing+=len(chosen)
  for t in chosen:
   for i in range(3):
    a,b=t[i],t[(i+1)%3]
    if(a[1]-plane)*(b[1]-plane)>=0:continue
    q=a+(b-a)*(plane-a[1])/(b[1]-a[1]);angle=math.atan2(-q[2],q[0]);radius=math.hypot(q[0],q[2]);error=radius-radial(plane,angle);points[tuple(np.round(q,12))]=(angle,error)
 vals=list(points.values());errors=[v[1]for v in vals];rows.append({'source_axial_plane_m':plane,'actual_crossing_triangles':crossing,'unique_section_points':len(vals),'radial_difference_from_author_function_um':[min(errors)*1e6,max(errors)*1e6],'samples_angle_radians_radial_difference_m':sorted(vals)})
r={'export_sha256':hashlib.sha256(data).hexdigest(),'source_sha256':hashlib.sha256((HERE/'handlebar-mount-nyloc-v3.blend').read_bytes()).hexdigest(),'GLB_buffers_modified':False,'comparison':'Actual piecewise-linear exported surface vs author radial function, not against a measured OEM surface','runout_mesh_grid':'Helicalphase-aligned rows with explicit source cuts at both unchanged axial fade derivative knots','plane_sections':rows,'art_accepted':False};(OUT/'runout-plane-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({**r,'plane_sections':[{k:v for k,v in q.items()if not k.startswith('samples_')}for q in rows]},indent=2))
