"""Three actual material views of unchanged linked exterior sources; no art receipt."""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
K='whole-exterior-material-preview-v5'
O=R/'creative/reviews'/K
H=R/'assets-src/moto-components'/K
O.mkdir(exist_ok=True)
H.mkdir(exist_ok=True)
raw=O/'raw'
raw.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
gray=R/'assets-src/moto-components/whole-exterior-coverage-v11/whole-exterior-coverage-v11.blend'
review=json.loads((R/'creative/reviews/whole-exterior-coverage-v11/coordinator-review.json').read_text())
assert review['actually_read']
parent=json.loads((R/'creative/reviews/whole-exterior-coverage-v11/linked-parents-check.json').read_text())
assert sha(gray)==parent['source_sha256']
for p in parent['parents']:
 assert sha(R/p['source'])==p['sha256']
 for dep in p.get('nested_sources',[]):assert sha(R/dep['source'])==dep['sha256']
bpy.ops.wm.open_mainfile(filepath=str(gray))
s=bpy.context.scene
s.view_layers[0].material_override=None
for ob in s.objects:
 if ob.type=='LIGHT':ob.hide_render=True
world=bpy.data.worlds.new('Artistic neutral HDRI, unchanged source materials')
world.use_nodes=True
nt=world.node_tree
tex=nt.nodes.new('ShaderNodeTexEnvironment')
tex.image=bpy.data.images.load(str(R/'app/public/materials/kloppenheim_06_puresky_1k.hdr'))
nt.links.new(tex.outputs['Color'],nt.nodes['Background'].inputs['Color'])
nt.nodes['Background'].inputs['Strength'].default_value=.65
s.world=world
center=Vector((0,.35,-.35))
s.camera.location=(2.9,-3,1)
s.camera.rotation_euler=(center-s.camera.location).to_track_quat('-Z','Y').to_euler()
s.cycles.samples=16
s['scope']='88 exact source parents, original materials, estimated placements; not finished motorcycle or final96'
bpy.context.preferences.filepaths.save_version=0
source=H/(K+'.blend')
bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
views=[]
for name,eye in [('material-left-quarter',(2.9,-3,1)),('material-right-quarter',(-2.9,-3,1)),('material-rear-quarter',(2.8,3.6,.8))]:
 s.camera.location=eye
 s.camera.rotation_euler=(center-s.camera.location).to_track_quat('-Z','Y').to_euler()
 s.render.image_settings.file_format='OPEN_EXR_MULTILAYER'
 s.render.image_settings.color_depth='32'
 s.render.filepath=str(raw/(name+'.exr'))
 bpy.ops.render.render(write_still=True)
 s.render.image_settings.file_format='PNG'
 s.render.image_settings.color_depth='8'
 bpy.data.images['Render Result'].save_render(str(O/(name+'.png')),scene=s)
 views.append(dict(name=name,camera_eye=list(eye),camera_target=list(center),samples=16,resolution_px=[1280,900],PNG_sha256=sha(O/(name+'.png')),EXR_sha256=sha(raw/(name+'.exr'))))
 report=dict(source=str(source.relative_to(R)),source_sha256=sha(source),gray_parent_source=str(gray.relative_to(R)),gray_parent_sha256=sha(gray),parents=parent['parents'],parent_count=88,views=views,HDRI='app/public/materials/kloppenheim_06_puresky_1k.hdr',HDRI_strength=.65,materials='Exact existing source materials retained; variant/calibration/fit limitations preserved',protocol_sha256=sha(Path(__file__)),art_accepted=False,whole_motorcycle_complete=False)
 (O/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
for p in parent['parents']:
 assert sha(R/p['source'])==p['sha256']
 for dep in p.get('nested_sources',[]):assert sha(R/dep['source'])==dep['sha256']
print('THREE_MATERIAL_VIEWS_SAVED')
