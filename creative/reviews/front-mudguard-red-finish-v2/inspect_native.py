import bpy,pathlib,json
R=pathlib.Path('/workspace/wewa');O=R/'creative/reviews/front-mudguard-red-finish-v2'
a={}
for key,rel in [('mudguard','assets-src/moto-components/front-mudguard/front-mudguard-shell-v1.blend'),('tank','assets-src/moto-components/fuel-tank-shell/fuel-tank-shell-v1.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(R/rel));a[key]={'objects':[],'materials':[]}
 for o in bpy.context.scene.objects:
  if o.type=='MESH':a[key]['objects'].append({'name':o.name,'hide_render':o.hide_render,'matrix':[list(r)for r in o.matrix_world],'materials':[m.name if m else None for m in o.data.materials],'modifiers':[(m.name,m.type)for m in o.modifiers]})
 for m in bpy.data.materials:
  if not m.use_nodes:continue
  a[key]['materials'].append({'name':m.name,'principled':[{i.name:list(i.default_value)if hasattr(i.default_value,'__len__')else i.default_value for i in n.inputs if i.name in ['Base Color','Roughness','Metallic','Coat Weight','Coat Roughness','IOR']}for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'],'images':[n.image.name for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]})
(O/'native-inspection.json').write_text(json.dumps(a,indent=2)+'\n');print(json.dumps(a))
