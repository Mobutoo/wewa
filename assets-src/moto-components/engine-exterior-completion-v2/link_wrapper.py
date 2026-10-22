import bpy,json,hashlib
from pathlib import Path
from mathutils import Matrix
O=Path(__file__).resolve().parent;R=Path('/workspace/wewa');rows=json.loads((O/'poses-and-sources.json').read_text())['parents'];bpy.ops.wm.read_factory_settings(use_empty=True);root=bpy.data.collections.new('WEWA_ENGINE_EXTERIOR_COMPLETION_V2_CONDITIONAL');bpy.context.scene.collection.children.link(root)
for row in rows:
 p=R/row['source'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
 if row['key'].startswith('WEWA_ENGINE'):
  with bpy.data.libraries.load(str(p),link=True) as(a,b):assert row['key'] in a.collections;b.collections=[row['key']]
  c=b.collections[0]
 else:
  names=list(row['objects'])
  with bpy.data.libraries.load(str(p),link=True) as(a,b):b.objects=names
  c=bpy.data.collections.new('EXACT_SOURCE_SELECTION_'+row['key'])
  for ob in b.objects:c.objects.link(ob)
 inst=bpy.data.objects.new(row['key'],None);inst.instance_type='COLLECTION';inst.instance_collection=c;inst.matrix_world=Matrix(row['matrix']);inst['source_sha256']=row['sha256'];inst['status']=row['status'];root.objects.link(inst)
bpy.context.preferences.filepaths.save_version=0;bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene['art_accepted']=False;bpy.context.scene['conditional_donor']=True;bpy.ops.wm.save_as_mainfile(filepath=str(O/'engine-exterior-completion-v2-linked.blend'),compress=True,relative_remap=True)
