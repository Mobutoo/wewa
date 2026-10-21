import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa-github');H=R/'assets-src/moto-components/frame/front-backbone';O=R/'creative/reviews/frame-front-backbone-edge-diagnostic-v1';O.mkdir(exist_ok=True);p=H/'frame-front-backbone-v1.blend';e=H/'frame-front-backbone-inspection.glb';ss=hashlib.sha256(p.read_bytes()).hexdigest();es=hashlib.sha256(e.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene
removed=[]
for m in bpy.data.materials:
 if not m.use_nodes:continue
 for n in m.node_tree.nodes:
  if n.type=='BSDF_PRINCIPLED':
   for link in list(n.inputs['Normal'].links):m.node_tree.links.remove(link);removed.append(m.name)
s.camera.location=(.10,-.12,.06);s.camera.rotation_euler=(Vector((0,.01,-.003))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=.105;s.camera.data.clip_start=.001;s.render.resolution_x=1400;s.render.resolution_y=900;s.render.resolution_percentage=100;s.cycles.samples=32;s.cycles.use_denoising=True;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.50;s.render.border_max_x=1.;s.render.border_min_y=0;s.render.border_max_y=1.;s.render.filepath=str(O/'source-without-normalmap.png');bpy.ops.render.render(write_still=True)
j={'source_sha256':ss,'export_sha256':es,'removed_normal_links_RAM_only':removed,'source_geometry_or_normals_modified':False,'source_material_roughness_and_lights_preserved':True,'camera':'Same front-opening finalview; crop right half, no resampling','samples':32,'denoising':'OIDN','PNG_sha256':hashlib.sha256(Path(s.render.filepath).read_bytes()).hexdigest(),'source_or_export_modified':False,'art_accepted':False};assert hashlib.sha256(p.read_bytes()).hexdigest()==ss and hashlib.sha256(e.read_bytes()).hexdigest()==es;(O/'report.json').write_text(json.dumps(j,indent=2)+'\n')
