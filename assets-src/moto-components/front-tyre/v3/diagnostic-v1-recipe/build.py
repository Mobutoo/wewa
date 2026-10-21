"""Local source correction and conforming sampled-error refinement only.

All original vertices are retained. Outside the overlap their coordinates stay
bit-identical; unrelated profile/bead/sidewall and bounds are protected. No
voxel remesh, no old asset save, no GLB buffer repair, no stale normal atlas.
"""
from pathlib import Path
import bpy,bmesh,json,hashlib,sys,math
import numpy as np
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/front-tyre-v3';O.mkdir(exist_ok=True)
sys.path.insert(0,str(H));from junction_field import JunctionField
P=json.loads((H/'parameters.json').read_text());F=JunctionField(P);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
diagnostic_after=next((int(a.split('=',1)[1])for a in sys.argv if a.startswith('--diagnostic-save-after=')),None)
asset_stem='front-tyre-v3-junction-diagnostic-v1'if diagnostic_after is not None else'front-tyre-v3'
source=R/P['original_geometry_source'];assert sha(source)==P['source_sha256']
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
col=bpy.data.collections.new(P['collection']);s.collection.children.link(col)
with bpy.data.libraries.load(str(source),link=False)as(a,b):b.objects=[P['original_inspection_object']]
o=b.objects[0];col.objects.link(o);o.hide_set(False);o.hide_render=False;m=o.data;m.calc_loop_triangles()
assert not o.modifiers and np.array_equal(np.array(o.matrix_world),np.eye(4))and len(m.uv_layers)==1
def array(c,key,n,dtype):
    a=np.empty(len(c)*n,dtype);c.foreach_get(key,a);return a.reshape(-1,n)if n>1 else a
V=array(m.vertices,'co',3,np.float32);I=array(m.loop_triangles,'vertices',3,np.int32);loops=array(m.loop_triangles,'loops',3,np.int32)
UV=array(m.uv_layers[0].data,'uv',2,np.float32)[loops];NN=array(m.corner_normals,'vector',3,np.float32)[loops]
initial_V=V.copy();initial_I=I.copy();initial_UV=UV.copy();initial_NN=NN.copy();initial_count=len(V);uvname=m.uv_layers[0].name
def coords(v):
    x=v[:,0].astype(np.float64);y=v[:,1].astype(np.float64);z=v[:,2].astype(np.float64)-.29
    return x,np.hypot(y,z),np.arctan2(y,z)*F.R
outer_corner=(UV[:,:,1]<5/30)|(UV[:,:,1]>25/30)
outer=np.zeros(len(V),bool);outer[I[outer_corner]]=True
x,r,arc=coords(V);a,b,d=F.fields(x,arc);delta=F.depth(x,arc)-F.depth(x,arc,False)
changed=outer&(delta>1e-12);assert np.all(F.support(x[changed],arc[changed]))
old_consistency=np.abs(r[outer&F.support(x,arc)]-F.crown(x[outer&F.support(x,arc)],arc[outer&F.support(x,arc)],False))
assert old_consistency.max()<2e-7,('Legacy field does not reproduce inspection',old_consistency.max())
newr=r[changed]-delta[changed];theta=arc[changed]/F.R
V[changed,1]=(newr*np.sin(theta)).astype(np.float32);V[changed,2]=(.29+newr*np.cos(theta)).astype(np.float32)
assert np.array_equal(V[~changed],initial_V[~changed])and np.array_equal(V[:,0],initial_V[:,0])
assert delta[changed].max()<=P['junction_extra_depth_bound_m']+1e-12

def normals(v,old,eligible):
    x,_,arc=coords(v);w=F.normal_weight(x,arc)*eligible
    out=old.astype(np.float64).copy();ids=np.flatnonzero(w>0)
    out[ids]=out[ids]*(1-w[ids,None])+F.normal(x[ids],arc[ids])*w[ids,None]
    out[ids]/=np.linalg.norm(out[ids],axis=1)[:,None]
    return out.astype(np.float32)
# B is the fixed piecewise-linear reference after the bounded old-vertex union
# correction. Its midpoint interpolation never projects to the new field. A C1
# gate against this reference avoids a geometric jump at the repair-band edge.
B=V.astype(np.float64).copy()
def target_position(base):
    x,r,arc=coords(base);weight=F.normal_weight(x,arc);out=base.copy();ids=np.flatnonzero(weight>0)
    target=F.crown(x[ids],arc[ids]);rr=r[ids]+weight[ids]*(target-r[ids]);theta=arc[ids]/F.R
    out[ids,1]=rr*np.sin(theta);out[ids,2]=.29+rr*np.cos(theta)
    return out
history=[]
macro_eye=np.array([.075,-.17,.69]);macro_target=np.array([.012,-.10,.562]);macro_scale=.05
macro_rotation=np.array((Vector(macro_target)-Vector(macro_eye)).to_track_quat('-Z','Y').to_matrix())
def project_macro(points):
    local=(points-macro_eye)@macro_rotation
    return np.stack([(.5+local[...,0]/macro_scale)*1400,(.5+local[...,1]/(macro_scale*1100/1400))*1100,-local[...,2]],axis=-1)
def sample():
    outer_faces=((UV[:,:,1]<5/30)|(UV[:,:,1]>25/30)).all(1)
    xx,_,aa=coords(V);candidate=np.flatnonzero(outer_faces&F.support(xx,aa)[I].any(1))
    tri=V[I[candidate]].astype(np.float64);reference=B[I[candidate]];errors=[]
    for weights in[(1/3,1/3,1/3),(.5,.5,0),(0,.5,.5),(.5,0,.5)]:
        q=sum(tri[:,j]*w for j,w in enumerate(weights));base=sum(reference[:,j]*w for j,w in enumerate(weights))
        errors.append(np.linalg.norm(target_position(base)-q,axis=1))
    errors=np.array(errors);bad=candidate[errors.max(0)>P['sampled_refinement_goal_m']]
    sample_id,local_face=np.unravel_index(np.argmax(errors),errors.shape);fi=int(candidate[local_face]);vertices=V[I[fi]].astype(np.float64);baseline=B[I[fi]]
    diagnostic={'iteration':len(history),'sample_id':int(sample_id),'triangle_index':fi,'vertex_indices':I[fi].tolist(),
      'V':vertices.tolist(),'B':baseline.tolist(),'target_of_B_corners':target_position(baseline).tolist(),
      'corner_target_mismatch_m':np.linalg.norm(target_position(baseline)-vertices,axis=1).tolist(),
      'edge_lengths_m':[float(np.linalg.norm(vertices[j]-vertices[(j+1)%3]))for j in range(3)],'UV':UV[fi].tolist()}
    # Select an actually projected macro witness, rather than citing only the
    # global maximum on the far side of the tyre.
    bary=np.array([(1/3,1/3,1/3),(.5,.5,0),(0,.5,.5),(.5,0,.5)])
    choices=errors.argmax(0);weights=bary[choices]
    q=(tri*weights[:,:,None]).sum(1);base=(reference*weights[:,:,None]).sum(1);wanted=target_position(base)
    pixels=project_macro(q);visible=(pixels[:,0]>=0)&(pixels[:,0]<=1400)&(pixels[:,1]>=0)&(pixels[:,1]<=1100)&(pixels[:,2]>.001)
    if visible.any():
        selected=np.flatnonzero(visible);k=selected[np.argmax(errors.max(0)[selected])];face=int(candidate[k])
        uvpixels=project_macro(V[I[face]]);qp=project_macro(q[k:k+1])[0];wp=project_macro(wanted[k:k+1])[0]
        diagnostic['visible_macro_witness']={'triangle_index':face,'vertex_indices':I[face].tolist(),'vertices_m':V[I[face]].tolist(),
          'camera_eye_m':macro_eye.tolist(),'camera_target_m':macro_target.tolist(),'ortho_scale_m':macro_scale,'resolution_px':[1400,1100],
          'vertices_projected_xy_pixels':uvpixels[:,:2].tolist(),'projected_triangle_extent_px':np.ptp(uvpixels[:,:2],axis=0).tolist(),
          'actual_mesh_sample_m':q[k].tolist(),'target_sample_m':wanted[k].tolist(),'sample_deviation_m':float(errors.max(0)[k]),
          'actual_sample_projected_px':qp[:2].tolist(),'target_sample_projected_px':wp[:2].tolist(),'projected_sample_deviation_px':float(np.linalg.norm(qp[:2]-wp[:2])),
          'scope':'Exact projection of our working-mesh witness in the proposed macro camera, not photo fidelity or OEM tolerance.'}
    (O/'refinement-local-diagnostic.json').write_text(json.dumps(diagnostic,indent=2)+'\n')
    witnesses=errors[:,errors.max(0)>P['sampled_refinement_goal_m']]
    return bad,{'vertices':len(V),'triangles':len(I),'sampled_triangles':len(candidate),'max_sampled_target_gap_m':float(errors.max()),
                'p99_sampled_target_gap_m':float(np.quantile(errors,.99)),'triangles_over_goal':len(bad)},witnesses
def edgekeys(edges):
    a=np.minimum(edges[...,0],edges[...,1]).astype(np.uint64);b=np.maximum(edges[...,0],edges[...,1]).astype(np.uint64)
    return(a<<np.uint64(32))|b
for iteration in range(P['maximum_refinement_iterations']+1):
    bad,row,witnesses=sample();row['iteration']=iteration;history.append(row);print('FRONT_JUNCTION_REFINEMENT',json.dumps(row),flush=True)
    if '--diagnostic-only'in sys.argv and iteration==6:
        print('DIAGNOSTIC_ONLY_NO_SOURCE_SAVED',flush=True);raise SystemExit
    if not len(bad):break
    if diagnostic_after is not None and iteration==diagnostic_after:
        print('SAVE_BOUNDED_VISUAL_DIAGNOSTIC_GOAL_NOT_MET',flush=True);break
    assert iteration<P['maximum_refinement_iterations'],('Sampled criterion not reached',row)
    be=I[bad][:,[[0,1],[1,2],[2,0]]]
    # Split ALL actual failing midpoint edges, not just the largest witness:
    # otherwise projected relief can generate a new fan while an original
    # failing edge is repeatedly starved. Centre-only failures use footprint
    # X/arc length, excluding radial height.
    ba=B[be[:,:,0]];bb=B[be[:,:,1]];dx=ba[:,:,0]-bb[:,:,0]
    angle_a=np.arctan2(ba[:,:,1],ba[:,:,2]-.29);angle_b=np.arctan2(bb[:,:,1],bb[:,:,2]-.29)
    da=np.arctan2(np.sin(angle_a-angle_b),np.cos(angle_a-angle_b))*F.R
    choice=(dx*dx+da*da).argmax(1);failing_edges=witnesses[1:].T>P['sampled_refinement_goal_m']
    centre_only=~failing_edges.any(1);badkeys=edgekeys(be)
    marked=np.unique(np.concatenate([badkeys[failing_edges],badkeys[np.flatnonzero(centre_only),choice[centre_only]]]))
    ends=np.stack([(marked>>np.uint64(32)).astype(np.int32),(marked&np.uint64(0xffffffff)).astype(np.int32)],-1)
    baseline_mid=(B[ends[:,0]]+B[ends[:,1]])*.5
    mid=target_position(baseline_mid).astype(np.float32)
    assert not np.any(np.all(mid==V[ends[:,0]],1)|np.all(mid==V[ends[:,1]],1)),'Float32 collapsed midpoint'
    offset=len(V);V=np.concatenate([V,mid]);B=np.concatenate([B,baseline_mid]);allkeys=edgekeys(I[:,[[0,1],[1,2],[2,0]]]);split=np.isin(allkeys,marked);touched=split.any(1)
    NF=[];NU=[];NNN=[]
    for fi in np.flatnonzero(touched):
        ids=I[fi];local={int(ids[j]):(UV[fi,j],NN[fi,j])for j in range(3)};mm={}
        for j in np.flatnonzero(split[fi]):
            k=int(np.searchsorted(marked,allkeys[fi,j]));ni=offset+k;mm[int(j)]=ni
            uv=(UV[fi,j]+UV[fi,(j+1)%3])*.5;n=(NN[fi,j]+NN[fi,(j+1)%3])*.5;n=n/np.linalg.norm(n)
            local[ni]=(uv,n)
        if len(mm)==1:
            j=next(iter(mm));a,b,c=map(int,[ids[j],ids[(j+1)%3],ids[(j+2)%3]]);q=mm[j];faces=[(a,q,c),(q,b,c)]
        elif len(mm)==2:
            missing=next(j for j in range(3)if j not in mm);c=(missing+2)%3;a=(c+2)%3;b=(c+1)%3;ma,mb=mm[a],mm[c]
            faces=[(int(ids[c]),mb,ma),(int(ids[a]),ma,int(ids[b])),(ma,mb,int(ids[b]))]
        else:
            a,b,c=map(int,ids);q0,q1,q2=mm[0],mm[1],mm[2];faces=[(a,q0,q2),(q0,b,q1),(q2,q1,c),(q0,q1,q2)]
        for face in faces:NF.append(face);NU.append([local[j][0]for j in face]);NNN.append([local[j][1]for j in face])
    I=np.concatenate([I[~touched],np.array(NF,np.int32)]);UV=np.concatenate([UV[~touched],np.array(NU,np.float32)]);NN=np.concatenate([NN[~touched],np.array(NNN,np.float32)])

assert np.array_equal(V[:initial_count][~changed],initial_V[~changed])and np.array_equal(V[:initial_count,0],initial_V[:,0])
assert np.array_equal(V.min(0),initial_V.min(0))and np.array_equal(V.max(0),initial_V.max(0)),'Bounds moved outside protected legacy envelope'
tri=V[I].astype(np.float64);areas=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)*.5
volume=float(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6);assert areas.min()>1e-18 and volume>0
mesh=bpy.data.meshes.new('Original inspection with bounded local junction correction');mesh.from_pydata(V,[],I);mesh.update();assert not mesh.validate(clean_customdata=False)
layer=mesh.uv_layers.new(name=uvname);layer.data.foreach_set('uv',UV.ravel());mesh.polygons.foreach_set('use_smooth',np.ones(len(I),bool));mesh.update()
actual_normals=array(mesh.corner_normals,'vector',3,np.float32)
corner_positions=V[I].reshape(-1,3);nx,_,na=coords(corner_positions)
eligible=((UV[:,:,1]<5/30)|(UV[:,:,1]>25/30)).ravel();weight=F.normal_weight(nx,na)*eligible
retained=NN.reshape(-1,3);blended=retained.astype(np.float64).copy();ids=np.flatnonzero(weight>0)
blended[ids]=retained[ids]*(1-weight[ids,None])+actual_normals[ids]*weight[ids,None];blended[ids]/=np.linalg.norm(blended[ids],axis=1)[:,None]
mesh.normals_split_custom_set(blended.astype(np.float32));o.data=mesh
stored_normals=array(mesh.corner_normals,'vector',3,np.float32)
normal_storage_error=np.linalg.norm(stored_normals.astype(np.float64)-blended.astype(np.float32),axis=1)
assert np.isfinite(stored_normals).all()and np.min(np.linalg.norm(stored_normals,axis=1))>.99
bm=bmesh.new();bm.from_mesh(mesh);nm=sum(not e.is_manifold for e in bm.edges);chi=len(bm.verts)-len(bm.edges)+len(bm.faces);bm.free();assert nm==0 and chi==0
o.name='Front tyre v3 locally corrected junction candidate';o['component_id']=P['component_id'];o['art_accepted']=False
gray=bpy.data.materials.new('G3 neutral gray no microrelief');gray.use_nodes=True;gray.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.22,.24,.26,1);gray.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.4;mesh.materials.append(gray)
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
glb=H/(asset_stem+'-inspection.glb');bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True,export_normals=True,export_texcoords=True,export_tangents=False)
s.world=bpy.data.worlds.new('FRONT TYRE G3 WORLD');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.18,.20,.23,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.25
for name,loc,power,size in [('KEY',(.7,-.7,1),30,.6),('FILL',(-.5,-.3,.6),12,.6),('EDGE',(.25,.7,.65),20,.5)]:
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o2=bpy.data.objects.new(name,d);s.collection.objects.link(o2);o2.location=loc;o2.rotation_euler=(Vector((0,0,.29))-o2.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('FRONT TYRE G3 CAMERA',bpy.data.cameras.new('FRONT TYRE G3 CAMERA'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.clip_start=.001;cam.data.clip_end=5
cam.location=(.7,-.9,.65);cam.rotation_euler=(Vector((0,0,.29))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.77
s.render.engine='CYCLES';s.render.threads_mode='FIXED';s.render.threads=1;s.cycles.samples=24;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-.5
newsource=H/(asset_stem+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(newsource),compress=True,relative_remap=False)
report={'component_id':P['component_id'],'revision':P['revision'],'collection':P['collection'],'source_sha256':sha(newsource),'export_sha256':sha(glb),'baseline_source_sha256':sha(source),
 'script_sha256':sha(Path(__file__)),'field_script_sha256':sha(H/'junction_field.py'),'legacy_field_consistency_max_m':float(old_consistency.max()),
 'initial_vertices':initial_count,'initial_triangles':len(initial_I),'vertices':len(V),'triangles':len(I),'old_vertices_radially_modified':int(changed.sum()),'added_vertices':len(V)-initial_count,
 'protected_old_vertex_coordinates_exact':True,'all_old_vertex_X_exact':True,'axis_aligned_bounds_exact':True,
 'old_vertex_max_radial_extra_depth_m':float(delta[changed].max()),'author_extra_depth_bound_m':P['junction_extra_depth_bound_m'],
 'indices_changed_by_conforming_local_refinement':True,'refinement_edge_policy':'Every failing edge-midpoint witness; only centroid-only failures use baseline X/arc footprint longest edge, excluding relief height.',
 'UV_interpolated_per_corner_without_seam_weld':True,'old_corner_normal_INPUTS_outside_expanded_band_preserved':True,
 'native_custom_normal_storage_max_error':float(normal_storage_error.max()),
 'stored_outside_input_normals_exact':bool(np.array_equal(stored_normals[weight==0],retained[weight==0])),
 'stored_outside_input_normal_max_error':float(normal_storage_error[weight==0].max()),
 'normal_rule':'Actual refined smooth-mesh corner normals with C1taper to retained old normals across repair band; no inherited modifiers/global WeightedNormal or postexport repair.',
 'minimum_triangle_area_m2':float(areas.min()),'signed_volume_m3':volume,'nonmanifold_edges':nm,'euler_characteristic':chi,'refinement_history':history,
 'sampled_goal_m':P['sampled_refinement_goal_m'],'sampled_goal_met':not len(bad),'sampled_target_gap_not_global_bound':True,
 'diagnostic_only_no_production_freeze':diagnostic_after is not None,'diagnostic_iteration_limit':diagnostic_after,
 'source_path':str(newsource.relative_to(R)),'export_path':str(glb.relative_to(R)),
 'C1_geometry_gate_to_fixed_baseline_surface':True,'new_tread_family_or_pitch':False,'stale_v2_bake_reused':False,'material_built':False,'art_accepted':False}
assert sha(source)==P['source_sha256'];outname='diagnostic-source-geometry-check.json'if diagnostic_after is not None else'source-geometry-check.json'
(O/outname).write_text(json.dumps(report,indent=2)+'\n');(H/('diagnostic-build-report.json'if diagnostic_after is not None else'build-report.json')).write_text(json.dumps(report,indent=2)+'\n');print('FRONT_TYRE_V3_G3_BUILT',json.dumps(report),flush=True)
