"""Read-only Blender inspection copies, not an installed assembly or receipt.

Append only named, already-evaluated inspection objects; never open/build/save the
historical scenes. Retain actual world positions and triangles privately for a
subsequent neutral interface study. Public output contains bounds and axial ray
stations, not photographic pixels or a new motorcycle component.
"""
from pathlib import Path
import hashlib, json, time
import bpy
import numpy as np

D=Path(__file__).resolve().parent
R=D.parents[2]
H=R/'assets-src/moto-components'
PRIVATE=Path('/workspace/wewa-assets/work-in-progress/front-wheel-interface-review-v1')
PRIVATE.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cases=[
 ('rim','front-rim/front-rim-v1.blend','front-rim/front-rim-inspection.glb','Front cast rim - inspection export',.29),
 ('panel','front-brake-plate/front-brake-plate-v2.blend','front-brake-plate/front-brake-plate-v2-inspection.glb','Front brake panel - inspection export',.29),
 ('fork-left','front-fork/outer-left/fork-outer-left-v1.blend','front-fork/outer-left/fork-outer-left-inspection.glb','LH fork outer body - relatedPF121018 candidate',0),
 ('fork-right','front-fork/outer-right/fork-outer-right-v1.blend','front-fork/outer-right/fork-outer-right-inspection.glb','RH fork outer body - relatedPF121019 candidate',0),
]

def stations(v,tri,y,z):
    # Two-sided Moller-Trumbore; x increases from -.20m. Coplanar/parallel
    # triangles are explicitly omitted, so this is a sampling diagnostic only.
    a=v[tri[:,0]];e1=v[tri[:,1]]-a;e2=v[tri[:,2]]-a
    direction=np.array([1.,0.,0.]);origin=np.array([-.20,y,z])
    h=np.cross(np.broadcast_to(direction,e2.shape),e2);det=np.einsum('ij,ij->i',e1,h)
    good=np.abs(det)>1e-16;inv=np.divide(1.,det,out=np.zeros_like(det),where=good)
    s=origin-a;u=inv*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1)
    w=inv*q[:,0];t=inv*np.einsum('ij,ij->i',e2,q)
    mask=good&(u>=-1e-8)&(w>=-1e-8)&(u+w<=1+1e-8)&(t>=0)&(t<=.4)
    hits=np.sort(t[mask]-.20)
    # Shared-edge duplicates are one surface station, not two contacts.
    unique=[]
    for x in hits:
        if not unique or x-unique[-1]>1e-6:unique.append(float(x))
    return {'y_m':y,'z_m':z,'x_surface_stations_m':unique,'raw_triangle_hits':int(mask.sum()),'merge_distance_m':1e-6}

report={'schema':1,'time_UTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
 'scope':'Read-only actual evaluated inspection geometry, not full editable masters, no pose/contact/clearance receipt. Source files and export buffers untouched.',
 'script_sha256':sha(Path(__file__)),'coordinate_system':'Native Blender world XYZ, unchanged. Wheel centre Z=.29; each isolated fork origin axlecentre Z=0.',
 'ray_method':'Two-sided Moller-Trumbore on actual triangles, +X from -.20 to +.20m; omit parallel/coplanar triangles, merge shared-edge stations within1micrometre. Sparse rays cannot certify all contacts or wall thickness.',
 'rows':[],'new_geometry_saved':False,'source_files_modified':False,'installed_pose_verified':False,'art_accepted':False}
for key,srel,grel,name,z0 in cases:
    source=H/srel;glb=H/grel;before=sha(source)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(str(source),link=False)as(available,loaded):
        assert name in available.objects,(name,list(available.objects))
        loaded.objects=[name]
    o=loaded.objects[0];bpy.context.scene.collection.objects.link(o)
    bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(deps)
    m=e.to_mesh(preserve_all_data_layers=True,depsgraph=deps);m.calc_loop_triangles()
    v=np.empty((len(m.vertices),3),dtype=np.float64);m.vertices.foreach_get('co',v.ravel())
    matrix=np.array(o.matrix_world,dtype=np.float64);v=v@matrix[:3,:3].T+matrix[:3,3]
    tri=np.empty((len(m.loop_triangles),3),dtype=np.int32);m.loop_triangles.foreach_get('vertices',tri.ravel())
    pv=PRIVATE/(key+'-inspection-native.npz');np.savez_compressed(pv,positions=v,triangles=tri)
    rays=[stations(v,tri,y,z0+z)for y,z in [(0,0),(.004,0),(.0063,0),(.0075,0),(.012,0),(.020,0),(.030,0),(.050,0),(.0645,0),(.070,0),(0,.010),(0,-.010)]]
    row={'key':key,'source':str(source.relative_to(R)),'source_sha256':before,'source_bytes':source.stat().st_size,
     'GLB':str(glb.relative_to(R)),'export_sha256':sha(glb),'export_bytes':glb.stat().st_size,
     'source_object':o.name,'object_world_matrix':matrix.tolist(),'source_object_modifiers':[{'name':q.name,'type':q.type}for q in o.modifiers],
     'inspection_vertices':len(v),'inspection_triangles':len(tri),'bounds_m':{'min':v.min(axis=0).tolist(),'max':v.max(axis=0).tolist()},
     'private_original_geometry_cache':str(pv),'cache_sha256':sha(pv),'axial_rays':rays,
     'source_SHA_unchanged_after_read':sha(source)==before,'source_vs_GLB_surface_comparison_performed':False}
    assert row['source_SHA_unchanged_after_read']
    e.to_mesh_clear();report['rows'].append(row);print('READ_ONLY_INTERFACE_EXTRACT',key,len(v),len(tri),flush=True)
    (D/'source-inspection-surface-read-v1.json').write_text(json.dumps(report,indent=2)+'\n')
print('READ_ONLY_INTERFACE_EXTRACTION_COMPLETE',flush=True)
