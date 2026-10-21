"""Blender-only camera check for new isolated component renders.
Checks actual evaluated mesh vertices, including active shape keys; no mesh or camera mutation.
A deliberate macro may allow cropping, never near/far clipping. This is not a photographic match.
Historical render helpers and proofs must stay unchanged.
"""
import json
import bpy
import numpy as np

def check_component_camera(scene, objects, *, allow_crop=False, margin=0.005):
    camera=scene.camera
    if camera is None:
        raise ValueError('No active camera')
    graph=bpy.context.evaluated_depsgraph_get()
    graph.update()
    render=scene.render
    projection=np.asarray(camera.calc_matrix_camera(graph,x=render.resolution_x,y=render.resolution_y,scale_x=render.pixel_aspect_x,scale_y=render.pixel_aspect_y),dtype=np.float64)
    view=np.asarray(camera.matrix_world.inverted(),dtype=np.float64)
    rows=[]
    for obj in objects:
        if obj.type!='MESH' or obj.hide_render or not obj.visible_camera:
            continue
        evaluated=obj.evaluated_get(graph)
        mesh=evaluated.to_mesh()
        try:
            if not mesh.vertices:
                continue
            coordinates=np.empty(len(mesh.vertices)*3,dtype=np.float64)
            mesh.vertices.foreach_get('co',coordinates)
            xyz=coordinates.reshape(-1,3)
            world=np.asarray(evaluated.matrix_world,dtype=np.float64)
            local_to_view=view@world
            positions=xyz@local_to_view[:3,:3].T+local_to_view[:3,3]
            depth=-positions[:,2]
            clip=np.column_stack((positions,np.ones(len(positions))))@projection.T
            uv=(clip[:,:2]/clip[:,3:4]+1)*0.5
            rows.append({'object':obj.name,'vertices':len(xyz),'depth_m':[float(depth.min()),float(depth.max())],'projected_uv_min':uv.min(0).tolist(),'projected_uv_max':uv.max(0).tolist(),'finite':bool(np.isfinite(uv).all())})
        finally:
            evaluated.to_mesh_clear()
    if not rows:
        raise ValueError('No camera-visible evaluated component mesh')
    low=np.min([r['projected_uv_min']for r in rows],axis=0)
    high=np.max([r['projected_uv_max']for r in rows],axis=0)
    depth_low=min(r['depth_m'][0]for r in rows)
    depth_high=max(r['depth_m'][1]for r in rows)
    clipping=depth_low<=camera.data.clip_start or depth_high>=camera.data.clip_end
    cropped=bool((low<margin).any()or(high>1-margin).any())
    result={'schema':'wewa.camera-preflight.v1','camera':camera.name,'camera_type':camera.data.type,'camera_clip_m':[camera.data.clip_start,camera.data.clip_end],'nearest_actual_vertex_depth_m':depth_low,'farthest_actual_vertex_depth_m':depth_high,'projected_uv_min':low.tolist(),'projected_uv_max':high.tolist(),'allow_deliberate_crop':allow_crop,'whole_component_margin':margin,'mesh_rows':rows,'actual_vertices_outside_depth_range':clipping,'projected_extent_outside_margin':cropped,'scope':'Actual evaluated mesh extents under active shape keys; geometry visibility only, not exposure, focus, photographic calibration or artistic reception'}
    if clipping or not all(r['finite']for r in rows)or(cropped and not allow_crop):
        raise ValueError(json.dumps(result))
    result['technical_preflight_passed']=True
    return result
