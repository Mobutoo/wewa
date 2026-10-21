"""Two actual same-camera gray macros before any v3 material/final96 work."""
from pathlib import Path
import bpy,hashlib,json,sys
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/front-tyre-v3'
sys.path.insert(0,str(H));from camera_preflight import check_component_camera
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();src=json.loads((O/'diagnostic-source-geometry-check.json').read_text());check=json.loads((O/'diagnostic-export-preflight.json').read_text())
assert check['technical_preflight_passed']and check['source_sha256']==src['source_sha256']and check['export_sha256']==src['export_sha256']
source=R/src['source_path'];assert sha(source)==src['source_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;candidate=bpy.data.collections[src['collection']].objects[0];gray=candidate.data.materials[0]
P=json.loads((H/'parameters.json').read_text());baseline=R/P['original_geometry_source'];assert sha(baseline)==P['source_sha256']
with bpy.data.libraries.load(str(baseline),link=False)as(a,b):b.objects=[P['original_inspection_object']]
old=b.objects[0];s.collection.objects.link(old);old.hide_set(False);old.hide_render=True;old.data.materials.clear();old.data.materials.append(gray)
s.cycles.samples=24;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
eye=(.075,-.17,.69);target=(.012,-.10,.562);s.camera.location=eye;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=.05
fixture={'source_sha256':sha(source),'export_sha256':src['export_sha256'],'baseline_source_sha256':sha(baseline),'render_script_sha256':sha(Path(__file__)),
 'camera_eye_m':eye,'camera_target_m':target,'ortho_scale_m':.05,'samples':24,'resolution_px':[1400,1100],'exposure_EV':s.view_settings.exposure,
 'gamma':s.view_settings.gamma,'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,
 'world_color_linear':list(s.world.node_tree.nodes['Background'].inputs['Color'].default_value),'world_strength':s.world.node_tree.nodes['Background'].inputs['Strength'].default_value,
 'lights':[{'name':x.name,'location_m':list(x.location),'rotation_rad':list(x.rotation_euler),'shape':x.data.shape,'power_W':x.data.energy,'size_m':x.data.size}for x in s.objects if x.type=='LIGHT']}
report={**fixture,'scope':'Diagnostic gray same-camera comparison, not production/art or20umcriterion receipt; no map material/final96.','views':[],'art_accepted':False}
for name,visible,hidden in [('diagnostic-gray-baseline',old,candidate),('diagnostic-gray-candidate',candidate,old)]:
    visible.hide_render=False;hidden.hide_render=True;bpy.context.view_layer.update();pre=check_component_camera(s,[visible],allow_crop=True,margin=.005)
    png=O/(name+'.png');cp=O/(name+'.json');config={**fixture,'name':name,'actual_object':visible.name,'camera_preflight':pre}
    s.render.filepath=str(png);bpy.ops.render.render(write_still=True)
    q={**config,'PNG_sha256':sha(png),'PNG_bytes':png.stat().st_size,'source_saved':False};cp.write_text(json.dumps(q,indent=2)+'\n');report['views'].append(q)
    (O/'diagnostic-gray-comparison-report.json').write_text(json.dumps(report,indent=2)+'\n')
assert sha(source)==src['source_sha256']and sha(baseline)==P['source_sha256']
print('FRONT_TYRE_DIAGNOSTIC_GRAY_PAIR_COMPLETE',flush=True)
