"""Actual source ray tests of visible openings and formed-return thickness."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/swingarm-body-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();s=json.loads((O/'source-geometry-check.json').read_text());assert s['source_sha256']==sha(H/'swingarm-body-v1.blend');bpy.ops.wm.open_mainfile(filepath=str(H/'swingarm-body-v1.blend'));o=next(o for o in bpy.data.collections['WEWA_SWINGARM_BODY_ISOLATED'].objects if o.type=='MESH');o.data.calc_loop_triangles();tree=BVHTree.FromPolygons([v.co for v in o.data.vertices],[tuple(t.vertices)for t in o.data.loop_triangles],all_triangles=True);probes=[]
for sign in[-1,1]:
 for name,y,z in[('paired_mount_holes',.430,.040),('small_front_tube',.062,.0185)]:
  x=sign*(.103+.007/.558*y);origin=Vector((x-.035,y,z));clear=tree.ray_cast(origin,Vector((1,0,0)),.07)[0]is None;probes.append({'name':name,'side_sign_provisional':sign,'origin_m':list(origin),'axis':[1,0,0],'length_m':.07,'clear':clear});assert clear,probes[-1]
origin=Vector((-.16,.482,-.029));clear=tree.ray_cast(origin,Vector((1,0,0)),.08)[0]is None;assert clear;probes.append({'name':'additional_asymmetric_tab_hole','origin_m':list(origin),'axis':[1,0,0],'length_m':.08,'clear':clear})
origin=Vector((0,.150,.007));a=tree.ray_cast(origin,Vector((0,1,0)),.05);assert a[0];b=tree.ray_cast(a[0]+Vector((0,1e-6,0)),Vector((0,1,0)),.05);assert b[0];thickness=(b[0]-a[0]).length;assert abs(thickness-.0018)<.00005,(a,b,thickness)
r={'source_sha256':sha(H/'swingarm-body-v1.blend'),'export_sha256':sha(H/'swingarm-body-v1-inspection.glb'),'visible_passage_rays':probes,'front_inner_return_actual_source_thickness_m':thickness,'front_inner_return_entry_m':list(a[0]),'front_inner_return_exit_m':list(b[0]),'thickness_is_author_geometry_not_physical_measurement':True,'external_libraries':[l.filepath for l in bpy.data.libraries],'image_paths':[{'path':i.filepath,'packed':bool(i.packed_file)}for i in bpy.data.images if i.source=='FILE'],'art_accepted':False};assert not r['external_libraries'];(O/'source-interface-check.json').write_text(json.dumps(r,indent=2)+'\n');print('WEWA_BODY_INTERFACES',json.dumps(r))
