"""Only a linked inspection guide; zero newly fabricated physical components.

All installed positions/rake/clocking remain unverified. This deliberately
upright neutral guide separates axial gaps from a claimed motorcycle assembly.
Run only in a free short CPU slot; --render is optional and separately timed.
"""
from pathlib import Path
import json,hashlib,sys
import bpy
from mathutils import Vector,Matrix
D=Path(__file__).resolve().parent;R=D.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
native=json.loads((D/'source-inspection-surface-read-v1.json').read_text())
spacing=.175;wheel_z=.29
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
col=bpy.data.collections.new('CONTEXT_LINKED_INSPECTION_CANDIDATES_NOT_INSTALLED');s.collection.children.link(col)
rows=[];objects=[]
for r in native['rows']:
    source=R/r['source'];assert sha(source)==r['source_sha256']
    with bpy.data.libraries.load(str(source),link=True,relative=True)as(a,b):b.objects=[r['source_object']]
    original=b.objects[0];o=original.copy();o.name='CONDITIONAL GUIDE '+r['key'];col.objects.link(o)
    offset=(spacing/2,0,wheel_z)if r['key']=='fork-left'else(-spacing/2,0,wheel_z)if r['key']=='fork-right'else(0,0,0)
    o.matrix_world=Matrix.Translation(offset)@original.matrix_world
    o.hide_render=False;o.hide_set(False);objects.append(o)
    rows.append({'key':r['key'],'source':r['source'],'source_sha256':sha(source),'object':r['source_object'],
     'extra_neutral_translation_m':offset,'working_centre_spacing_m':spacing if'fork'in r['key']else None,
     'translation_or_clocking_measured':False,'geometry_created_or_modified':False})
axis=bpy.data.objects.new('PROVISIONAL AXLE LINE NOT HARDWARE',None);s.collection.objects.link(axis);axis.location=(0,0,wheel_z);axis.empty_display_type='ARROWS';axis.empty_display_size=.15
s.world=bpy.data.worlds.new('NEUTRAL GUIDE WORLD');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.18,.20,.23,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.3
for name,loc,power,size in [('KEY',(.5,-.5,1),18,.8),('FILL',(-.6,.2,.7),10,.7)]:
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,.3))-o.location).to_track_quat('-Z','Y').to_euler()
gray=bpy.data.materials.new('DIAGNOSTIC GRAY OVERRIDE NOT MATERIAL RECEIPT');gray.use_nodes=True;p=gray.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.22,.24,.26,1);p.inputs['Roughness'].default_value=.4
s.view_layers[0].material_override=gray
cam=bpy.data.objects.new('NEUTRAL INTERFACE CAMERA',bpy.data.cameras.new('NEUTRAL INTERFACE CAMERA'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.clip_start=.001;cam.data.clip_end=5
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.render.threads_mode='FIXED';s.render.threads=1
s.render.resolution_x=1100;s.render.resolution_y=850;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-.5
views=[('whole-quarter',(.85,-1,.78),(0,0,.34),.80,False),('axial-stack',(0,-.7,.29),(0,0,.29),.34,True)]
cam.location=views[0][1];cam.rotation_euler=(Vector(views[0][2])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=views[0][3]
# Relative library URIs are written against the new guide's own directory.
libraries=[]
for lib in bpy.data.libraries:
    absolute=Path(bpy.path.abspath(lib.filepath)).resolve();assert absolute.exists(),absolute
    lib.filepath=bpy.path.relpath(str(absolute),start=str(D));libraries.append({'uri':lib.filepath,'sha256':sha(absolute),'exists':True})
guide=D/'front-wheel-neutral-interface-v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(guide),compress=True,relative_remap=False)
report={'schema':1,'scope':'Linked inspection guide only, no new physical component, no installed pose or exact current RDC fit. Forks upright, not inferred rake. No tyre to avoid concealing axial interfaces.',
 'script_sha256':sha(Path(__file__)),'source_guide_sha256':sha(guide),'inputs':rows,'relative_libraries':libraries,
 'working_spacing_m_estimated':spacing,'working_spacing_range_m':[.150,.190],
 'axis_line_is_hardware':False,'guides_or_context_exported_as_hardware':False,'installed_contacts_verified':False,'art_accepted':False,'renders':[]}
if '--render'in sys.argv:
    sys.path.insert(0,str(R/'tools'))
    from blender_component_camera_preflight import check_component_camera
    for name,location,target,scale,crop in views:
        cam.location=location;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;bpy.context.view_layer.update()
        preflight=check_component_camera(s,objects,allow_crop=crop,margin=.005)
        png=D/(name+'.png');s.render.filepath=str(png);bpy.ops.render.render(write_still=True)
        report['renders'].append({'name':name,'PNG_sha256':sha(png),'samples':12,'resolution_px':[1100,850],'camera_preflight':preflight,'targeted_crop_not_complete_component':crop})
for r in rows:assert sha(R/r['source'])==r['source_sha256']
(D/'neutral-guide-report-v1.json').write_text(json.dumps(report,indent=2)+'\n')
print('NEUTRAL_INTERFACE_GUIDE_ONLY',sha(guide),flush=True)
