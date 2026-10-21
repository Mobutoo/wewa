"""Actual source opening/thickness/flat-normal and portability checks, no fit claim."""
import bpy,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-protection-terminal-b-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();src=H/'engine-protection-terminal-b-v1.blend';glb=H/'engine-protection-terminal-b-inspection.glb';bpy.ops.wm.open_mainfile(filepath=str(src));obs=list(bpy.data.collections['WEWA_ENGINE_PROTECTION_TERMINAL_B_ISOLATED'].objects);assert len(obs)==1;m=obs[0].data;tree=BVHTree.FromPolygons([v.co for v in m.vertices],[tuple(p.vertices)for p in m.polygons]);probes=[]
for p in json.loads((H/'probes.json').read_text()):
 hit=tree.ray_cast(Vector(p['origin']),Vector(p['direction']),p['max_distance']);clear=p['expected_hits']==0;assert(hit[0]is None)==clear,(p['name'],hit);probes.append({'name':p['name'],'expected_clear':clear,'actually_clear':hit[0]is None,'first_hit_m':float(hit[3])if hit[3]is not None else None})
V=np.array([v.co[:]for v in m.vertices]);ns=np.array([n.vector[:]for n in m.corner_normals]);flatloops=[];flatfaceN=[]
for p in m.polygons:
 q=V[list(p.vertices)]
 # Only genuinely identical stored float32 plane coordinates; the former
 # tolerance also selected almost-planar bevel faces and tested the wrong scope.
 if np.ptp(q[:,1])==0 and not p.use_smooth:
  flatloops.extend(p.loop_indices);flatfaceN.append(p.normal[:]);assert not p.use_smooth
flat=ns[flatloops];assert len(flat)>0;err=float(np.max(np.abs(flat[:,[0,2]])));geometric_error=float(np.max(np.abs(np.asarray(flatfaceN)[:,[0,2]])));assert geometric_error<1e-7 and np.min(np.abs(flat[:,1]))>.99999
libs=[x.filepath for x in bpy.data.libraries];assert not libs;images=[{'name':x.name,'path':x.filepath,'packed':bool(x.packed_file)}for x in bpy.data.images if x.source=='FILE'];assert all(x['packed']and x['path'].startswith('//')and(H/x['path'][2:]).is_file()for x in images)
r={'source_sha256':sha(src),'export_sha256':sha(glb),'actual_source_void_checks':probes,'actual_planar_loops_checked':len(flat),'maximum_planar_geometric_face_normal_transverse_component':geometric_error,'maximum_stored_corner_normal_transverse_component_measured':err,'normal_limit':'Stored actual planar corner residual reported without claiming exact direction or OEM tolerance. Curves retain analytic normals, no buffer repair. Reflection review required.','external_libraries':libs,'images':images,'tube_hook_spacer_or_weld_built':False,'fold_profile_or_thickness_measured':False,'installed_pose_or_mount_contact_verified':False,'current_RDC_identity_verified':False,'art_accepted':False};(O/'source-interface-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
