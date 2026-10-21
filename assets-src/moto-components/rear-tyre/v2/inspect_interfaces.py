"""Re-evaluate actual source passages and portable dependencies, no source mutation."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/rear-tyre-v2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(H/'rear-tyre-v2.blend'));o=bpy.data.collections['WEWA_REAR_TYRE_ISOLATED'].objects[0];tree=BVHTree.FromObject(o,bpy.context.evaluated_depsgraph_get());probes=[]
def ray(label,origin,direction,distance,clear):
 hit=tree.ray_cast(Vector(origin),Vector(direction),distance);actual=hit[0]is None;assert actual==clear,(label,hit);probes.append({'label':label,'origin_m':list(origin),'direction':list(direction),'distance_m':distance,'clear':actual,'hit_distance_m':hit[3]})
ray('open axle axis',(-.15,0,0),(1,0,0),.3,True)
for t in [0,.13,.31]:ray('rubber crown at angle '+str(t),(0,.34*math.cos(t),.34*math.sin(t)),(0,-math.cos(t),-math.sin(t)),.09,False)
ray('bead opening clearance',(-.10,.20,0),(1,0,0),.2,True)
libs=[l.filepath for l in bpy.data.libraries];images=[{'path':im.filepath,'packed':bool(im.packed_file)}for im in bpy.data.images if im.source=='FILE'];assert not libs;assert all(im['packed']or im['path'].startswith('//')for im in images)
r={'source_sha256':sha(H/'rear-tyre-v2.blend'),'export_sha256':sha(H/'rear-tyre-v2-inspection.glb'),'actual_source_probes':probes,'external_libraries':libs,'image_paths':images,'current_RDC_fit_verified':False,'art_accepted':False};(O/'source-interface-check.json').write_text(json.dumps(r,indent=2)+'\n');s=json.loads((O/'source-geometry-check.json').read_text());assert s['source_sha256']==r['source_sha256'];s['source_probes']=probes;s['previous_source_probes_not_reused']=True;(O/'source-geometry-check.json').write_text(json.dumps(s,indent=2)+'\n');(H/'build-report.json').write_text(json.dumps(s,indent=2)+'\n');print('TYRE2_ACTUAL_INTERFACE_PROBES',len(probes))
