"""Reopen the standalone delivered GLB and save an editable packed Blender context."""
from pathlib import Path
import hashlib
import json
import bpy

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets-src/moto-components/under-tank-completion-v1'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
path=OUT/'motorcycle-completed-candidate.glb'
bpy.ops.import_scene.gltf(filepath=str(path))
# Blender also imports orphaned original nodes retained for byte provenance.
# Remove precisely the four detached study hierarchies from this active context.
plan=json.loads((ROOT/'creative/research/under-tank-completion-v1/plan.json').read_text())
for key in plan['replace_groups']:
    ob=bpy.data.objects.get('PARENT ['+key+']')
    if ob:
        for child in list(ob.children_recursive):bpy.data.objects.remove(child,do_unlink=True)
        bpy.data.objects.remove(ob,do_unlink=True)
assert len([o for o in bpy.context.scene.objects if o.name.startswith('COMPLETION [')])==10
groups=[o.name for o in bpy.context.scene.objects if o.name.startswith('PARENT [')]
assert len(groups)==173,(len(groups),groups)
bpy.ops.file.pack_all()
assert not bpy.data.libraries
images=[im for im in bpy.data.images if im.type=='IMAGE']
assert all(im.packed_file for im in images)
bpy.context.scene['scope']='Editable context imported from LOD candidate; detailed additions source supplied separately.'
bpy.context.scene['input_glb_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'motorcycle-completed-context.blend'),compress=True)
report={'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'linked_libraries':0,
        'packed_images':len(images),'original_groups':173,'completion_groups':10,
        'context_scope':'Reimported LOD mesh context, not original high resolution source.'}
(ROOT/'creative/reviews/under-tank-completion-v1/context-check.json').write_text(json.dumps(report,indent=2)+'\n')
print('UNDER_TANK_CONTEXT',len(images),'packed images')
