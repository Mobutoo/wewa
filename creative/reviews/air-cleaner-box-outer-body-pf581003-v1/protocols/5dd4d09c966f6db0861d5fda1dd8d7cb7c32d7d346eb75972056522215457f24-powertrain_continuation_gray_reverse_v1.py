"""Read-only opposite gray16 capture for physically asymmetric outer bodies, actual same source rig."""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import bounds,look,digest
R=Path(__file__).resolve().parents[1];name=sys.argv[sys.argv.index('--')+1];H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;source=H/'child-gray.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(source)
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;c,size,_,_=bounds();direction=Vector((1,-.7,-2.7));s.camera.location=c+direction*size;look(s.camera,c);bpy.context.view_layer.update();mesh_before={o.name:digest(o.data)for o in s.objects if o.type=='MESH'}
pts=[world_to_camera_view(s,s.camera,o.matrix_world@v.co)for o in s.objects if o.name in mesh_before for v in o.data.vertices];lo=[min(p[i]for p in pts)for i in range(3)];hi=[max(p[i]for p in pts)for i in range(3)];assert min(lo[:2])>.01 and max(hi[:2])<.99
s.cycles.samples=16;label='gray-reverse';(O/'raw').mkdir(exist_ok=True);s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(O/'raw'/(label+'.exr'));bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/(label+'.png')),scene=s)
assert sha(source)==before and all(digest(bpy.data.objects[n].data)==d for n,d in mesh_before.items())
(O/'gray-reverse-render-report.json').write_text(json.dumps(dict(view=label,samples=16,resolution_px=[900,700],png=label+'.png',png_sha256=sha(O/(label+'.png')),exr='raw/'+label+'.exr',source_sha256=before,source_unchanged=True,geometry_unchanged=True,direction_source=list(direction),actual_frame_min=lo,actual_frame_max=hi,protocol_sha256=sha(Path(__file__)),art_accepted=False),indent=2)+'\n')
