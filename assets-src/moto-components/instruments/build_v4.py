"""Only the continuous central-cover side-normal field; v3 immutable."""
import bpy,bmesh,json,hashlib,math,subprocess
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/instruments-v4';OUT.mkdir(parents=True,exist_ok=True);old=json.loads((ROOT/'creative/reviews/instruments-v3/source-geometry-check.json').read_text());source=HERE/'instruments-v3.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(source)==old['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));parts=bpy.data.collections['WEWA_INSTRUMENTS_SEPARATE_PARTS'];o=bpy.data.objects['Shaped central cluster cover']
def snapshot(obj,include_normals=True):
 row={'type':obj.type,'matrix':[list(x)for x in obj.matrix_world],'parent':obj.parent.name if obj.parent else None}
 if obj.type in ['MESH','CURVE','FONT']:
  dg=bpy.context.evaluated_depsgraph_get();em=bpy.data.meshes.new_from_object(obj.evaluated_get(dg),depsgraph=dg);row.update(positions=[list(v.co)for v in em.vertices],polygons=[list(p.vertices)for p in em.polygons],UV=[[list(x.uv)for x in uv.data]for uv in em.uv_layers],materials=[m.name for m in em.materials])
  if include_normals:row['normals']=[list(n.vector)for n in em.corner_normals]
  bpy.data.meshes.remove(em)
 return hashlib.sha256(json.dumps(row,separators=(',',':')).encode()).hexdigest()
protected={x.name:snapshot(x)for x in parts.objects if x!=o};before=snapshot(o,False);m=o.data;incident={v.index:[]for v in m.vertices}
for p in m.polygons:
 if abs(p.normal.z)<.5:
  for vi in p.vertices:incident[vi].append(p.normal.copy())
field=[]
for p in m.polygons:
 side=abs(p.normal.z)<.5;p.use_smooth=side
 for li in p.loop_indices:
  ns=incident[m.loops[li].vertex_index]
  if side:assert len(ns)==2;field.append((ns[0]+ns[1]).normalized())
  else:field.append(p.normal.copy())
m.set_sharp_from_angle(angle=math.radians(45));m.normals_split_custom_set(field)
for mod in list(o.modifiers):
 if mod.type=='WEIGHTED_NORMAL':o.modifiers.remove(mod)
 elif mod.type=='BEVEL':mod.harden_normals=True
bpy.context.view_layer.update();assert snapshot(o,False)==before,'Cover evaluated geometry/UV/transforms changed'
for name,sig in protected.items():assert snapshot(bpy.data.objects[name])==sig,name
bodies=[]
for obj in parts.objects:
 if not obj.get('structural_closed_volume',False)and obj.name not in ['USB contoured surround - closed v2','USB inset capsule face - closed v2']:continue
 dg=bpy.context.evaluated_depsgraph_get();mesh=bpy.data.meshes.new_from_object(obj.evaluated_get(dg),depsgraph=dg);bm=bmesh.new();bm.from_mesh(mesh);todo=set(bm.verts);components=0
 while todo:
  components+=1;stack=[todo.pop()]
  while stack:
   for e in stack.pop().link_edges:
    for v in e.verts:
     if v in todo:todo.remove(v);stack.append(v)
 row={'object':obj.name,'components':components,'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_m3':bm.calc_volume(signed=True)};bm.free();bpy.data.meshes.remove(mesh);assert row['components']==1 and row['non_manifold_edges']==0 and row['volume_m3']>0,row;bodies.append(row)
bpy.ops.object.select_all(action='DESELECT')
for obj in parts.objects:obj.select_set(True)
bpy.context.view_layer.objects.active=bpy.data.objects['INSTRUMENT_CLUSTER_MOUNT'];glb=HERE/'instruments-v4-inspection.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True,export_tangents=True);subprocess.run(['node',str(HERE/'finalize_export_v4.mjs')],cwd=ROOT,check=True);dest=HERE/'instruments-v4.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True);report={'schema':1,'revision':'instruments-v4','source_sha256':sha(dest),'export_sha256':sha(glb),'baseline_source_sha256':old['source_sha256'],'baseline_export_sha256':old['export_sha256'],'collection':parts.name,'root':'INSTRUMENT_CLUSTER_MOUNT','changed_only_central_cover_normal_field':True,'cover_evaluated_geometry_UV_material_worldmatrix_sha256_before':before,'cover_evaluated_geometry_UV_material_worldmatrix_sha256_after':snapshot(o,False),'cover_evaluated_geometry_UV_material_worldmatrix_bit_identical':True,'protected_source_nodes_sha256':protected,'protected_source_nodes_bit_identical':True,'structural_bodies':bodies,'geometry_profiles_dims_angles_artwork_USB_and_controls_unchanged':True,'all_part_dimensions_estimated':True,'physical_iphone_tested':False,'art_accepted':False};(HERE/'build-report-v4.json').write_text(json.dumps(report,indent=2)+'\n');(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');assert sha(source)==old['source_sha256'];print('INSTRUMENTS_V4_NORMALS',report['source_sha256'],report['export_sha256'],len(protected))
