"""Read-only evaluated candidate surfaces: both-direction containment and overlap."""
from pathlib import Path
import bpy,json,hashlib,sys
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/exhaust-silencer-end-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=H/'exhaust-silencer-end-v1.blend';build=json.loads((H/'build-report.json').read_text());assert sha(source)==build['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));guides=bpy.data.collections['SILENCER_END_IMMUTABLE_GUIDES'];guides.hide_viewport=False;bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
exact_cache={}
def data(o):
 assert not o.modifiers, 'Retained evaluated source required'
 m=o.data;m.calc_loop_triangles();points=[o.matrix_world@v.co for v in m.vertices];faces=[tuple(t.vertices)for t in m.loop_triangles];tree=BVHTree.FromPolygons(points,faces,all_triangles=True);tri=np.asarray([[list(points[i])for i in face]for face in faces],dtype=np.float64);exact_cache[id(tree)]=(tri[:,0],tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);return points,tree
objects=[bpy.data.objects[x['name']]for x in build['geometry']];directions=[Vector(x).normalized()for x in [(1,.371,.129),(-.283,1,.417),(.191,-.313,1)]]
def parity(point,tree,d):
 origin=point.copy();distance=0.;hits=0
 for j in range(100):
  hit=tree.ray_cast(origin,d,1.)
  if hit[0]is None:return hits%2
  parameter=(hit[0]-point).dot(d)
  if parameter<=distance+1e-8:
   origin=point+d*(distance+1e-6);distance+=1e-6;continue
  hits+=1;distance=parameter;origin=point+d*(distance+1e-6)
 raise RuntimeError('Ray not terminated')
def double_ray_parity(point,direction,tree):
 # Direct float64 Moller-Trumbore intersection against all actual triangles.
 # No BVH advancement, sourcepositions unchanged; shared hits deduplicated.
 a,e1,e2=exact_cache[id(tree)];d=np.asarray(direction,dtype=np.float64);p=np.asarray(point,dtype=np.float64);h=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,h);area2=np.linalg.norm(np.cross(e1,e2),axis=1);valid=np.abs(det)>1e-12*area2;inv=np.zeros_like(det);inv[valid]=1/det[valid];delta=p-a;u=inv*np.einsum('ij,ij->i',delta,h);q=np.cross(delta,e1);v=inv*(q@d);t=inv*np.einsum('ij,ij->i',e2,q);hit=valid&(u>=-1e-12)&(v>=-1e-12)&(u+v<=1+1e-12)&(t>1e-9)
 if np.any(hit&((np.minimum(np.minimum(u,v),1-u-v))<1e-10)):return None
 distances=np.sort(t[hit]);count=0;last=-1.
 for value in distances:
  if count==0 or value-last>1e-9:count+=1;last=value
 return count%2

def classify(points,tree):
 inside=[];ambiguous=[];boundary=[];minimum=1.;fallbacks=[]
 for index,point in enumerate(points):
  near=tree.find_nearest(point);dist=near[3];minimum=min(minimum,dist)
  if dist<=1e-7:boundary.append(index);continue
  values=[parity(point,tree,d)for d in directions]
  if len(set(values))!=1:
   previous=values;values=[double_ray_parity(point,d,tree)for d in directions];fallbacks.append({'vertex':index,'world_point_m':list(point),'BVH_parities':previous,'direct_float64_parities':values})
  if None in values or len(set(values))!=1:ambiguous.append({'vertex':index,'parities':values})
  elif values[0]:inside.append(index)
 return {'direct_float64_fallbacks':fallbacks,'sampled_vertices':len(points),'inside':inside,'ambiguous':ambiguous,'boundary_100nm':boundary,'sampled_vertex_nearest_distance_m':minimum}
rows=[];guideobjects=[o for o in guides.all_objects if o.type=='MESH'];pairs=[(o,g)for o in objects for g in guideobjects]+[(a,b)for i,a in enumerate(objects)for b in objects[i+1:]]
cache={o.name:data(o)for o in objects+guideobjects}
for a,b in pairs:
 ap,at=cache[a.name];bp,bt=cache[b.name];rows.append({'a':a.name,'b':b.name,'surface_pairs':len(at.overlap(bt)),'a_vertices_in_b':classify(ap,bt),'b_vertices_in_a':classify(bp,at)})
report={'component_id':build['component_id'],'source_sha256':sha(source),'export_sha256':build['export_sha256'],'pairs':rows,'scope':'Actual candidate meshes. Vertex containment is sampled, not proof of an exact minimum clearance or real fit. Three parity directions must agree. BVH disagreements require unanimous direct float64 triangle checks with explicit logged values, no majority or mesh mutation.','all_dimensions_estimated':True,'art_accepted':False};(O/'interface-solid-check.json').write_text(json.dumps(report,indent=2)+'\n')
for row in rows:
 assert row['surface_pairs']==0,row
 for key in ['a_vertices_in_b','b_vertices_in_a']:
  assert not any(row[key][k]for k in ['inside','ambiguous','boundary_100nm']),row
assert sha(source)==build['source_sha256'];print('SILENCER_END_INTERFACE',json.dumps(report))
