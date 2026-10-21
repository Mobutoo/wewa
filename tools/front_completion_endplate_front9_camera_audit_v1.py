import bpy,sys,json,runpy,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');K='front-completion-p23-endplate-front9-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K
check=runpy.run_path(str(R/'tools/blender_component_camera_preflight.py'))['check_component_camera'];bpy.ops.wm.open_mainfile(filepath=str(H/'endplate-gray.blend'));s=bpy.context.scene;objects=[o for o in bpy.data.objects if o.type=='MESH'];coords=[o.matrix_world@Vector(p)for o in objects for p in o.bound_box];low=Vector([min(p[i]for p in coords)for i in range(3)]);high=Vector([max(p[i]for p in coords)for i in range(3)]);target=(low+high)/2;size=max(high-low);cam=bpy.data.objects.new('Audit replay',bpy.data.cameras.new('Audit replay'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=size*1.65;cam.data.clip_start=size*.001;cam.data.clip_end=size*100;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;rows=[]
for name,d in [('gray-quarter',(.7,-1,2)),('reflection',(1,-1,1.5))]:
 cam.location=target+size*Vector(d);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.view_layers[0].update();rows.append({'view':name,'preflight':check(s,objects)})
(O/'camera-audit.json').write_text(json.dumps({'method':'Replay exact common camera settings used for gray/material rendering; independent evaluated vertex preflight','protocol_sha256':hashlib.sha256((R/'tools/front_completion_endplate_front9_render_v1.py').read_bytes()).hexdigest(),'views':rows},indent=2))
