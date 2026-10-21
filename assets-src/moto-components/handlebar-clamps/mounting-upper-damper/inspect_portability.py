"""Final source dependencies/roles, no duplicate geometry scan or source mutation."""
import bpy,json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/handlebar-mount-upper-damper-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();src=H/'handlebar-mount-upper-damper-v1.blend';glb=H/'handlebar-mount-upper-damper-inspection.glb';bpy.ops.wm.open_mainfile(filepath=str(src));libs=[x.filepath for x in bpy.data.libraries];ims=[]
for x in bpy.data.images:
 if x.source!='FILE':continue
 assert x.filepath.startswith('//')and x.packed_file and x.colorspace_settings.name=='Non-Color';p=H/x.filepath[2:];assert p.is_file();ims.append({'name':x.name,'relative_path':x.filepath,'packed':True,'relative_companion_exists':True,'companion_sha256':sha(p),'color_space':x.colorspace_settings.name})
assert not libs and len(ims)==2
r={'source_sha256':sha(src),'export_sha256':sha(glb),'external_libraries':libs,'images':ims,'packed_relative_images':len(ims),'all_companion_files_exist':True,'geometry_scan_repeated':False,'geometry_evidence':'source-inspection-check.json is original G3 scan; material-preservation-check.json proves exact actual G3→PBR attributes, indices and matrices.','hidden_reverse_or_mounting_certified':False,'art_accepted':False};(O/'source-portability-check.json').write_text(json.dumps(r,indent=2)+'\n');print('UPPER_DAMPER_PORTABILITY',json.dumps(r))
