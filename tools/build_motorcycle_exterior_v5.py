"""Blender linked exterior assembly: retain all unchanged parents, replace reviewed mirrors, attach visible components."""
import hashlib
import json
import math
from pathlib import Path
import bpy
from mathutils import Matrix,Vector

R=Path(__file__).resolve().parents[1];K='motorcycle-exterior-v5';F=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K
F.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True);(O/'raw').mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=json.loads((R/'creative/research/motorcycle-exterior-v5/parents.json').read_text());assert sha(R/plan['base_native'])==plan['base_native_sha256']
bpy.ops.wm.open_mainfile(filepath=str(R/plan['base_native']));scene=bpy.context.scene
changed={r['key'] for r in plan['changes']};before={o.name:o.matrix_world.copy() for o in scene.objects if o.name.startswith('COVERAGE_PARENT [')}
for row in plan['parents']:
    key=row['key'];name='COVERAGE_PARENT ['+key+']';assert len(name.encode())<=63
    if key not in changed:continue
    if name in bpy.data.objects:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
    source=R/row['source'];assert sha(source)==row['sha256']
    with bpy.data.libraries.load(str(source),link=True) as (available,loaded):
        if row['collection']=='Scene Collection':
            assert all(n in available.objects for n in row['selected_objects']);loaded.objects=list(row['selected_objects'])
        else:
            assert row['collection'] in available.collections,(key,row['collection']);loaded.collections=[row['collection']]
    objects=loaded.objects if row['collection']=='Scene Collection' else loaded.collections[0].all_objects
    wanted=set(row['selected_objects']);found={o.name:o for o in objects if o.type=='MESH' and o.name in wanted}
    assert set(found)==wanted,(key,wanted-set(found))
    keep=set(found.values())
    for ob in list(keep):
        parent=ob.parent
        while parent is not None:keep.add(parent);parent=parent.parent
    wrapper=bpy.data.collections.new('EXTERIOR_ONLY ['+key+']')
    for ob in keep:wrapper.objects.link(ob)
    inst=bpy.data.objects.new(name,None);scene.collection.objects.link(inst);inst.instance_type='COLLECTION';inst.instance_collection=wrapper
    if 'matrix_world' in row:inst.matrix_world=Matrix(row['matrix_world'])
    else:inst.location=row['translation_m'];inst.rotation_euler=[math.radians(v) for v in row['rotation_degrees']];inst.scale=row['scale']
    inst['scope']=row['placement_status'];inst['art_accepted']=False
bpy.context.view_layer.update()
preserved=[]
for name,old in before.items():
    key=name.removeprefix('COVERAGE_PARENT [').removesuffix(']')
    if key in changed:continue
    delta=max(abs(old[i][j]-bpy.data.objects[name].matrix_world[i][j]) for i in range(4) for j in range(4));assert delta<1e-7
    preserved.append({'key':key,'maximum_matrix_delta':delta})
rows=[]
for row in plan['parents']:
    ob=bpy.data.objects['COVERAGE_PARENT ['+row['key']+']'];assert sha(R/row['source'])==row['sha256']
    rows.append({**row,'collection':ob.instance_collection.name,'matrix_world':[list(v) for v in ob.matrix_world]})
scene['scope']=plan['scope'];scene['whole_motorcycle_complete']=False;scene['art_accepted']=False;scene['rider_created']=False
scene.view_layers[0].material_override=None;scene.cycles.use_denoising=False;scene.cycles.device='CPU';scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=960;scene.render.resolution_y=675;scene.render.resolution_percentage=100
bpy.context.preferences.filepaths.save_version=0
for library in bpy.data.libraries:library.filepath=bpy.path.relpath(library.filepath,start=str(F))
file=F/(K+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(file),compress=True)
report={**plan,'source':str(file.relative_to(R)),'source_sha256':sha(file),'parents':rows,'all_parent_sources_unchanged':True,'unchanged_parent_pose_checks':preserved,'protocol_sha256':sha(Path(__file__))}
(O/'linked-parents-check.json').write_text(json.dumps(report,indent=2)+'\n')
print('LINKED_EXTERIOR_ASSEMBLY',len(rows),'UNCHANGED_POSES',len(preserved),flush=True)
