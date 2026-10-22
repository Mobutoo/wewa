import bpy,json,hashlib
from pathlib import Path
R=Path('/workspace/wewa');K='passenger-footrest-left-exterior-context-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;COL='PASSENGER_FOOTREST_LEFT_EXTERIOR_CONTEXT_V1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=H/(K+'.blend');bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
with bpy.data.libraries.load(str(source),link=True)as(a,b):b.collections=[COL]
inst=bpy.data.objects.new('COVERAGE_PARENT ['+K+']',None);bpy.context.scene.collection.objects.link(inst);inst.instance_type='COLLECTION';inst.instance_collection=b.collections[0];inst['new_physical_ids_in_wrapper']=0;inst['unit_context_count']=1;inst['existing_parent_count']=3;inst['fit_qualified']=False
for lib in bpy.data.libraries:lib.filepath=bpy.path.relpath(lib.filepath,start=str(H))
out=H/'coord-exemplar.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(O/'linked-parents-check.json').write_text(json.dumps({'source':str(out.relative_to(R)),'source_sha256':sha(out),'parent_count':1,'parents':[{'key':K,'source':str(source.relative_to(R)),'sha256':sha(source),'collection':COL,'selected_objects':[],'translation_m':[0,0,0],'rotation_degrees':[0,0,0],'scale':[1,1,1]}],'scope':'One reused LH local exterior unit, three parents once, no new physical IDs or installed fit'},indent=2)+'\n')
