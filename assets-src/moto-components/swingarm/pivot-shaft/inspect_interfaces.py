"""Read-only source probes, source analytic flat normals and portability; no fit claim."""
import bpy,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/swingarm-pivot-shaft-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();src=H/'swingarm-pivot-shaft-v1.blend';glb=H/'swingarm-pivot-shaft-inspection.glb';bpy.ops.wm.open_mainfile(filepath=str(src));o=list(bpy.data.collections['WEWA_SWINGARM_PIVOT_SHAFT_ISOLATED'].objects)[0];m=o.data;m.calc_loop_triangles();v=np.array([v.co[:]for v in m.vertices]);tr=np.array([t.vertices[:]for t in m.loop_triangles]);b=BVHTree.FromPolygons([Vector(a)for a in v],tr.tolist(),all_triangles=True);rows=[]
for name,origin,direction,expected in [('tip axial hit',(-.3,0,0),(1,0,0),.17),('head axial hit',(.3,0,0),(-1,0,0),.17),('midshank14diameter',(0,.05,0),(0,-1,0),.043)]:
 loc,n,idx,d=b.ray_cast(Vector(origin),Vector(direction),1.);assert loc is not None and abs(d-expected)<1e-7;rows.append({'probe':name,'actual_hit_m':d,'expected_candidate_m':expected,'numerical_tolerance_m':1e-7})
ns=np.array([n.vector[:]for n in m.corner_normals]);poly=np.array([p.vertices[:]for p in m.polygons]);normidx=np.array([p.loop_start for p in m.polygons]);flatrows=[];targetnormals=ns.copy();cap_indices=[]
for label,xsign in [('tip',-1),('head',1)]:
 at=abs(v[poly][:,:,0]-xsign*.13).max(axis=1)<1e-8;ids=np.flatnonzero(at);assert len(ids)>0;corn=np.concatenate([np.arange(normidx[i],normidx[i]+3)for i in ids]);target=np.array([xsign,0,0]);targetnormals[corn]=target;cap_indices.append(corn);err=float(np.max(np.linalg.norm(ns[corn]-target,axis=1)));flatrows.append({'plane':label,'actual_faces':len(ids),'decoded_max_corner_normal_error_from_ideal_axis':err,'initial_1e_minus6_ideal_axis_check_passed':err<1e-6,'actual_endplane_error_m':float(abs(v[poly[ids]][:,:,0]-xsign*.13).max())})
# Numerical author check, not a higher arbitrary tolerance: replay EXACT intended cap axis normals.
# Blender encodes custom split normals relative to loop fans. Compare the decoded result bit-for-bit.
copy=m.copy();copy.normals_split_custom_set(targetnormals.tolist());copy.update();replay=np.array([n.vector[:]for n in copy.corner_normals])
for row,corn in zip(flatrows,cap_indices):
 row['exact_axis_author_replay_decodes_identically']=bool(np.array_equal(ns[corn],replay[corn]));row['maximum_replay_difference']=float(np.linalg.norm(ns[corn]-replay[corn],axis=1).max());assert row['exact_axis_author_replay_decodes_identically']
bpy.data.meshes.remove(copy)
libs=[l.filepath for l in bpy.data.libraries];assert not libs;images=[]
for im in bpy.data.images:
 if im.type=='IMAGE'and im.source=='FILE':assert im.filepath.startswith('//')and im.packed_file;images.append({'name':im.name,'path':im.filepath,'packed':bool(im.packed_file)})
r={'source_sha256':sha(src),'export_sha256':sha(glb),'probes':rows,'source_endplane_normals':flatrows,'external_libraries':libs,'image_paths':images,'source_portable_without_reference_photos':True,'shaft_bush_or_frame_fit_verified':False,'collar_separate_or_integral_resolved':False,'thread_pitch_handedness_form_certified':False,'load_or_strength_qualified':False,'current_RDC_identity_verified':False,'art_accepted':False};(O/'source-interface-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
