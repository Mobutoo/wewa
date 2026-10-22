"""Use the source cover's actual open lower boundary, not its top skin ray hits, for pan pose trials."""
import bpy,json,math,collections,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix,kdtree
R=Path(__file__).resolve().parents[1];O=R/'creative/research/seat-pan-context-correction-v1';O.mkdir(parents=True,exist_ok=True);s=bpy.data.objects['Seat outer upholstered envelope - estimated'];me=s.data;uses=collections.Counter(tuple(sorted(e))for p in me.polygons for e in p.edge_keys);ids=sorted({i for e,n in uses.items()if n==1 for i in e});assert ids,'No open boundary: inspect source topology';B=[s.matrix_world@me.vertices[i].co for i in ids];kd=kdtree.KDTree(len(B))
for i,v in enumerate(B):kd.insert(Vector((v.x,v.y,0)),i)
kd.balance()
p=R/'assets-src/moto-components/seat-base-observed-underside-v2/seat-base-observed-underside-v2.blend'
with bpy.data.libraries.load(str(p),link=True)as(a,b):b.collections=['WEWA_SEAT_BASE_OBSERVED_UNDERSIDE_V2']
ob=next(x for x in b.collections[0].all_objects if x.type=='MESH');V=[ob.matrix_world@v.co for v in ob.data.vertices];nx=240;ny=600;sample=[V[j*(nx+1)+i]for j in range(0,ny+1,20)for i in [0,nx]]+[V[j*(nx+1)+i]for j in [0,ny]for i in range(0,nx+1,20)];trials=[]
for scale in [1,.98,.95,.92,.9,.88]:
 for cy in [.64,.65,.66,.67,.68,.69,.7,.71]:
  for deg in [-5,0,3,6,9,12,15]:
   A=Matrix.Rotation(math.radians(deg),4,'X')@Matrix.Rotation(math.pi,4,'Y')@Matrix.Scale(scale,4);pts=[A@v for v in sample];diff=[];xy=[]
   for v in pts:
    _,i,dist=kd.find(Vector((v.x,v.y+cy,0)));diff.append(B[i].z-v.z);xy.append(dist)
   z=float(np.mean(diff)-.002);e=np.array(diff)-z;cost=float(np.mean(np.array(xy)**2)+np.mean(e**2)*2)
   trials.append(dict(scale=scale,translation=[0,cy,z],rotation_x_degrees=deg,boundary_xy_distance_mean=float(np.mean(xy)),boundary_xy_distance_max=float(max(xy)),boundary_z_gap_min=float(min(e)),boundary_z_gap_max=float(max(e)),boundary_z_gap_rms=float(np.sqrt(np.mean(e**2))),score=cost))
trials.sort(key=lambda t:t['score']);(O/'lower-boundary-pose-trials.json').write_text(json.dumps(dict(scope='Actual source upholstered outer skin has an open lower boundary; prior upward ray hits were upper skin and invalid for underside fitting. Only lower boundary used here.',boundary_vertices=len(B),boundary_native=[list(v)for v in B[::max(1,len(B)//60)]],candidates=trials[:40],source_geometry_unchanged=True,art_accepted=False),indent=2)+'\n');print('BOUNDARY_BEST',json.dumps(trials[:3]))
