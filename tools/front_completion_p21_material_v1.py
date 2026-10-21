"""Clean related carrier appearance: observed cast/machined contrast, estimated response."""
import bpy,json,hashlib,sys,math
from pathlib import Path
R=Path('/workspace/wewa');old,key=sys.argv[sys.argv.index('--')+1:][:2];H=R/'assets-src/moto-components'/key;O=R/'creative/reviews'/key;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True);source=next((R/'assets-src/moto-components'/old).glob('*.blend'));bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.preferences.filepaths.save_version=0
mats=[]
for name,rough in [('Clean cast silver estimate',.42),('Visible machined silver estimate',.22)]:
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.62,.64,.66,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=1;mats.append(m)
bpy.ops.object.select_all(action='DESELECT');counts=[0,0]
for ob in bpy.data.objects:
 if ob.type!='MESH':continue
 ob.data.materials.clear()
 for m in mats:ob.data.materials.append(m)
 for p in ob.data.polygons:
  c=p.center;r=math.hypot(c.x,c.y);mouth=min(math.hypot(c.x-.047*math.cos(a),c.y-.047*math.sin(a))for a in [0,math.pi/2,math.pi,3*math.pi/2]);machined=(abs(c.z-.027)<.00001 and p.normal.z>.98)or(r<.0295 and c.z>.028)or(mouth<.0041 and c.z>.0225);p.material_index=int(machined);counts[p.material_index]+=1
 ob.select_set(True);bpy.context.view_layer.objects.active=ob
bpy.ops.wm.save_as_mainfile(filepath=str(H/'material.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/'material.glb'),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False);(O/'material-plan.json').write_text(json.dumps({'gray_source':str(source.relative_to(R)),'gray_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'appearance':{'base_color_linear':[.62,.64,.66,1],'metallic':1,'cast_roughness':{'working':.42,'bounds':[.30,.55]},'machined_roughness':{'working':.22,'bounds':[.15,.30]},'grain':'none invented','textures':'none','region_method':'Photographed machined mounting tops, upper collar and upper mounting mouths versus cast dish; geometric boundary interpretation remains estimated'},'face_counts_cast_machined':counts,'measured':False,'not_claimed':['exact alloy','surface metrology','hidden reverse finish','current RDC variant','mounted fit'],'art_accepted':False},indent=2))
