"""One rigid base-cover placement correction; old source and all meshes immutable."""
import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/mirror-right-v2';OLD=ROOT/'creative/reviews/mirror-right-v1';OUT.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=HERE/'mirror-right-v1.blend';old=json.loads((OLD/'source-geometry-check.json').read_text());assert sha(source)==old['source_sha256'];params=json.loads((HERE/'parameters-right-v2.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(source));collection=bpy.data.collections['WEWA_MIRROR_RIGHT'];objects=[o for o in collection.all_objects if o.type=='MESH'];name='RH hollow mirror mounting cover - estimated';cover=bpy.data.objects[name];before=list(cover.location);offset=params['base_cover_axial_offset_m_estimated'];assert abs(offset+.0063)<1e-10;cover.location.z+=offset;bpy.context.view_layer.update();checks=[]
for o in objects:
 bm=bmesh.new();bm.from_mesh(o.data);unseen=set(bm.verts);components=0
 while unseen:
  components+=1;stack=[unseen.pop()]
  while stack:
   for e in stack.pop().link_edges:
    for v in e.verts:
     if v in unseen:unseen.remove(v);stack.append(v)
 row={'object':o.name,'vertices':len(bm.verts),'faces':len(bm.faces),'components':components,'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_m3':bm.calc_volume(signed=True)};bm.free();assert row['components']==1 and row['non_manifold_edges']==0 and row['volume_m3']>0;checks.append(row)
 bpy.context.view_layer.objects.active=o
# Selection and export match immutablev1; no geometry/UV/normal/material rebuild.
bpy.ops.object.select_all(action='DESELECT')
for o in collection.all_objects:o.select_set(True)
bpy.context.view_layer.objects.active=cover;export=HERE/'mirror-right-v2.glb';bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_apply=True,export_tangents=True);dest=HERE/'mirror-right-v2.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
report=dict(old);report.update({'phase':'full v2 candidate; only base-cover rigid placement changed','source_sha256':sha(dest),'export_sha256':sha(export),'geometry':checks,'inherited_CSG_from_v1_no_CSG_reexecuted':True,'prior_source_sha256':old['source_sha256'],'prior_export_sha256':old['export_sha256'],'change':{'object':name,'translation_before_world_m':before,'translation_after_world_m':list(cover.location),'delta_world_m':[0,0,offset],'source_mesh_UV_normals_materials_edited':False,'cover_bottom_q_m_estimated':.020+offset,'nut_top_q_m_estimated':.0133,'gap_m_estimated':.020+offset-.0133,'interpretation':'Related-photo qualitative spacing correction; no calibrated photo distance, exact RDC fit or thread qualification.'}});(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');assert sha(source)==old['source_sha256'];print('RIGHT_V2_RIGID_COVER',report['source_sha256'],report['export_sha256'],report['change'])
