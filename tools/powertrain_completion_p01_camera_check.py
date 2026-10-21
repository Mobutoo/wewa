import bpy,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];O=R/'creative/reviews/side-cover-left-v2';s=bpy.context.scene;cam=s.camera
rows=[]
for name,eye in [('profile',(0,0,.5)),('quarter',(.24,.12,.46)),('edge',(-.34,-.13,.20))]:
 cam.location=eye;cam.rotation_euler=(Vector((0,0,.007))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.48;bpy.context.view_layer.update()
 pts=[]
 for ob in s.objects:
  if ob.type!='MESH':continue
  evaluated=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=evaluated.to_mesh()
  for v in m.vertices:pts.append(world_to_camera_view(s,cam,evaluated.matrix_world@v.co))
  evaluated.to_mesh_clear()
 lo=[min(v[i]for v in pts)for i in range(3)];hi=[max(v[i]for v in pts)for i in range(3)]
 assert lo[0]>.01 and lo[1]>.01 and hi[0]<.99 and hi[1]<.99
 assert lo[2]>cam.data.clip_start and hi[2]<cam.data.clip_end
 rows.append(dict(view=name,eye=list(eye),min=lo,max=hi,actual_evaluated_vertices=len(pts),clip=[cam.data.clip_start,cam.data.clip_end],whole_component_framed=True))
(O/'camera-preflight.json').write_text(json.dumps(dict(views=rows,scope='Actual evaluated source mesh vertices projected for saved protocol cameras; not photo camera calibration',art_accepted=False),indent=2)+'\n')
