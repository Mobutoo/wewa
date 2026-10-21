"""Frozen gasket1 macro, same camera/lights, isolated material controls in RAM only."""
from pathlib import Path
import bpy,json,sys,hashlib
from mathutils import Matrix
D=Path(__file__).resolve().parent;R=D.parents[3];H=R/'assets-src/moto-components/exhaust-header-gasket';O=R/'creative/reviews/exhaust-header-gasket-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();source=H/'exhaust-header-gasket-v1.blend';b=json.loads((H/'build-report.json').read_text());assert sha(source)==b['source_sha256'];cp=json.loads((O/'annular-raised-region-detail.checkpoint.json').read_text());assert cp['source_sha256']==sha(source);config=cp['configuration'];args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];variant=args[args.index('--variant')+1]if'--variant'in args else'baseline';assert variant in ['baseline','normal-unlinked-only','roughness-constant-only'];sys.path.insert(0,str(H));from render_checkpoint import checkpoint_view
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.camera.matrix_world=Matrix(config['camera_world_matrix']);s.camera.data.lens=config['lens_mm'];s.camera.data.clip_start=config['camera_clip_m'][0];s.camera.data.clip_end=config['camera_clip_m'][1];s.render.resolution_x=config['resolution'][0];s.render.resolution_y=config['resolution'][1];s.render.resolution_percentage=config['resolution'][2];s.cycles.samples=12
for q in config['lights']:
 o=bpy.data.objects[q['name']];o.matrix_world=Matrix(q['matrix']);o.data.energy=q['energy'];o.data.size=q['size']
o=bpy.data.objects[b['geometry'][0]['name']];mat=o.data.materials[0];p=mat.node_tree.nodes.get('Principled BSDF');links=mat.node_tree.links;changed=[]
if variant=='normal-unlinked-only':
 for link in list(p.inputs['Normal'].links):changed.append({'removed_link':[link.from_node.name,link.from_socket.name,link.to_socket.name]});links.remove(link)
if variant=='roughness-constant-only':
 for link in list(p.inputs['Roughness'].links):changed.append({'removed_link':[link.from_node.name,link.from_socket.name,link.to_socket.name]});links.remove(link)
 p.inputs['Roughness'].default_value=.37;changed.append({'roughness_constant':.37})
bpy.context.view_layer.update();out=D/'native12';q=checkpoint_view(s,out,source,variant);r={'source_sha256':sha(source),'export_sha256':b['export_sha256'],'original_macro_checkpoint_sha256':sha(O/'annular-raised-region-detail.checkpoint.json'),'variant':variant,'samples':12,'resolution_camera_lights_from_actual_final_checkpoint':True,'changed_in_memory_only':changed,'geometry_modified':False,'source_saved':False,'outputs':q['outputs'],'art_accepted':False};(out/(variant+'.diagnostic.json')).write_text(json.dumps(r,indent=2)+'\n');assert sha(source)==b['source_sha256'];print('GASKET_DIAGNOSTIC',variant,flush=True)
