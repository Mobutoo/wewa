"""Read-only Blender native coordinate extraction. Never save/transform a source."""
import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent;args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []; input_name=args[0] if args else 'parent-inputs.json'; output_name=args[1]if len(args)>1 else 'native-coordinate-read.json';manifest=json.loads((D/input_name).read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
def bounds(points):return {'min':[min(p[i]for p in points) for i in range(3)],'max':[max(p[i]for p in points) for i in range(3)]}if points else None
for entry in manifest['parents']:
 p=R/entry['native'];row={'id':entry['id'],'native':entry['native'],'exists':p.exists()}
 if not p.exists():rows.append(row);continue
 before=sha(p);bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();objs=[];allpts=[]
 selected=bpy.data.collections.get(entry.get('collection',''))
 for o in (selected.all_objects if selected else s.objects):
  if o.type in ['CAMERA','LIGHT']:continue
  m=o.matrix_world;v={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'hide_render':o.hide_render,'collections':[c.name for c in o.users_collection],'matrix_world_rows':[list(x)for x in m],'matrix_local_rows':[list(x)for x in o.matrix_local],'origin_world_m':list(m.translation),'basis_world_columns':[[m[j][i]for j in range(3)]for i in range(3)],'custom_properties':{k:str(o[k])for k in o.keys()if k!='_RNA_UI'}}
  if o.type=='MESH':
   ev=o.evaluated_get(deps);mesh=ev.to_mesh();points=[m@x.co for x in mesh.vertices];allpts+=points;mesh.calc_loop_triangles();v.update(mesh_vertices=len(mesh.vertices),mesh_triangles=len(mesh.loop_triangles),mesh_local_bounds=bounds([x.co for x in mesh.vertices]),evaluated_world_bounds_m=bounds(points),modifiers=[{'name':x.name,'type':x.type,'show_render':x.show_render}for x in o.modifiers]);ev.to_mesh_clear()
  objs.append(v)
 assert sha(p)==before
 visible=[x['evaluated_world_bounds_m']for x in objs if x['type']=='MESH'and not x['hide_render']]
 component_bounds={'min':[min(x['min'][i]for x in visible)for i in range(3)],'max':[max(x['max'][i]for x in visible)for i in range(3)]}if visible else None
 row.update(sha256=before,bytes=p.stat().st_size,scene_units={'system':s.unit_settings.system,'scale_length':s.unit_settings.scale_length,'length_unit':s.unit_settings.length_unit},all_scene_mesh_bounds_m=bounds(allpts),component_bounds_m=component_bounds,component_meshes=[x['name']for x in objs if x['type']=='MESH'and not x['hide_render']],objects=objs,source_unchanged=True)
 rows.append(row);print('NATIVE_READ',entry['id'],flush=True)
(D/output_name).write_text(json.dumps({'schema':1,'scope':'Actual opened .blend scene matrices/evaluated bounds only. Zero source save or pose change, no installed fit inferred.','units_note':'Numeric Blender world coordinates are metres only with recorded scene scale_length; object origin differs from mesh geometric centre.','parents':rows},indent=2)+'\n')
