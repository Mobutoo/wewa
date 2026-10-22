"""One estimated normalized RH exemplar wrapper, compatible with existing coord native checker."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');K='right-side-cover-coordinate-conversion-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;D=R/'creative/research'/K;sys.path.insert(0,str(H));import build
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();T=Vector((-.135,.535,-.41))
def build_context():
 data=json.loads((D/'native-reopen-check.json').read_text());lo=[min(o['bounds_m']['min'][i]for o in data['objects'])+T[i]for i in range(3)];hi=[max(o['bounds_m']['max'][i]for o in data['objects'])+T[i]for i in range(3)]
 assert hi[0]<0 and lo[1]>-.42 and hi[1]<.865 and lo[2]>-.74
 s=1.285/527;nominal=[None,-.42+(797-432)*s,-.74+(494-360)*s];dy=T.y-nominal[1];dz=T.z-nominal[2]
 pose=dict(T=list(T),rotation_degrees=[0,0,0],scale=[1,1,1],world_bounds_m={'min':lo,'max':hi},coarse_context_checks={'entire_cover_on_right':hi[0]<0,'profile_between_axles':lo[1]>-.42 and hi[1]<.865,'above_axle_plane':lo[2]>-.74,'same_source_profile_connectivity':True},photo_nominal_center_world_yz=nominal[1:],proposed_minus_photo_nominal_yz_m=[dy,dz],proposed_photo_outline_shift_px=[-dy/s,-dz/s],frame_anchor_status='Existing whole v8 nominal axle layout and source selected1285mm/527px baseline, not calibrated mounted measurement',decision='Allow proposed T as coarse context-only exemplar; correct handedness/profile and vertical band, but ~65mm rearward difference remains explicit and photo registration is NOT qualified',uncertainty='Source scale broad .001962.. .002933m/px; world skeleton layout and photograph uncalibrated. No manufactured attachment/contact or photo tolerance inferred.',fit_qualified=False,photo_registration_qualified=False)
 (D/'estimated-context-pose-check.json').write_text(json.dumps(pose,indent=2)+'\n')
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
 source=H/'child-candidate.blend'
 with bpy.data.libraries.load(str(source),link=True)as(a,b):assert build.COLLECTION in a.collections;b.collections=[build.COLLECTION]
 ob=bpy.data.objects.new('COVERAGE_PARENT ['+K+']',None);bpy.context.scene.collection.objects.link(ob);ob.instance_type='COLLECTION';ob.instance_collection=b.collections[0];ob.location=T;ob['fit_qualified']=False;ob['physical_count_increment']=0
 build.studio()
 # Move review rig with context, not the linked native source.
 for o in bpy.context.scene.objects:
  if o.type in ['LIGHT','CAMERA']:o.location+=T
 sourceout=H/'estimated-context.blend'
 for lib in bpy.data.libraries:lib.filepath=bpy.path.relpath(lib.filepath,start=str(H))
 bpy.ops.wm.save_as_mainfile(filepath=str(sourceout),compress=True)
 row=dict(key=K,source=str(source.relative_to(R)),sha256=sha(source),collection=build.COLLECTION,selected_objects=[],translation_m=list(T),rotation_degrees=[0,0,0],scale=[1,1,1],placement_status='Coordinator proposed T, coarse context only; photo shift and fit unqualified')
 (O/'linked-parents-check.json').write_text(json.dumps(dict(source=str(sourceout.relative_to(R)),source_sha256=sha(sourceout),parents=[row],parent_count=1,scope='Single normalized RH exemplar wrapper, positive determinant, not mounted fit or source acceptance'),indent=2)+'\n')
 return pose
if __name__=='__main__':build_context()
