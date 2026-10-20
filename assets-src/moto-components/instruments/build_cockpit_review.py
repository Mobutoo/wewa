"""Linked-source inspection assembly, not an accepted motorcycle or game scene."""
import bpy,hashlib,json,math,os
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];DEST=HERE.parent/'cockpit-review';DEST.mkdir(exist_ok=True)
OUT=ROOT/'creative/reviews/cockpit-v1';OUT.mkdir(exist_ok=True)
configs=[('instruments',HERE/'instruments-v1.blend','WEWA_INSTRUMENTS_SEPARATE_PARTS','instruments-v1'),('handlebar',HERE.parent/'handlebar/handlebar-v1.blend','WEWA_BARE_HANDLEBAR','handlebar-v1'),('grips',HERE.parent/'handlebar-grips/handlebar-grips-v1.blend','WEWA_HANDLEBAR_GRIP_ENVELOPES','handlebar-grips-v1')]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;objects={};sources=[]
for key,path,collection_name,revision in configs:
 check=json.loads((ROOT/'creative/reviews'/revision/'source-geometry-check.json').read_text());assert check['source_sha256']==hashlib.sha256(path.read_bytes()).hexdigest()
 with bpy.data.libraries.load(str(path),link=True) as (available,loaded):assert collection_name in available.collections;loaded.collections=[collection_name]
 collection=loaded.collections[0];local=bpy.data.collections.new('COCKPIT '+key);scene.collection.children.link(local);copies={o:o.copy() for o in collection.objects}
 for original,copy in copies.items():
  local.objects.link(copy);copy.parent=copies.get(original.parent);copy.name='COCKPIT '+original.name;copy['source_object_name']=original.name;copy['source_component']=key
 objects[key]=list(copies.values());sources.append({'component':key,'source':str(path.relative_to(ROOT)),'sha256':check['source_sha256'],'object_count':len(copies)})
for obj in objects['instruments']:
 if obj['source_object_name']=='SPEED_NEEDLE_PIVOT':obj.rotation_euler.z=math.radians(225-42*270/140)
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
def tree(obj):
 e=obj.evaluated_get(deps);m=e.to_mesh();world=obj.matrix_world;result=BVHTree.FromPolygons([world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);e.to_mesh_clear();return result
bar=tree(next(o for o in objects['handlebar'] if o.type=='MESH'));crossings=[]
for obj in objects['grips']:
 if obj.type=='MESH':crossings.append({'object':obj['source_object_name'],'bar_surface_crossings':len(bar.overlap(tree(obj)))})
for obj in objects['instruments']:
 if obj.type=='MESH' and obj.get('structural_closed_volume'):crossings.append({'object':obj['source_object_name'],'bar_surface_crossings':len(bar.overlap(tree(obj)))})
assert not any(r['bar_surface_crossings'] for r in crossings),crossings
# This is a surface-crossing check only. It does not validate the absent clamps,
# throttle carrier, instrument bracket, cables, controls or wiring.
studio=bpy.data.collections.new('COCKPIT_STUDIO_NOT_EXPORTED');scene.collection.children.link(studio)
world=bpy.data.worlds.new('Cockpit HDR studio');world.use_nodes=True;scene.world=world;nodes=world.node_tree.nodes;env=nodes.new('ShaderNodeTexEnvironment');env.image=bpy.data.images.load(str(ROOT/'app/public/materials/kloppenheim_06_puresky_1k.hdr'));env.image.pack();world.node_tree.links.new(env.outputs['Color'],nodes['Background'].inputs['Color']);nodes['Background'].inputs['Strength'].default_value=.30
for name,location,energy,size in [('COCKPIT_KEY',(-.6,-.2,1),60,.45),('COCKPIT_FILL',(.6,-.05,.65),30,.50)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size;o=bpy.data.objects.new(name,data);studio.objects.link(o);o.location=location;o.rotation_euler=(Vector((0,-.03,.08))-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('COCKPIT_CAMERA',bpy.data.cameras.new('COCKPIT_CAMERA'));studio.objects.link(cam);scene.camera=cam;cam.location=(0,.67,.49);cam.rotation_euler=(Vector((0,-.03,.07))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=28
scene.render.engine='CYCLES';scene.cycles.samples=128;scene.cycles.use_denoising=False;scene.cycles.caustics_reflective=False;scene.cycles.caustics_refractive=False;scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
scene['scope']='Inspection assembly of three separate candidates, all dimensions provisional. Missing clamps/controls/mirrors/cables/visor/rider; no game scene.'
path=DEST/'cockpit-review-v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
for lib in bpy.data.libraries:lib.filepath='//'+os.path.relpath(Path(bpy.path.abspath(lib.filepath)),DEST)
bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
report={'scope':scene['scope'],'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'linked_components':sources,'source_libraries_relative':True,'bar_surface_checks':crossings,'preview_pose':{'speed_kmh':42,'fuel_fraction':.65},'installed_fit_verified':False,'art_accepted':False,'physical_iphone_tested':False}
(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');print('WEWA_COCKPIT_REVIEW_SOURCE',json.dumps(report))
