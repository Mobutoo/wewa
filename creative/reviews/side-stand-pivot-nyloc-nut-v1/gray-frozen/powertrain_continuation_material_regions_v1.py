"""Apply documented proposed object-region PBR materials without geometry mutation."""
import bpy,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import digest,export,write
R=Path(__file__).resolve().parents[1];name=sys.argv[sys.argv.index('--')+1];H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name
assert not (O/'delivery.json').exists();assert json.loads((O/'gray-review.json').read_text())['read_for_exterior_study'];P=json.loads((H/'parameters.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(H/'child-gray.blend'));before={o.name:digest(o.data)for o in bpy.context.scene.objects if o.type=='MESH'and not o.hide_render};regions=P['material_regions'];assert set(before)==set(regions)
for ob in bpy.context.scene.objects:
 if ob.name not in before:continue
 p=regions[ob.name];m=bpy.data.materials.new(p['name']);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=p['base_color_linear'];b.inputs['Metallic'].default_value=p['metallic'];b.inputs['Roughness'].default_value=p['roughness'];ob.data.materials.clear();ob.data.materials.append(m)
after={o.name:digest(o.data)for o in bpy.context.scene.objects if o.name in before};assert before==after;bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(H/'child-candidate.blend'),compress=True);export(H,'child-candidate.glb');write(O,'material-transfer-check.json',dict(geometry_digest_before=before,geometry_digest_after=after,geometry_identical=True,regions=regions,scope='Proposed physical-region PBR separation only, no measured chemistry/optics/grain or vendor pixels',art_accepted=False))
