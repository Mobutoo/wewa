"""Original finite-wall tube; physical side mouths cut in author geometry, not GLB.
Run host Python before build.py. Manifold is a construction operation only.
All dimensions are working estimates; separate terminal plates remain unbuilt.
"""
from pathlib import Path
import math,json,hashlib
import numpy as np
import manifold3d as md
H=Path(__file__).resolve().parent;P=json.loads((H/'parameters.json').read_text())
raw=np.array(P['construction_polyline_m'],float);pieces=[];cursor=raw[0];offset=0.
def add(kind,a,b,**kwargs):
 global offset
 length=float(np.linalg.norm(b-a)) if kind=='line' else kwargs['radius']*kwargs['angle']
 pieces.append(dict(kind=kind,a=a.tolist(),b=b.tolist(),length=length,s0=offset,**kwargs));offset+=length
for i in range(1,len(raw)-1):
 a,b,c=raw[i-1:i+2];u=(b-a)/np.linalg.norm(b-a);v=(c-b)/np.linalg.norm(c-b);theta=math.acos(np.clip(u@v,-1,1));radius=P['bend_radii_m'][i-1];t=radius*math.tan(theta/2)
 assert t<min(np.linalg.norm(b-a),np.linalg.norm(c-b)),(i,t)
 start=b-u*t;end=b+v*t;axis=np.cross(u,v);axis/=np.linalg.norm(axis);n=np.cross(axis,u);centre=start+n*radius
 assert (start-cursor)@u>=-1e-9,'Adjacent bend tangent lengths overlap'
 if np.linalg.norm(cursor-start)>1e-9:add('line',cursor,start)
 add('arc',start,end,centre=centre.tolist(),axis=axis.tolist(),radius=radius,angle=theta)
 cursor=end
add('line',cursor,raw[-1]);path=[];tangent=[];ss=[]
def rotate(v,k,a):return v*math.cos(a)+np.cross(k,v)*math.sin(a)+k*(k@v)*(1-math.cos(a))
for q in pieces:
 steps=max(1,math.ceil(q['length']/P['source_step_m']));a=np.array(q['a']);b=np.array(q['b'])
 for j in range(steps):
  t=j/steps
  if q['kind']=='line':x=a+(b-a)*t;d=(b-a)/np.linalg.norm(b-a)
  else:
   k=np.array(q['axis']);r=rotate(a-np.array(q['centre']),k,q['angle']*t);x=np.array(q['centre'])+r;d=np.cross(k,r);d/=np.linalg.norm(d)
  path.append(x);tangent.append(d);ss.append(q['s0']+q['length']*t)
path.append(raw[-1]);tangent.append((raw[-1]-np.array(pieces[-1]['a']))/pieces[-1]['length']);ss.append(offset)
path=np.array(path);tangent=np.array(tangent);ss=np.array(ss);N=P['radial_segments'];M=len(path);ro=P['tube_outer_radius_m'];ri=ro-P['tube_wall_m'];Y=np.array([0.,1.,0.]);B=np.cross(tangent,Y)
verts=[]
for radius in [ro,ri]:
 for x,b in zip(path,B):
  for j in range(N):verts.append(x+radius*(Y*math.cos(math.tau*j/N)+b*math.sin(math.tau*j/N)))
faces=[]
for layer in range(2):
 off=layer*M*N
 for i in range(M-1):
  for j in range(N):
   a=off+i*N+j;b=off+i*N+(j+1)%N;c=off+(i+1)*N+(j+1)%N;d=off+(i+1)*N+j
   fs=[(a,b,c),(a,c,d)];faces.extend(fs if layer==0 else [f[::-1]for f in fs])
for i in [0,M-1]:
 for j in range(N):
  a=i*N+j;b=i*N+(j+1)%N;c=M*N+i*N+(j+1)%N;d=M*N+i*N+j;fs=[(a,c,b),(a,d,c)]
  faces.extend(fs if i==0 else [f[::-1]for f in fs])
V=np.array(verts,np.float32);F=np.array(faces,np.uint32)
volume=np.einsum('ij,ij->i',V[F[:,0]].astype(float),np.cross(V[F[:,1]].astype(float),V[F[:,2]].astype(float))).sum()/6
if volume<0:F=F[:,::-1].copy()
body=md.Manifold(md.Mesh(V,F));assert str(body.status())=='Error.NoError',body.status();before=body.volume();holes=[]
for point in P['side_hole_centres_m']:
 # Half-sector cutter phase avoids coincident cut vertices on the tube seam.
 # Radius, axis and centre are unchanged; no exported mesh cleanup or displacement.
 centre=np.array(point);cutter=md.Manifold.cylinder(P['side_hole_cutter_length_m'],P['side_hole_radius_m'],circular_segments=P['hole_segments'],center=True).rotate([90,0,0]).rotate([0,180/P['hole_segments'],0]).translate(centre.tolist());body=body-cutter;holes.append({'centre_m':point,'axis':[0,1,0],'radius_m_estimated':P['side_hole_radius_m'],'cutter_sector_phase_deg':180/P['hole_segments'],'opens_only_observed_near_wall':True,'hidden_opposite_wall_punch_not_created':True})
assert str(body.status())=='Error.NoError' and body.volume()>0,body.status();m=body.to_mesh();V=np.array(m.vert_properties[:,:3],np.float32);F=np.array(m.tri_verts,np.uint32);area=np.linalg.norm(np.cross(V[F[:,1]].astype(float)-V[F[:,0]],V[F[:,2]].astype(float)-V[F[:,0]]),axis=1)/2;assert area.min()>1e-15,float(area.min())
np.savez_compressed(H/'author-tube-geometry.npz',positions=V,triangles=F)
r={'component_id':P['component_id'],'revision':P['revision'],'source_parameters_sha256':hashlib.sha256((H/'parameters.json').read_bytes()).hexdigest(),'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'author_mesh_sha256':hashlib.sha256((H/'author-tube-geometry.npz').read_bytes()).hexdigest(),'original_centreline_pieces':pieces,'centreline_length_m_estimated':offset,'sample_count':M,'radial_segments':N,'side_mouths':holes,'volume_before_holes_m3':before,'volume_after_holes_m3':body.volume(),'triangles':len(F),'vertices':len(V),'minimum_triangle_area_m2':float(area.min()),'planar_centreline_working_estimate':True,'external_photo_or_mesh_used':False,'all_metric_parameters_estimated':True,'terminal_plates_notbuilt':True,'centralplate_notbuilt':True,'protective_strength_qualified':False,'art_accepted':False};(H/'author-tube-generation.json').write_text(json.dumps(r,indent=2)+'\n');print('HOOP_TUBE_AUTHOR',len(V),len(F),area.min(),body.volume())
