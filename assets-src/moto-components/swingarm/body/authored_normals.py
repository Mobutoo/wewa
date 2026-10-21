"""Source shading intent for actual native planes, using robust float64 geometry.
Sharing smooth fans inside a plane avoids tiny Newell-normal differences creating
isolated Mikk corners. Authored plane normals retain flat surfaces; curved loops
retain Blender's smooth-fan response. No tangent or export buffer is edited.
"""
import bpy,numpy as np

def author_normals(mesh,P):
 if mesh.has_custom_normals:bpy.ops.mesh.customdata_custom_splitnormals_clear()
 for face in mesh.polygons:face.use_smooth=True
 mesh.update();mesh.set_sharp_from_angle(angle=.55);mesh.update()
 coords=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',coords);coords=coords.reshape(-1,3).astype(np.float64);indices=np.empty(len(mesh.loops),dtype=np.int32);mesh.loops.foreach_get('vertex_index',indices);assert len(mesh.loops)==len(mesh.polygons)*3
 faces=coords[indices.reshape(-1,3)];fn=np.cross(faces[:,1]-faces[:,0],faces[:,2]-faces[:,0]);length=np.linalg.norm(fn,axis=1);assert np.all(length>0);fn/=length[:,None]
 slope=.007/P['working_body_rear_end_y_m_estimated'];centres=faces.mean(axis=1);longest=np.maximum.reduce([np.linalg.norm(faces[:,1]-faces[:,0],axis=1),np.linalg.norm(faces[:,2]-faces[:,0],axis=1),np.linalg.norm(faces[:,2]-faces[:,1],axis=1)]);condition=length/(longest*longest);seam_x=.103+slope*centres[:,1]-.012
 # These faces belong to the explicitly authored continuous U-to-rail weld sweep.
 # Float32 face-angle tests on sub-nm-high Boolean needles must not create a new
 # hard normal fan inside that continuous curved bead. Actual surface remains.
 weld_needle=(condition<1e-5)&(centres[:,1]>.109)&(centres[:,1]<.379)&(np.abs(np.abs(centres[:,0])-seam_x)<.0016)&((np.abs(centres[:,2]-.0118)<.001)|(np.abs(centres[:,2]-.0104)<.001))
 joined_ids=np.flatnonzero(weld_needle);joined_edges=[]
 if len(joined_ids):
  edge_indices=np.empty(len(mesh.loops),dtype=np.int32);mesh.loops.foreach_get('edge_index',edge_indices);sharp=mesh.attributes.get('sharp_edge');flags=np.zeros(len(mesh.edges),dtype=bool)
  if sharp:
   sharp.data.foreach_get('value',flags);joined_edges=np.unique(edge_indices[(3*joined_ids[:,None]+np.arange(3)).ravel()]);flags[joined_edges]=False;sharp.data.foreach_set('value',flags);mesh.update()
 normals=np.empty(len(mesh.loops)*3,dtype=np.float32);mesh.corner_normals.foreach_get('vector',normals);normals=normals.reshape(-1,3).astype(np.float64);planes=[]
 for axis,values in[(2,[.015,-.015,.0132,-.0132,.012,.0102]),(1,[-.008,.022,P['working_body_rear_end_y_m_estimated']-.0018,P['working_body_rear_end_y_m_estimated']])]:
  for value in values:
   n=np.zeros(3);n[axis]=1;planes.append((n,value))
 for sign in[-1,1]:
  for edge in[-.012,.012,-.0102,.0102]:planes.append((np.array([1,-sign*slope,0]),sign*.103+edge))
  for edge in[-.0125,.0125]:planes.append((np.array([1,0,0]),sign*.103+edge))
  for edge in[-1,1]:
   cx=sign*(.103+slope*.43)+edge*(.019/2+.0025/2)
   for side in[-1,1]:planes.append((np.array([1,0,0]),cx+side*.0025/2))
  for side in[-1,1]:planes.append((np.array([1,0,0]),sign*(.103+slope*.062)+side*.015))
 for side in[-1,1]:planes.append((np.array([1,0,0]),-(.103+slope*.482+.0105)+side*.0025/2))
 assigned=np.zeros(len(faces),dtype=bool);projection_normals=fn.copy();groups=[]
 for n,offset in planes:
  distances=np.einsum('ijk,k->ij',faces,n)-offset;unit=n/np.linalg.norm(n);agreement=np.einsum('ij,j->i',fn,unit);mask=(~assigned)&(np.max(np.abs(distances),axis=1)<=1e-7)&(np.abs(agreement)>.995)
  ids=np.flatnonzero(mask)
  if not len(ids):continue
  oriented=unit[None,:]*np.where(agreement[ids]>=0,1.,-1.)[:,None];projection_normals[ids]=oriented
  for corner in range(3):normals[3*ids+corner]=oriented
  assigned[ids]=True;groups.append({'normal':n.tolist(),'offset_m':offset,'triangles':len(ids)})
 mesh.normals_split_custom_set(normals.tolist());mesh.update()
 return projection_normals,{'method':'Known native planes with shared normal fans and authored planar loop normals, source only. Nonplanar loops preserve ordinary sharp-edge-constrained fan interpolation. Float64 cross products drive physical UV projection. No tangent repair.','numerical_plane_membership_tolerance_m':1e-7,'minimum_alignment_cosine':.995,'known_plane_groups':groups,'assigned_planar_triangles':int(assigned.sum()),'continuous_U_weld_ill_conditioned_faces_with_joined_normal_fans':joined_ids.tolist(),'edges_with_source_sharp_flag_cleared':list(map(int,joined_edges)),'weld_condition_ratio_threshold':1e-5,'geometry_modified':False}
