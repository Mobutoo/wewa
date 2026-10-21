"""G4 USB appearance study derived from the frozen gray shape, not OEMCAD."""
import bpy,bmesh,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/instruments-usb-v2-material-study-r2';OUT.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(HERE));from usb_g4_v2 import apply_materials
from v2_artwork_helpers import filled_curve
G3=ROOT/'creative/reviews/instruments-usb-v2-study-r2';gray=json.loads((G3/'source-geometry-check.json').read_text());read=json.loads((G3/'preview-review.json').read_text());assert read['passed_for_diffuse_shape_preview']and read['source_sha256']==gray['source_sha256'];source=HERE/'instruments-usb-v2-study-r2.blend';assert hashlib.sha256(source.read_bytes()).hexdigest()==gray['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));parts=bpy.data.collections['WEWA_INSTRUMENT_USB_STUDY_V2'];parts.name='WEWA_INSTRUMENT_USB_MATERIAL_STUDY_V2';root=bpy.data.objects['INSTRUMENT_USB_STUDY_MOUNT'];root.name='INSTRUMENT_USB_MATERIAL_STUDY_MOUNT';objects={'surround':bpy.data.objects['USB contoured surround - closed v2'],'capsule':bpy.data.objects['USB inset capsule face - closed v2']}
def geometry(o):return hashlib.sha256(json.dumps({'vertices':[list(v.co)for v in o.data.vertices],'faces':[list(f.vertices)for f in o.data.polygons]},separators=(',',':')).encode()).hexdigest()
before={k:geometry(o)for k,o in objects.items()};materials=apply_materials(objects,HERE);assert before=={k:geometry(o)for k,o in objects.items()}
# The photograph reveals a rectangle and oblique interior mark; manufacturing
# process and meaning are unconfirmed. This is low-contrast surface geometry.
mat=bpy.data.materials.new('USB observed motif low-contrast black - process unknown');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.002,.0025,.003,1);bs.inputs['Roughness'].default_value=.64;guides=bpy.data.collections.new('USB original editable motif contours v2');bpy.context.scene.collection.children.link(guides);guides.hide_render=True
symbolpath=ROOT/'creative/research/instruments-v2/usb-symbol-v2.json';symbol=json.loads(symbolpath.read_text());tree=BVHTree.FromPolygons([v.co for v in objects['capsule'].data.vertices],[tuple(p.vertices)for p in objects['capsule'].data.polygons]);marks=[]
for spec in symbol['parts']:
 o=filled_curve('EDITABLE USB '+spec['name']+' v2',spec['metric_outline_loops'],mat,guides,None);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();mesh=bpy.data.meshes.new_from_object(o.evaluated_get(deps),depsgraph=deps)
 for v in mesh.vertices:
  hit=tree.ray_cast(Vector((v.co.x,v.co.y,.10)),Vector((0,0,-1)),.2);assert hit[0]is not None,(o.name,list(v.co));v.co=hit[0]+hit[1]*.000020
 mesh.calc_loop_triangles();assert all(len(f.vertices)==3 for f in mesh.polygons);keep=[];removed=[]
 for f in mesh.polygons:
  a,b,c=[mesh.vertices[i].co for i in f.vertices];area=(b-a).cross(c-a).length/2
  (removed if area==0 else keep).append(f)
 clean=bpy.data.meshes.new('USB '+spec['name']+' surface v2');clean.from_pydata([list(v.co)for v in mesh.vertices],[],[tuple(f.vertices)for f in keep]);clean.materials.append(mat);clean.update();bm=bmesh.new();bm.from_mesh(clean);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(clean);bm.free()
 visible=bpy.data.objects.new('USB '+spec['name']+' v2',clean);parts.objects.link(visible);visible.parent=root;visible['structural_closed_volume']=False;visible['surface_marking_process_unknown']=True
 for f in clean.polygons:f.use_smooth=True
 o.hide_render=True;o.hide_set(True);marks.append({'object':visible.name,'editable_curve':o.name,'triangles_retained':len(keep),'exact_zero_area_faces_removed':len(removed),'positive_area_faces_removed':0,'surface_offset_m_estimated':.000020,'meaning':'unknown'});bpy.data.meshes.remove(mesh)
# Lighting changed as a documented appearance protocol, no geometry deformation.
for o in bpy.data.collections['USB_STUDY_STUDIO_NOT_EXPORTED'].objects:
 if o.type=='LIGHT':o.data.energy*=2
bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT')
for o in parts.objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects['surround'];glb=HERE/'instruments-usb-v2-material-study-r2.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True,export_tangents=True);path=HERE/'instruments-usb-v2-material-study-r2.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
report={'schema':1,'source_path':str(path.relative_to(ROOT)),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'export_path':str(glb.relative_to(ROOT)),'export_sha256':hashlib.sha256(glb.read_bytes()).hexdigest(),'gray_source_sha256':gray['source_sha256'],'gray_export_sha256':gray['export_sha256'],'gray_body_positions_faces_bit_identical':True,'gray_body_geometry_sha256':before,'bodies':gray['bodies'],'materials_and_UV':materials,'surface_marks':marks,'symbol_vector_path':str(symbolpath.relative_to(ROOT)),'symbol_vector_sha256':hashlib.sha256(symbolpath.read_bytes()).hexdigest(),'material_measurement_status':'Estimated BRDF, grain and material split; no measured manufacturer finish','collection':parts.name,'root':root.name,'studio_light_power_multiplier_vs_gray':2,'whole_instrument_interface_not_yet_tested':True,'art_accepted':False};(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');print('USB_MATERIAL_STUDY',report['source_sha256'],report['export_sha256'])
