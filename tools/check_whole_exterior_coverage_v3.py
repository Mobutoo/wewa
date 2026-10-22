"""Reopen linked native layout and verify exact parents/poses; no fit or art reception."""
import bpy,json,sys,hashlib,math
from pathlib import Path
from mathutils import Matrix,Euler,Vector
R=Path(__file__).resolve().parents[1];rev=sys.argv[sys.argv.index('--')+1];O=R/'creative/reviews'/rev;report=json.loads((O/'linked-parents-check.json').read_text());source=R/report['source'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert Path(bpy.data.filepath).resolve()==source.resolve();assert sha(source)==report['source_sha256'];rows=[]
def visible_nested(col, path=()):
 pointer=col.as_pointer();assert pointer not in path
 result=[]
 for ob in col.all_objects:
  if ob.hide_render:continue
  if ob.type in ('MESH','CURVE'):result.append(ob)
  elif ob.instance_type=='COLLECTION'and ob.instance_collection:result.extend(visible_nested(ob.instance_collection,path+(pointer,)))
 return result
for row in report['parents']:
 nested_checks=[]
 for dep in row.get('nested_sources',[]):
  pdep=R/dep['source'];assert sha(pdep)==dep['sha256'];found=any(Path(bpy.path.abspath(lib.filepath)).resolve()==pdep.resolve()for lib in bpy.data.libraries);assert found,dep['source'];nested_checks.append(dict(source=dep['source'],sha256=sha(pdep),actually_loaded=True))
 p=R/row['source'];assert sha(p)==row['sha256'];obj=bpy.data.objects['COVERAGE_PARENT ['+row['key']+']'];assert obj.instance_type=='COLLECTION';col=obj.instance_collection;
 if row.get('selected_objects'):
  assert not col.library
  assert sorted(o.name for o in col.objects)==sorted(row['selected_objects'])
  for ob in col.objects:
   assert ob.library and Path(bpy.path.abspath(ob.library.filepath)).resolve()==p.resolve()
  libpath=p.resolve()
 else:
  assert col.library
  libpath=Path(bpy.path.abspath(col.library.filepath)).resolve();assert libpath==p.resolve(),(row['key'],str(libpath),str(p))
 expected=Matrix.LocRotScale(Vector(row['translation_m']),Euler([math.radians(v)for v in row['rotation_degrees']],'XYZ').to_quaternion(),Vector(row['scale']));delta=max(abs(expected[i][j]-obj.matrix_world[i][j])for i in range(4)for j in range(4));assert delta<1e-6
 visible=visible_nested(col);assert visible;rows.append(dict(key=row['key'],actual_linked_library=str(libpath.relative_to(R)),source_sha256=sha(p),visible_geometry_objects=len(visible),nested_source_checks=nested_checks,maximum_pose_matrix_delta=delta,actual_collection=col.name))
assert len(rows)==report['parent_count'];(O/'native-reopen-check.json').write_text(json.dumps(dict(source_sha256=sha(source),source_reopened=True,parents=rows,parent_count=len(rows),all_exact_parent_hashes_and_relative_library_paths_verified=True,source_unchanged=sha(source)==report['source_sha256'],protocol_sha256=sha(Path(__file__)),scope='Actual native library references and instance transforms; not source/export parity, calibrated projection, collisions, complete assembly or art reception'),indent=2)+'\n');print('NATIVE_LAYOUT_REOPENED',rev,len(rows))
