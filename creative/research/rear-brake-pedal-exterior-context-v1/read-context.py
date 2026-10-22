import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix,Euler
from mathutils.bvhtree import BVHTree
R=Path('/workspace/wewa');K='rear-brake-pedal-exterior-context-v1';H=R/'assets-src/moto-components'/K;D=R/'creative/research'/K;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(H/(K+'.blend')));bpy.context.view_layer.update();rows=[];points={};geometries={}
for inst in bpy.context.evaluated_depsgraph_get().object_instances:
 ob=inst.object
 if ob.type!='MESH':continue
 assert inst.is_instance and ob.original.library and ob.data.library and all(m.library for m in ob.data.materials)
 ps=[inst.matrix_world@v.co for v in ob.data.vertices];points[ob.name]=ps;geometries[ob.name]=(ps,[list(p.vertices)for p in ob.data.polygons]);rows.append(dict(object=ob.name,library=bpy.path.abspath(ob.original.library.filepath),matrix_world=[list(r)for r in inst.matrix_world],bounds_m={'min':[min(p[i]for p in ps)for i in range(3)],'max':[max(p[i]for p in ps)for i in range(3)]},vertices=len(ps),materials=[dict(name=m.name,library=bpy.path.abspath(m.library.filepath))for m in ob.data.materials]))
assert len(rows)==4 and bpy.context.scene.view_layers[0].material_override is None
checks=[];arm=next(k for k in geometries if k=='BRAKE_PEDAL_COMPOUND_ARM_METAL');verts,polys=geometries[arm];tree=BVHTree.FromPolygons(verts,polys,all_triangles=False)
for key,ps in points.items():
 if key==arm:continue
 distances=[tree.find_nearest(p)[3]for p in ps];checks.append(dict(object=key,minimum_vertex_to_arm_surface_distance_m=min(distances),scope='Vertices to arm BVH only, not exact continuous surface clearance or collision/fit proof'))
for p in json.loads((D/'native-links-and-transforms.json').read_text())['parents']:assert sha(R/p['source'])==p['sha256']
(D/'native-context-read.json').write_text(json.dumps(dict(source_sha256=sha(H/(K+'.blend')),mesh_instances=rows,source_hashes_unchanged=True,linked_native_geometry_and_materials=True,approximate_separation_checks=checks,new_physical_ids=0,fit_qualified=False),indent=2)+'\n')
# Q checked independently of any mounted translation. Exact intended signs, no arbitrary X offset.
Q=Matrix(((0,0,-1),(-1,0,0),(0,1,0)));E=Euler((1.5707963267948966,0,-1.5707963267948966),'XYZ').to_matrix();assert max(abs(Q[i][j]-E[i][j])for i in range(3)for j in range(3))<1e-6
endpoint=Vector((.19278,-.17577,.028));requested=Vector((0,.136,-.777));hint=requested-Q@endpoint
(D/'world-frame-hint-check.json').write_text(json.dumps(dict(authority='Coordinator dispatch within user-authorized autonomous motorcycle completion; numeric example supplied by coordinator, NOT user measurement or OEM data',Q_rows=[list(r)for r in Q],Q_EulerXYZ_degrees=[90,0,-90],determinant=Q.determinant(),mapping='+X -> world-Y front; +Y -> world+Z up; +Z -> world-X right',arm_origin_role='PF product photo bend178,159, not actual pivot',arm_toe_endpoint=list(endpoint),illustrative_target_YZ=[.136,-.777],implied_arm_origin_world_YZ=[hint.y,hint.z],world_X='Unknown; no arbitrary transverse placement assigned',projected_local_sleeve_axis_XY=[-.0063,.0063],implied_sleeve_axis_world_YZ=[hint.y+.0063,hint.z+.0063],parked_pad_center_local=[.20916,-.20475,.050],illustrative_parked_pad_center_world_YZ=[hint.y-.20916,hint.z-.20475],warning='Endpoint target is not pad-centre target. Implied arm-origin coordinates are not pivot coordinates. Pad face-study normal+Z maps world-X, NOT foot-up: parked pad must not be called mounted after Q. Camera/product perspective and related variant prohibit certified installed pose.',mounted_pose_qualified=False,fit_qualified=False),indent=2)+'\n')
