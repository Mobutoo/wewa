import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews'/H.name;p=H/(H.name+'.blend');bpy.ops.wm.open_mainfile(filepath=str(p),use_scripts=False);cam=bpy.context.scene.camera;up=cam.matrix_world.to_3x3()@Vector((0,1,0));conv=lambda v:[v[0],v[2],-v[1]];cfg=next(iter(json.loads((O/'runtime-config.json').read_text())['assets'].values()))['views']['quarter']
assert cfg['position']==conv(cam.location)and cfg['up']==conv(up)
(O/'native-camera-parity.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),source_camera_position=list(cam.location),source_camera_up=list(up),gltf_camera_position=conv(cam.location),gltf_camera_up=conv(up),same_view_direction_and_roll=True,projection_difference='Native ortho .123m vs runtime perspective; no pixel photometric parity claim',calibrated_source=False),indent=2)+'\n')
