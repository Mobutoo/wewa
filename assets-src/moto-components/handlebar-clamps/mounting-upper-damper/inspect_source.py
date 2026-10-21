"""Read-only geometry-normal/portability and nonadjacent BVH witness, no fit claim."""
import bpy,json,hashlib,numpy as np,sys,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/handlebar-mount-upper-damper-v1';sys.path.insert(0,str(H));from profile_shape import profile
P=json.loads((H/'parameters.json').read_text());src=H/'handlebar-mount-upper-damper-v1.blend';glb=H/'handlebar-mount-upper-damper-inspection.glb';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src));o=list(bpy.data.collections[P['collection']].objects)[0];assert not o.modifiers;m=o.data;m.calc_loop_triangles();h=hashlib.sha256()
for c,p,n,dt in[(m.vertices,'co',3,np.float32),(m.loops,'vertex_index',1,np.int32),(m.corner_normals,'vector',3,np.float32),(m.uv_layers.active.data,'uv',2,np.float32)]:
 a=np.empty(len(c)*n,dt);c.foreach_get(p,a);h.update(a.tobytes())
rows=profile(P);N=P['radial_segments'];errors=[];flat=[]
for p in m.polygons:
 for li in p.loop_indices:
  vi=m.loops[li].vertex_index;i,j=divmod(vi,N);rad,z,nr,nz,tag=rows[i];a=math.tau*j/N;expected=Vector((nr*math.cos(a),nr*math.sin(a),nz))if p.use_smooth else p.normal;actual=m.corner_normals[li].vector;errors.append((actual-expected).length)
  if not p.use_smooth:flat.append(max(abs(actual.x),abs(actual.y)))
assert max(errors)<.001
verts=[v.co for v in m.vertices];faces=[tuple(t.vertices)for t in m.loop_triangles];sets=[set(f)for f in faces];a=BVHTree.FromPolygons(verts,faces,all_triangles=True);b=BVHTree.FromPolygons(verts,faces,all_triangles=True);pairs=a.overlap(b);kept=[(x,y)for x,y in pairs if x<y and not sets[x].intersection(sets[y])];w1=BVHTree.FromPolygons([(-1,-1,0),(1,-1,0),(0,1,0)],[(0,1,2)],all_triangles=True);w2=BVHTree.FromPolygons([(0,-.5,-1),(0,-.5,1),(0,.5,0)],[(0,1,2)],all_triangles=True);w3=BVHTree.FromPolygons([(-1,-1,0),(1,-1,0),(0,1,0)],[(0,1,2)],all_triangles=True);witness={'known_noncoplanar_crossings':len(w1.overlap(w2)),'coincident_coplanar_pairs_returned':len(w1.overlap(w3))};assert not kept and witness['known_noncoplanar_crossings']>0
libs=[x.filepath for x in bpy.data.libraries];ims=[{'name':x.name,'filepath':x.filepath,'packed':bool(x.packed_file),'relative_companion_exists':(H/x.filepath[2:]).is_file()if x.filepath.startswith('//')else False}for x in bpy.data.images if x.source=='FILE'];assert not libs and all(x['packed']and x['relative_companion_exists']for x in ims)
r={'source_sha256':sha(src),'export_sha256':sha(glb),'actual_source_vertex_loop_normal_UV_digest':h.hexdigest(),'fresh_analytic_profile_normal_maximum_stored_vector_error':max(errors),'normal_error_scope':'Actual stored corner normal versus analytic profile or actual geometric flat face. Encoding precision diagnostic, not OEM/physical tolerance.','actual_flat_loops':len(flat),'maximum_flat_corner_transverse_component':max(flat),'nonadjacent_noncoplanar_crossings':len(kept),'BVH_algorithm_witness':witness,'BVH_scope':'Actual triangles; sharedvertex adjacency excluded. Coincident coplanar or adjacentfold overlap NOT certified. No source mutation.','external_libraries':libs,'images':ims,'packed_relative_companion_files_verified':all(x['packed']and x['relative_companion_exists']for x in ims),'unseen_reverse_or_installed_contacts_qualified':False,'art_accepted':False};(O/'source-inspection-check.json').write_text(json.dumps(r,indent=2)+'\n');print('UPPER_DAMPER_SOURCE_INSPECTION',json.dumps(r))
