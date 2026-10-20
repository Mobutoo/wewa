"""Read the saved source and inspect its evaluated casting and reduction."""
import hashlib,json,math
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
bpy.ops.wm.open_mainfile(filepath=str(HERE/'front-rim-v1.blend'))
deps=bpy.context.evaluated_depsgraph_get()
obj=bpy.data.objects['Cast rim - closed bead and drop-centre section']
reduced=bpy.data.objects['Front cast rim - inspection export']
evaluated=obj.evaluated_get(deps);mesh=evaluated.to_mesh();bm=bmesh.new();bm.from_mesh(mesh)
components=0;unseen=set(bm.verts)
while unseen:
 components+=1;pending=[unseen.pop()]
 while pending:
  v=pending.pop()
  for e in v.link_edges:
   other=e.other_vert(v)
   if other in unseen:unseen.remove(other);pending.append(other)
bvh=BVHTree.FromObject(reduced,deps)
distances=[]
for i in range(0,len(mesh.vertices),max(1,len(mesh.vertices)//10000)):
 nearest=bvh.find_nearest(mesh.vertices[i].co)
 if nearest[0] is not None:distances.append(nearest[3])
distances.sort()
points=[obj.matrix_world@v.co for v in mesh.vertices]
bounds={'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)]}
tyre=HERE.parent/'front-tyre/front-tyre-v1.blend'
report={'scope':'Saved editable source, actual evaluated casting; sparse directional reduction distance is not a full Hausdorff or photo-fidelity test','source':str((HERE/'front-rim-v1.blend').relative_to(ROOT)),'source_sha256':hashlib.sha256((HERE/'front-rim-v1.blend').read_bytes()).hexdigest(),'source_vertices':len(bm.verts),'source_faces':len(bm.faces),'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'connected_casting_shells':components,'signed_volume_m3':bm.calc_volume(signed=True),'bounds_blender_xyz_m':bounds,'reduction_sample_count':len(distances),'source_vertex_to_reduced_surface_distance_m':{'mean':sum(distances)/len(distances),'p95':distances[int(.95*(len(distances)-1))],'max':max(distances)},'linked_tyre':{'relative_path':'../front-tyre/front-tyre-v1.blend','exists':tyre.exists(),'sha256':hashlib.sha256(tyre.read_bytes()).hexdigest()},'photo_cameras_calibrated':False,'art_accepted':False}
report['evaluated_material_faces']={m.name:sum(p.material_index==i for p in mesh.polygons) for i,m in enumerate(mesh.materials)}
assert report['evaluated_material_faces'].get('Machined drum and bearing seat',0)>0,report
assert report['non_manifold_edges']==0 and components==1 and report['signed_volume_m3']>0,report
assert max(distances)<.0015,report
(ROOT/'creative/reviews/front-rim-v1/source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n')
bm.free();evaluated.to_mesh_clear();print('WEWA_RIM_SOURCE_CHECK',json.dumps(report))
