"""Widen only unfrozen gray source camera; record geometry/export invariance."""
import bpy,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import bounds,digest,sha
R=Path(__file__).resolve().parents[1];n=sys.argv[sys.argv.index('--')+1];H=R/'assets-src/moto-components'/n;O=R/'creative/reviews'/n
assert not (O/'gray-delivery.json').exists() and not (O/'delivery.json').exists()
p=H/'child-gray.blend';before=sha(p);g=sha(H/'child-gray.glb');bpy.ops.wm.open_mainfile(filepath=str(p));dig={o.name:digest(o.data)for o in bpy.context.scene.objects if o.type=='MESH'};_,size,_,_=bounds();old=bpy.context.scene.camera.data.ortho_scale;bpy.context.scene.camera.data.ortho_scale=size*2.15;bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True)
assert all(digest(bpy.data.objects[k].data)==v for k,v in dig.items()) and sha(H/'child-gray.glb')==g
j=json.loads((O/'geometry-check.json').read_text());j['source_sha256']=sha(p);(O/'geometry-check.json').write_text(json.dumps(j,indent=2)+'\n');(O/'camera-margin-correction.json').write_text(json.dumps(dict(reason='Whole actual gray bounds exceeded frame in edge/reverse; widening camera only, no shape change',old_ortho_scale_m=old,new_ortho_scale_m=size*2.15,source_before_sha256=before,source_after_sha256=sha(p),export_sha256=g,geometry_digest=dig,geometry_unchanged=True),indent=2)+'\n')
