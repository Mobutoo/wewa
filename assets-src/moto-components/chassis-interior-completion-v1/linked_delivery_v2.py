import bpy,json,math,hashlib
from pathlib import Path
R=Path('/workspace/wewa');O=Path(__file__).resolve().parent
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.open_mainfile(filepath=str(R/'assets-src/moto-components/whole-exterior-coverage-v14/whole-exterior-coverage-v14.blend'))
keep=['frame-headtube','frame-front-backbone-v2','frame-front-downmember','frame-head-gusset','frame-lower-cradle-rail','frame-seat-rail-observed','swingarm-body','air-cleaner-box-outer-body-pf581003-v1','airbox-carb-boot-physical-study-v2']
rows=[];inputs=json.loads((R/'creative/research/whole-exterior-coverage-v14/native-collection-inventory-v14.json').read_text())['inputs']
for ob in list(bpy.context.scene.objects):
 key=next((k for k in keep if ob.name=='COVERAGE_PARENT ['+k+']'),None)
 if not key:
  if ob.type not in ['CAMERA','LIGHT']:bpy.data.objects.remove(ob,do_unlink=True)
  continue
 source=next(r for r in inputs if r['key']==key);rows.append(dict(key=key,source=source['source_blend'],collection=ob.instance_collection.name,selected_objects=source.get('selected_objects'),matrix_world=[list(v)for v in ob.matrix_world],source_class='documented_related_variant / estimated',pose_uncertainty_m=.03))
 if key in ['frame-seat-rail-observed','frame-lower-cradle-rail']:
  cp=ob.copy();bpy.context.scene.collection.objects.link(cp);cp.location.x-=.16 if key=='frame-seat-rail-observed'else .14;cp.name='PROVISIONAL opposite '+key;bpy.context.view_layer.update();rows.append(dict(key=cp.name,source=source['source_blend'],collection=cp.instance_collection.name,matrix_world=[list(v)for v in cp.matrix_world],source_class='estimated',provisional_same_exemplar=True,pose_uncertainty_m=.025))
extras=json.loads((O/'context-sources.json').read_text())
for r in extras:
 if 'source'not in r:continue
 p=R/r['source'];col=r['collection']
 with bpy.data.libraries.load(str(p),link=True)as(a,b):b.collections=[col]
 ob=bpy.data.objects.new('OMITTED source '+col,None);bpy.context.scene.collection.objects.link(ob);ob.instance_type='COLLECTION';ob.instance_collection=b.collections[0];pos=r['translation_m'];rot=r['rotation_deg']
 if 'seat-base-observed-underside-v2'in r['source']:pos=[0,.7,-.265];rot=[0,180,0]
 ob.location=pos;ob.rotation_euler=[math.radians(v)for v in rot];bpy.context.view_layer.update();rows.append(dict(key=col,source=r['source'],collection=col,matrix_world=[list(v)for v in ob.matrix_world],source_class='documented_related_variant / estimated',pose_uncertainty_m=.03,rotation_uncertainty_deg=10))
with bpy.data.libraries.load(str(O/'new-observed-children.blend'),link=True)as(a,b):b.collections=['CHASSIS_NEW_OBSERVED_CHILDREN_V1']
ob=bpy.data.objects.new('NEW children observed related kit',None);bpy.context.scene.collection.objects.link(ob);ob.instance_type='COLLECTION';ob.instance_collection=b.collections[0]
rows.extend([r for r in json.loads((O/'poses-global.json').read_text())['items']if r['key'].startswith('NEW ')])
(O/'poses-global.json').write_text(json.dumps({'convention':'Blender Xleft Yrear Zup, metres; row-major matrices act on column vectors. glTF conversion C=[[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]], MglTF=C Mnative C^-1','items':rows,'all_poses_estimated':True,'art_accepted':False},indent=2))
bpy.context.scene['scope']='Interior linked kit, originals untouched, visible related children estimated, no weld or fit acceptance'
for lib in bpy.data.libraries:lib.filepath=bpy.path.relpath(lib.filepath,start=str(O))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'kit-linked-v2.blend'),compress=True,relative_remap=False)
print('LINKED_KIT_READY',len(rows),(O/'kit-linked-v2.blend').stat().st_size)
