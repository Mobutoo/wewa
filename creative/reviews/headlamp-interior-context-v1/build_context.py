import bpy,json,pathlib,math,hashlib
from mathutils import Vector
R=pathlib.Path('/workspace/wewa'); D=R/'creative/reviews/headlamp-interior-context-v1'; A=R/'assets-src/moto-components/headlamp-interior-context-v1';A.mkdir(exist_ok=True)
inputs=json.loads((D/'native-inputs.json').read_text()); bpy.ops.wm.read_factory_settings(use_empty=True)
main=bpy.context.scene; main.name='CL201023_same_photo_unit_PROVISIONAL'
report={'new_geometry':False,'art_accepted':False,'G8':'pending','mounted_in_housing':False,'transforms':{},'source_hashes':{k:v['sha256'] for k,v in inputs.items()}}
for key in ['base','flange','capsule','housing','cage','cap']:
 with bpy.data.libraries.load(str(R/inputs[key]['path']),link=False) as (src,dst):dst.scenes=src.scenes
 source=dst.scenes[0]
 visible=[o for o in source.objects if o.type=='MESH' and not o.hide_render]
 scene=main if key in ['base','flange','capsule'] else bpy.data.scenes.new(key.upper()+'_ISOLATED_NOT_MOUNTED')
 coll=bpy.data.collections.new(key.upper());scene.collection.children.link(coll)
 report['transforms'][key]=[]
 for old in visible:
  ob=old.copy();ob.data=old.data.copy();coll.objects.link(ob);ob.name=key+'__'+old.name
  if key=='capsule':ob.location.z+=.0062
  report['transforms'][key].append({'name':ob.name,'matrix':[list(r) for r in ob.matrix_world],'offset_m':[0,0,.0062] if key=='capsule' else [0,0,0]})
 bpy.data.scenes.remove(source)
report['placement']={'base_flange':'Shared author axis +Z and z=0 unchanged. Same CL201023 photographic unit; relative face station approximate, no seating/weld claim.','capsule':'Exterior lower review cut translated +6.2mm to base mouth station; estimated collar overlap 0..3mm => allowable translation3.2..6.2mm. Numeric working range comes from partial native mouth, not source measurement.','housing_cage_cap':'Separate isolated scenes at original coordinates; no common transform supported. No mounted pose or focal depth assigned.'}
report['known_gaps']=['Main/pilot reflector depth and facets remain unknown','Flange inner-edge to base has an unresolved annular joint: no weld or hidden collar added','Capsule has no inner wall, filament or support','Bulb angular key orientation follows author flange only, not installed orientation','Housing/cage/cap compatibility and positions unknown']
bpy.context.window.scene=main
bpy.ops.object.select_all(action='DESELECT')
for o in main.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(A/'bulb-provisional.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_yup=True,export_extras=True)
main.render.engine='CYCLES';main.cycles.device='CPU';main.cycles.samples=96;main.cycles.use_denoising=True;main.render.threads_mode='FIXED';main.render.threads=2
main.render.resolution_x=720;main.render.resolution_y=720;main.render.resolution_percentage=100
main.world=bpy.data.worlds.new('Neutral');main.world.use_nodes=True;main.world.node_tree.nodes['Background'].inputs[0].default_value=(.15,.15,.15,1);main.world.node_tree.nodes['Background'].inputs[1].default_value=.5
main.view_settings.view_transform='AgX'
def point(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new('camera');c=bpy.data.objects.new('camera',cam);main.collection.objects.link(c);main.camera=c;cam.lens=65;cam.clip_start=.001;cam.clip_end=10
for name,loc,power,size in [('key',(.08,-.08,.1),12,.08),('rim',(-.08,.04,.07),9,.06)]:
 l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=size;o=bpy.data.objects.new(name,l);main.collection.objects.link(o);o.location=loc;point(o,(0,0,.02))
c.location=(.09,-.14,.085);point(c,(0,0,.018))
# Camera enclosure against evaluated geometry, before render.
bpy.context.view_layer.update();from bpy_extras.object_utils import world_to_camera_view
pts=[world_to_camera_view(main,c,o.matrix_world@Vector(v)) for o in main.objects if o.type=='MESH' for v in o.bound_box]
report['camera_preflight']={'inside':all(.02<p.x<.98 and .02<p.y<.98 and cam.clip_start<p.z<cam.clip_end for p in pts),'range':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]}
assert report['camera_preflight']['inside']
# Native meshes never emit. Keep original material parameters.
report['mesh_emission']={m.name:[list(n.inputs['Emission Color'].default_value) if 'Emission Color' in n.inputs else None,float(n.inputs['Emission Strength'].default_value) if 'Emission Strength' in n.inputs else None] for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'}
bpy.ops.wm.save_as_mainfile(filepath=str(A/'headlamp-context.blend'))
(D/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
