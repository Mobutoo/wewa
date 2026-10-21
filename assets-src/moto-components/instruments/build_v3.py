"""Only two closed lens normal splits after read-only causal witnesses.
Historical v1/v2, all positions, topology, UV, materials and controls untouched.
"""
import bpy,bmesh,json,hashlib,math,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/instruments-v3';OUT.mkdir(parents=True,exist_ok=True);OLD=ROOT/'creative/reviews/instruments-v2';source=HERE/'instruments-v2.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();old=json.loads((OLD/'source-geometry-check.json').read_text());read=json.loads((ROOT/'creative/research/instruments-v2/optical-edge-diagnostic-reading.json').read_text());assert sha(source)==old['source_sha256']==read['source_sha256']and read['all_five_actual_previews_read'];bpy.ops.wm.open_mainfile(filepath=str(source));parts=bpy.data.collections['WEWA_INSTRUMENTS_SEPARATE_PARTS'];changed=['SPEED clear closed lens','FUEL_GEAR clear closed lens'];checks=[]
def signature(o):
 m=o.data;return hashlib.sha256(json.dumps({'positions':[list(v.co)for v in m.vertices],'faces':[list(p.vertices)for p in m.polygons],'UV':[[list(x.uv)for x in u.data]for u in m.uv_layers],'matrix':[list(r)for r in o.matrix_world],'materials':[m.name for m in m.materials]},separators=(',',':')).encode()).hexdigest()
for name in changed:
 o=bpy.data.objects[name];before=signature(o);old_edges=sum(e.use_edge_sharp for e in o.data.edges);o.data.set_sharp_from_angle(angle=math.radians(30));o.data.update();assert signature(o)==before;checks.append({'object':name,'source_positions_topology_UV_matrix_materials_sha256_before':before,'source_positions_topology_UV_matrix_materials_sha256_after':signature(o),'geometry_UV_matrix_materials_bit_identical':True,'sharp_edges_before':old_edges,'sharp_edges_after':sum(e.use_edge_sharp for e in o.data.edges),'crease_threshold_degrees_working':30})
bpy.context.view_layer.update();bodies=[]
for o in parts.objects:
 if not o.get('structural_closed_volume',False)and o.name not in ['USB contoured surround - closed v2','USB inset capsule face - closed v2']:continue
 deps=bpy.context.evaluated_depsgraph_get();m=bpy.data.meshes.new_from_object(o.evaluated_get(deps),depsgraph=deps);bm=bmesh.new();bm.from_mesh(m);remaining=set(bm.verts);components=0
 while remaining:
  components+=1;stack=[remaining.pop()]
  while stack:
   for e in stack.pop().link_edges:
    for v in e.verts:
     if v in remaining:remaining.remove(v);stack.append(v)
 row={'object':o.name,'components':components,'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_m3':bm.calc_volume(signed=True)};bm.free();bpy.data.meshes.remove(m);assert row['components']==1 and row['non_manifold_edges']==0 and row['volume_m3']>0,row;bodies.append(row)
bpy.ops.object.select_all(action='DESELECT')
for o in parts.objects:o.select_set(True)
bpy.context.view_layer.objects.active=bpy.data.objects['INSTRUMENT_CLUSTER_MOUNT'];glb=HERE/'instruments-v3-inspection.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True,export_tangents=True);subprocess.run(['node',str(HERE/'finalize_export_v3.mjs')],cwd=ROOT,check=True);dest=HERE/'instruments-v3.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True);report={'schema':1,'revision':'instruments-v3','source_sha256':sha(dest),'export_sha256':sha(glb),'baseline_source_sha256':old['source_sha256'],'baseline_export_sha256':old['export_sha256'],'collection':parts.name,'root':'INSTRUMENT_CLUSTER_MOUNT','changed_only_lens_normal_splits':checks,'structural_bodies':bodies,'geometry_profiles_dims_angles_artwork_USB_and_controls_unchanged':True,'crease_threshold_is_OEM_specification':False,'diagnostic_reading':'creative/research/instruments-v2/optical-edge-diagnostic-reading.json','all_part_dimensions_estimated':True,'physical_iphone_tested':False,'art_accepted':False};(HERE/'build-report-v3.json').write_text(json.dumps(report,indent=2)+'\n');(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');assert sha(source)==old['source_sha256'];print('INSTRUMENTS_V3_LENS_NORMALS',report['source_sha256'],report['export_sha256'],len(bodies),checks)
