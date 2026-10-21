"""Read-only true contact-face vertices against frozen guide triangles, sampled only."""
from pathlib import Path
import bpy,json,hashlib,math,numpy as np
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-protection-end-weld-a-v1';P=json.loads((H/'parameters.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();src=H/'engine-protection-end-weld-a-v1.blend';glb=H/'engine-protection-end-weld-a-inspection.glb';a=json.loads((O/'source-geometry-check.json').read_text());guide=R/P['guide_source'];assert sha(src)==a['source_sha256']and sha(guide)==P['guide_source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(src));obs=list(bpy.data.collections[P['collection']].objects);assert len(obs)==1 and not obs[0].modifiers and not bpy.data.libraries;o=obs[0];o.data.calc_loop_triangles();V=[tuple(v.co)for v in o.data.vertices];F=[tuple(t.vertices)for t in o.data.loop_triangles];images=[{'name':im.name,'path':im.filepath,'packed':bool(im.packed_file)}for im in bpy.data.images if im.source=='FILE'];assert all(im['packed']and im['path'].startswith('//')for im in images);pose=Matrix.Translation(P['context_pose_estimated']['translation_m'])@Matrix.Rotation(math.pi,4,'Z');world=[pose@Vector(v)for v in V];weldtree=BVHTree.FromPolygons(world,F,all_triangles=True);bpy.ops.wm.open_mainfile(filepath=str(guide))
def actual_tree(collection):
 v=[];f=[]
 for o in bpy.data.collections[collection].all_objects:
  if o.type!='MESH':continue
  o.data.calc_loop_triangles();offset=len(v);v.extend([o.matrix_world@p.co for p in o.data.vertices]);f.extend([tuple(i+offset for i in t.vertices)for t in o.data.loop_triangles])
 return BVHTree.FromPolygons(v,f,all_triangles=True)
tube=actual_tree('WEWA_ENGINE_PROTECTION_HOOP_TUBE_ISOLATED');plate=actual_tree('WEWA_ENGINE_PROTECTION_TERMINAL_A_ISOLATED');K=P['outer_profile_segments']+2;rows=[]
for i in range(P['angular_segments']+1):
 for role,jj,tree in [('plate-toe',1,plate),('tube-toe',K-1,tube)]:
  point=world[i*K+jj];loc,n,triangle,dist=tree.find_nearest(point);assert loc is not None;rows.append({'row':i,'role':role,'actual_weld_vertex':i*K+jj,'actual_weld_world_m':list(point),'nearest_actual_context_triangle':triangle,'nearest_context_point_m':list(loc),'distance_m':dist})
stats={}
for role in ['plate-toe','tube-toe']:
 d=np.array([q['distance_m']for q in rows if q['role']==role]);stats[role]={'samples':len(d),'max_distance_m':float(d.max()),'median_distance_m':float(np.median(d)),'p95_distance_m':float(np.percentile(d,95))}
probes=[]
for name,origin,direction,distance in [('existing-side-mouth-axis-weld-only',(-.070,-.02,-.255),(0,1,0),.05),('existing-lower-tab-axis-weld-only',(-.10,0,-.255),(1,0,0),.1)]:
 hit=weldtree.ray_cast(Vector(origin),Vector(direction),distance);assert hit[0]is None;probes.append({'name':name,'origin':origin,'direction':direction,'max_distance_m':distance,'weld_hit':False,'scope':'Tests only the new bead mesh, not the entire assembled path or real hardware interface.'})
assert sha(src)==a['source_sha256']and sha(guide)==P['guide_source_sha256'];q={'component_id':P['component_id'],'source_sha256':sha(src),'export_sha256':sha(glb),'guide_source_sha256':sha(guide),'source_external_libraries':[],'source_images':images,'all_four_original_guide_parts_and_poses_unchanged':True,'actual_sampled_contact_stats':stats,'actual_sampled_contacts':rows,'weld_only_clearance_probes':probes,'scope':'Actual transformed weldtoe vertices against actual frozen guide triangles, sparse contact witness. Native tube polygonal discretization can differ from the nominal circular author section. No arbitrary buffer correction or oldpart deformation. No complete area/contact/overlap/structural certificate.','all_metrics_and_pose_estimated':True,'complete_weld_or_guard_built':False,'installed_fit_or_strength_verified':False,'art_accepted':False};(O/'source-interface-check.json').write_text(json.dumps(q,indent=2)+'\n');print('WELD_A_INTERFACE_READ',json.dumps(stats),flush=True)
