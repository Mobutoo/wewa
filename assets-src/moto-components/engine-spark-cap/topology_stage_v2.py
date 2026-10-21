"""Retessellate one 11nm-height CSG needle, never repair a tangent buffer."""
from pathlib import Path
import bpy,bmesh,json,hashlib,sys,math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-spark-cap-v2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
g=json.loads((H/'geometry-report-v2.json').read_text());src=H/'engine-spark-cap-v2-geometry.blend'
assert sha(src)==g['geometry_source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(src))
sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import check_mesh,export
o=bpy.data.objects[g['geometry'][0]['name']];contact=bpy.data.objects[g['geometry'][1]['name']];datum=o.parent
original=o.data.copy();original.calc_loop_triangles();verts=[v.co.copy()for v in original.vertices]
def faces(m):return {tuple(sorted(p.vertices)):tuple(p.vertices) for p in m.polygons}
def tree(m):return BVHTree.FromPolygons([v.co for v in m.vertices],[tuple(f.vertices)for f in m.polygons],all_triangles=True)
def samples(m,subset,n=32):
    result=[]
    for ids in subset:
        a,b,c=[np.asarray(m.vertices[i].co,dtype=np.float64)for i in ids]
        for j in range(n+1):
            for k in range(n+1-j):result.append(a+(b-a)*(j/n)+(c-a)*(k/n))
    return result
def direct_distance(p,m,subset):
    best=float('inf')
    for ids in subset:
        a,b,c=[np.asarray(m.vertices[i].co,dtype=np.float64)for i in ids]
        normal=np.cross(b-a,c-a);normal/=np.linalg.norm(normal)
        signed=np.dot(p-a,normal);q=p-normal*signed
        if min(np.dot(np.cross(v-u,q-u),normal)for u,v in [(a,b),(b,c),(c,a)])>=-1e-24:
            best=min(best,abs(signed))
        for u,v in [(a,b),(b,c),(c,a)]:
            t=np.clip(np.dot(p-u,v-u)/np.dot(v-u,v-u),0.,1.)
            best=min(best,float(np.linalg.norm(p-u-t*(v-u))))
    return best
oldfaces=faces(original);oldtree=tree(original);trials=[];meshes=[]
for ids in [(16844,16845),(16845,21569),(21569,16844)]:
    m=original.copy();bm=bmesh.new();bm.from_mesh(m);bm.verts.ensure_lookup_table()
    edge=next(e for e in bm.edges if {v.index for v in e.verts}==set(ids))
    before_faces=[f.index for f in edge.link_faces];bmesh.ops.rotate_edges(bm,edges=[edge],use_ccw=False)
    bm.normal_update();bm.to_mesh(m);bm.free();m.update();newfaces=faces(m)
    removed=[v for k,v in oldfaces.items()if k not in newfaces];added=[v for k,v in newfaces.items()if k not in oldfaces]
    assert len(removed)==len(added)==2
    assert verts==[v.co.copy()for v in m.vertices], 'Vertex moved'
    newtree=tree(m);oldpoints=samples(original,removed);newpoints=samples(m,added)
    d1=max(direct_distance(v,m,added)for v in oldpoints);d2=max(direct_distance(v,original,removed)for v in newpoints)
    row={'old_edge_vertex_indices':ids,'old_face_indices':before_faces,'removed_triangles':removed,'new_triangles':added,
         'all_vertex_positions_bit_identical':True,'old_to_new_surface_sample_max_m':d1,'new_to_old_surface_sample_max_m':d2,
         'distance_method':'Direct float64 point-to-two-triangle distance, plane inclusion and clamped edge projections; float32 BVH nearest is unstable on this needle and is not used as a metrology result. Sampled bound only.', 'samples_each_direction':len(oldpoints),'subdivision_per_triangle':32,'source_topology_operation':'one BMesh diagonal rotation; no deletion, weld, displacement or normal/tangent repair'}
    trials.append(row);meshes.append(m)
index=min(range(len(trials)),key=lambda i:max(trials[i]['old_to_new_surface_sample_max_m'],trials[i]['new_to_old_surface_sample_max_m']))
print('TRIALS',json.dumps(trials),flush=True);o.data=meshes[index];chosen=trials[index];assert max(chosen[k]for k in ['old_to_new_surface_sample_max_m','new_to_old_surface_sample_max_m'])<1e-7
for f in o.data.polygons:f.use_smooth=True
o.data.update();geometry=[check_mesh(v)for v in [o,contact]]
assert not any(x['non_manifold_edges']or x['connected_shells']!=1 for x in geometry)
dest=H/'engine-spark-cap-v2-topology.blend';glb=H/'engine-spark-cap-v2-topology.glb'
export(glb,[datum,o,contact]);bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
report={**g,'geometry_source_sha256':sha(dest),'geometry_export_sha256':sha(glb),'geometry':geometry,
        'parent_geometry_source_sha256':g['geometry_source_sha256'],'topology_trials':trials,'chosen_topology_trial':index,
        'vertex_count_preserved':len(o.data.vertices)==len(original.vertices),'material_bake_pending':True,
        'tangent_buffers_repaired':False,'reason':'Original CSG needle height ~11nm creates a zero native tangent at its acute tip. Bounded diagonal rotation in source retains every vertex and removes the needle before UV authoring and baking.'}
(H/'topology-report-v2.json').write_text(json.dumps(report,indent=2)+'\n');(O/'source-topology-refinement.json').write_text(json.dumps(report,indent=2)+'\n')
assert sha(src)==g['geometry_source_sha256'];print('CAP2_TOPOLOGY',index,chosen,sha(dest),sha(glb))
