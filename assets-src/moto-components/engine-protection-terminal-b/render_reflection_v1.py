"""Neutral reflective whole/profile/fold G3views; original source never saved."""
from pathlib import Path
import bpy,json,hashlib,sys
import numpy as np
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-protection-terminal-b-v1';sys.path.insert(0,str(H));from camera_preflight import check_component_camera
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();a=json.loads((O/'source-geometry-check.json').read_text());b=json.loads((O/'geometry-check.json').read_text());src=H/'engine-protection-terminal-b-v1.blend';glb=H/'engine-protection-terminal-b-inspection.glb';assert b['technical_passed']and a['source_sha256']==b['source_sha256']==sha(src)and a['export_sha256']==b['export_sha256']==sha(glb)
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;obs=list(bpy.data.collections['WEWA_ENGINE_PROTECTION_TERMINAL_B_ISOLATED'].objects);centre=np.mean(np.array(a['bounds_m']),axis=0);s.cycles.samples=24;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100
for o in obs:
 for mat in o.data.materials:
  p=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(.24,.24,.24,1);p.inputs['Metallic'].default_value=.8;p.inputs['Roughness'].default_value=.20
shift=np.array(a['origin_shift_from_developed_mapping_m']);fold=np.array([0.,.0055,.025])-shift
views=[('quarter',centre+(.12,-.22,.10),centre,.14,False),('profile',centre+(.25,0.,0.),centre,.14,False),('doublebend-detail',fold+(.07,-.15,.07),fold,.045,True)]
report={'source_sha256':sha(src),'export_sha256':sha(glb),'render_script_sha256':sha(Path(__file__)),'views':[],'samples':24,'scope':'First actualG3gray, lowerperforation/back/metric and contact reserved; no material or artreceipt','art_accepted':False,'material_override_scope':'Temporary reflective gray only; not finished metal or measured reflectance'}
for name,eye,target,scale,crop in views:
 s.camera.location=eye;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;bpy.context.view_layer.update();pre=check_component_camera(s,obs,allow_crop=crop,margin=.005);png=O/('reflection-'+name+'.png');s.render.filepath=str(png);bpy.ops.render.render(write_still=True)
 row={'source_sha256':sha(src),'export_sha256':sha(glb),'render_script_sha256':sha(Path(__file__)),'view':name,'samples':24,'resolution_px':[1400,1000],'camera_eye_m':list(eye),'camera_target_m':list(target),'ortho_scale_m':scale,'camera_preflight':pre,'exposure_EV':s.view_settings.exposure,'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,'world_color_linear':list(s.world.node_tree.nodes['Background'].inputs[0].default_value),'world_strength':s.world.node_tree.nodes['Background'].inputs[1].default_value,'lights':[{'name':o.name,'location_m':list(o.location),'rotation_rad':list(o.rotation_euler),'shape':o.data.shape,'power_W':o.data.energy,'size_m':o.data.size}for o in s.objects if o.type=='LIGHT'],'PNG_sha256':sha(png),'PNG_bytes':png.stat().st_size,'source_saved':False,'art_accepted':False,'material_override_scope':'Temporary reflective gray only; not finished metal or measured reflectance'};png.with_suffix('.json').write_text(json.dumps(row,indent=2)+'\n');report['views'].append(row);(O/'reflection-render-report-v1.json').write_text(json.dumps(report,indent=2)+'\n')
assert sha(src)==a['source_sha256'];print('TERMINAL_B_REFLECTION_COMPLETE',flush=True)
