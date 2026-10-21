"""Additional native96 mouth view of the same frozen sleeve source; no source mutation."""
import bpy,sys,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import bounds,look,sha,write,R
H=R/'assets-src/moto-components/footrest-rubber-v1';O=R/'creative/reviews/footrest-rubber-v1';bpy.ops.wm.open_mainfile(filepath=str(H/'child-candidate.blend'));s=bpy.context.scene;c,size,lo,hi=bounds();s.camera.location=c+Vector((-2,.4,.8))*size;look(s.camera,c);bpy.context.view_layer.update();pts=[world_to_camera_view(s,s.camera,ob.matrix_world@v.co)for ob in s.objects if ob.type=='MESH'for v in ob.data.vertices];mn=[min(v[i]for v in pts)for i in range(3)];mx=[max(v[i]for v in pts)for i in range(3)];assert min(mn[:2])>.01 and max(mx[:2])<.99 and mn[2]>s.camera.data.clip_start and mx[2]<s.camera.data.clip_end
s.cycles.samples=96;s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(O/'raw/final-mouth.exr');bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/'final-mouth.png'),scene=s);write(O,'final-mouth-render-report.json',dict(view='final-mouth',samples=96,resolution_px=[900,700],png_sha256=sha(O/'final-mouth.png'),source_sha256=sha(H/'child-candidate.blend'),camera=list(s.camera.location),target=list(c),actual_vertex_frame_min=mn,actual_vertex_frame_max=mx,protocol_sha256=sha(Path(__file__)),art_accepted=False))
