"""Read-only source openings, cavity openness, thickness and portability; not OEMfit."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/chaincase-upper-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();src=H/'chaincase-upper-v1.blend';glb=H/'chaincase-upper-inspection.glb';P=json.loads((H/'parameters.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(src));o=bpy.data.collections['WEWA_CHAINCASE_UPPER_ISOLATED'].objects[0];m=o.data;m.calc_loop_triangles();b=BVHTree.FromPolygons([v.co for v in m.vertices],[t.vertices for t in m.loop_triangles],all_triangles=True);rows=[]
for label,yz in [(f'definite visible passage{i+1}',p)for i,p in enumerate(P['mount_holes_candidate_YZ_m'])]+[('concave rear arch',[0,0])]:
 hit=b.ray_cast(Vector((-.15,*yz)),Vector((1,0,0)),.4);assert hit[0]is None;rows.append({'probe':label,'actual_ray_clear':True})
for label,origin,direction,clear in [('closed relief',(-.15,-.065,.060),(1,0,0),False),('cavity open inboard',(-.03,-.30,.035),(-1,0,0),True),('finite wall in front of cavity',(-.03,-.30,.035),(1,0,0),False)]:
 hit=b.ray_cast(Vector(origin),Vector(direction),.4);assert(hit[0]is None)==clear;rows.append({'probe':label,'actual_ray_clear':clear,'actual_hit_distance_m':None if clear else hit[3]})
# Independent opposed source rays bound actual plainwall intersection planes.
a=b.ray_cast(Vector((-.15,-.30,.035)),Vector((1,0,0)),.4)[0];c=b.ray_cast(Vector((.15,-.30,.035)),Vector((-1,0,0)),.4)[0];th=c.x-a.x;assert abs(th-.0009)<1e-7;libs=[l.filepath for l in bpy.data.libraries];assert not libs;images=[]
for im in bpy.data.images:
 if im.type=='IMAGE'and im.source=='FILE':assert im.filepath.startswith('//')and im.packed_file;images.append({'name':im.name,'path':im.filepath,'packed':bool(im.packed_file)})
r={'source_sha256':sha(src),'export_sha256':sha(glb),'probes':rows,'actual_plainwall_thickness_m':th,'numerical_tolerance_m_not_metrology':1e-7,'external_libraries':libs,'image_paths':images,'no_hidden_inboard_backplate_in_cavity_probe':True,'complete_forward_ear_built':False,'fourth_independent_mount_certified':False,'chain_swept_volume_or_lower_half_fit_verified':False,'RDC_identity_or_dimensions_certified':False,'strength_or_chemical_grade_qualified':False,'art_accepted':False};(O/'source-interface-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
