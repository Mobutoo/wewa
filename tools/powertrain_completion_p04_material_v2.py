"""Restore preserved analytic per-piece materials only after new composition gray review."""
import bpy,sys,json,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import R,digest,sha,write,export
H=R/'assets-src/moto-components/side-cover-right-v2';O=R/'creative/reviews/side-cover-right-v2';assert json.loads((O/'gray-review.json').read_text())['read_for_exterior_study'];bpy.ops.wm.open_mainfile(filepath=str(H/'child-gray.blend'));record=json.loads((O/'reuse-placement-check.json').read_text());before={n:digest(bpy.data.objects[n].data)for n in record['preserved_materials']}
for name,mat in record['preserved_materials'].items():
 ob=bpy.data.objects[name];ob.data.materials.clear();ob.data.materials.append(bpy.data.materials[mat]);assert digest(ob.data)==before[name]
images=[]
for im in bpy.data.images:
 if im.packed_file:images.append({'name':im.name,'packed':True,'sha256':hashlib.sha256(im.packed_file.data).hexdigest()})
bpy.ops.wm.save_as_mainfile(filepath=str(H/'child-candidate.blend'),compress=True);export(H,'child-candidate.glb');write(O,'material-transfer-check.json',{'geometry_digest_before':before,'geometry_digest_after':{n:digest(bpy.data.objects[n].data)for n in before},'geometry_identical':True,'restored_materials':record['preserved_materials'],'packed_original_analytic_images':images,'scope':'Preserved existing per-piece analytic materials; no vendor image data or photo sampling','art_accepted':False})
