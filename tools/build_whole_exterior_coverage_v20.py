"""Integrate source-frozen exterior completions while preserving unchanged native instance matrices."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];K='whole-exterior-coverage-v20';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;D=R/'creative/research'/K
for p in [H,O,D,O/'raw']:p.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=json.loads((R/'creative/reviews/whole-exterior-coverage-v19/linked-parents-check.json').read_text());assert sha(R/base['source'])==base['source_sha256'];changes=json.loads((D/'integration-changes.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/base['source']));s=bpy.context.scene
metadata={r['key']:r for r in base['parents']}
for r in changes['replace']:
 key=r['key'];bpy.data.objects.remove(bpy.data.objects['COVERAGE_PARENT ['+key+']'],do_unlink=True);del metadata[key]
for r in changes['replace']+changes['add']:
 key=r['key'];assert len(('COVERAGE_PARENT ['+key+']').encode())<=63,key;assert key not in metadata;src=R/r['source'];assert sha(src)==r['sha256'];selected=r.get('selected_objects',[])
 if selected:
  with bpy.data.libraries.load(str(src),link=True)as(a,b):assert all(n in a.objects for n in selected);b.objects=list(selected)
  col=bpy.data.collections.new('COVERAGE_SELECTION_V20 ['+key+']')
  for ob in b.objects:col.objects.link(ob)
 else:
  with bpy.data.libraries.load(str(src),link=True)as(a,b):assert r['collection']in a.collections;b.collections=[r['collection']]
  col=b.collections[0]
 inst=bpy.data.objects.new('COVERAGE_PARENT ['+key+']',None);s.collection.objects.link(inst);inst.instance_type='COLLECTION';inst.instance_collection=col
 if r.get('matrix_world'):inst.matrix_world=Matrix(r['matrix_world'])
 else:inst.location=r.get('translation_m',[0,0,0]);inst.rotation_euler=[math.radians(x)for x in r.get('rotation_degrees',[0,0,0])];inst.scale=r.get('scale',[1,1,1])
 metadata[key]=r
rows=[]
def count(col):return sum(1 if o.type in ('MESH','CURVE')else count(o.instance_collection)if o.instance_type=='COLLECTION'and o.instance_collection else 0 for o in col.all_objects if not o.hide_render)
for key,r in metadata.items():
 ob=bpy.data.objects['COVERAGE_PARENT ['+key+']'];row=dict(key=key,source=r['source'],sha256=r['sha256'],collection=ob.instance_collection.name,selected_objects=r.get('selected_objects',[]),translation_m=list(ob.location),rotation_degrees=[math.degrees(v)for v in ob.rotation_euler],scale=list(ob.scale),placement_status=r.get('placement_status','Historical bounded placement retained'),nested_sources=r.get('nested_sources',[]),renderable_meshes=count(ob.instance_collection));assert row['renderable_meshes']>0;rows.append(row)
s['scope']='Exterior source completions integrated; all source variants and bounded depths/poses remain explicit. Not mechanical/optical/hardware or artistic reception.';s['all_placements_estimated']=True;bpy.context.preferences.filepaths.save_version=0
for lib in bpy.data.libraries:lib.filepath=bpy.path.relpath(lib.filepath,start=str(H))
source=H/(K+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
report=dict(source=str(source.relative_to(R)),source_sha256=sha(source),parents=rows,parent_count=len(rows),all_parent_sources_unchanged=True,protocol_sha256=sha(Path(__file__)),scope=s['scope'],art_accepted=False,package_complete=False);(O/'linked-parents-check.json').write_text(json.dumps(report,indent=2)+'\n')
c=s.camera;target=Vector((0,.35,-.35));c.location=(2.9,-3,1);c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();s.cycles.samples=16;s.render.resolution_x=960;s.render.resolution_y=640;s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(O/'raw/coverage-quarter.exr');bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/'coverage-quarter.png'),scene=s);(O/'render-checkpoint.json').write_text(json.dumps(dict(source_sha256=sha(source),views=[dict(name='coverage-quarter',samples=16,resolution=[960,640],png_sha256=sha(O/'coverage-quarter.png'),exr_sha256=sha(O/'raw/coverage-quarter.exr'))]),indent=2)+'\n');print('INTEGRATED_PARENTS',len(rows))
