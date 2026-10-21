"""Only actual planar cap normal boundaries of two rear pods; v4 immutable."""
import bpy,bmesh,json,hashlib,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];P=R/'creative/reviews/instruments-v5';P.mkdir(parents=True,exist_ok=True);old=json.loads((R/'creative/reviews/instruments-v4/source-geometry-check.json').read_text());read=json.loads((R/'creative/reviews/instruments-v4/preview-review.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();src=H/'instruments-v4.blend';assert sha(src)==old['source_sha256']==read['source_sha256']and read['passed_for_next_normals_revision'];bpy.ops.wm.open_mainfile(filepath=str(src));C=bpy.data.collections[old['collection']];changed={'SPEED hollow rear pod','FUEL_GEAR hollow rear pod'}
def signature(o,normals=True):
 row={'type':o.type,'matrix':[list(r)for r in o.matrix_world],'parent':o.parent.name if o.parent else None}
 if o.type in ['MESH','CURVE','FONT']:
  dg=bpy.context.evaluated_depsgraph_get();em=bpy.data.meshes.new_from_object(o.evaluated_get(dg),depsgraph=dg);row.update(positions=[list(v.co)for v in em.vertices],polygons=[list(p.vertices)for p in em.polygons],UV=[[list(x.uv)for x in uv.data]for uv in em.uv_layers],materials=[m.name for m in em.materials])
  if normals:row['normals']=[list(n.vector)for n in em.corner_normals]
  bpy.data.meshes.remove(em)
 return hashlib.sha256(json.dumps(row,separators=(',',':')).encode()).hexdigest()
protected={o.name:signature(o)for o in C.objects if o.name not in changed};checks=[]
for name in sorted(changed):
 o=bpy.data.objects[name];before=signature(o,False);m=o.data;assert not m.has_custom_normals;planes={p.index for p in m.polygons if abs(p.normal.z)>.999999};edge_faces={tuple(sorted(e.vertices)):[]for e in m.edges}
 for p in m.polygons:
  for a,b in zip(list(p.vertices),list(p.vertices)[1:]+list(p.vertices)[:1]):edge_faces[tuple(sorted((a,b)))].append(p.index)
 boundaries=[]
 for edge in m.edges:
  adjacent=edge_faces[tuple(sorted(edge.vertices))];assert len(adjacent)==2
  if sum(i in planes for i in adjacent)==1:edge.use_edge_sharp=True;boundaries.append(edge.index)
 for p in m.polygons:
  if p.index in planes:p.use_smooth=False
 m.update();bpy.context.view_layer.update();assert signature(o,False)==before
 checks.append({'object':name,'actual_planar_cap_polygons':len(planes),'normal_boundary_edges':len(boundaries),'cap_source_Z_planes_m':sorted(set(round(m.vertices[m.polygons[i].vertices[0]].co.z,6)for i in planes)),'evaluated_positions_polygons_UV_material_worldmatrix_sha256_before':before,'evaluated_positions_polygons_UV_material_worldmatrix_sha256_after':signature(o,False),'geometry_UV_material_transform_bit_identical':True})
for name,sig in protected.items():assert signature(bpy.data.objects[name])==sig,name
bodies=[]
for o in C.objects:
 if not o.get('structural_closed_volume',False)and o.name not in ['USB contoured surround - closed v2','USB inset capsule face - closed v2']:continue
 dg=bpy.context.evaluated_depsgraph_get();em=bpy.data.meshes.new_from_object(o.evaluated_get(dg),depsgraph=dg);bm=bmesh.new();bm.from_mesh(em);todo=set(bm.verts);components=0
 while todo:
  components+=1;stack=[todo.pop()]
  while stack:
   for edge in stack.pop().link_edges:
    for v in edge.verts:
     if v in todo:todo.remove(v);stack.append(v)
 row={'object':o.name,'components':components,'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_m3':bm.calc_volume(signed=True)};bm.free();bpy.data.meshes.remove(em);assert row['components']==1 and row['non_manifold_edges']==0 and row['volume_m3']>0; bodies.append(row)
bpy.ops.object.select_all(action='DESELECT')
for o in C.objects:o.select_set(True)
bpy.context.view_layer.objects.active=bpy.data.objects[old['root']];glb=H/'instruments-v5-inspection.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True,export_tangents=True);subprocess.run(['node',str(H/'finalize_export_v5.mjs')],cwd=R,check=True);dest=H/'instruments-v5.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True);report={'schema':1,'revision':'instruments-v5','source_sha256':sha(dest),'export_sha256':sha(glb),'baseline_source_sha256':old['source_sha256'],'baseline_export_sha256':old['export_sha256'],'collection':C.name,'root':old['root'],'changed_only_planar_pod_cap_normal_boundaries':checks,'protected_source_nodes_sha256':protected,'protected_source_nodes_bit_identical':True,'structural_bodies':bodies,'geometry_profiles_dims_angles_artwork_USB_and_controls_unchanged':True,'all_part_dimensions_estimated':True,'physical_iphone_tested':False,'art_accepted':False};(H/'build-report-v5.json').write_text(json.dumps(report,indent=2)+'\n');(P/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');assert sha(src)==old['source_sha256'];print('INSTRUMENTS_V5_NORMAL_CAPS',report['source_sha256'],report['export_sha256'],checks)
