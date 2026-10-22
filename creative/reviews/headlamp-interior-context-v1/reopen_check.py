import bpy,pathlib,json,math,hashlib
R=pathlib.Path('/workspace/wewa');D=R/'creative/reviews/headlamp-interior-context-v1';A=R/'assets-src/moto-components/headlamp-interior-context-v1';bpy.ops.wm.open_mainfile(filepath=str(A/'headlamp-context.blend'))
s=bpy.context.scene;r={'native_reopened':True,'active_scene':s.name,'scenes':{x.name:[o.name for o in x.objects if o.type=='MESH'] for x in bpy.data.scenes},'mesh_emission_zero':True}
for o in s.objects:
 if o.type!='MESH':continue
 for m in o.data.materials:
  if m and m.use_nodes:
   for n in m.node_tree.nodes:
    if n.type=='EMISSION':r['mesh_emission_zero']=False
    if n.type=='BSDF_PRINCIPLED' and n.inputs['Emission Strength'].default_value!=0 and any(n.inputs['Emission Color'].default_value[i]!=0 for i in range(3)):r['mesh_emission_zero']=False
r['raw']={}
for name in ['native96-source.exr','native96-export.exr']:
 im=bpy.data.images.load(str(D/name),check_existing=False);px=list(im.pixels);r['raw'][name]={'size':list(im.size),'channels':im.channels,'float':im.is_float,'all_finite':all(math.isfinite(v) for v in px),'rgb_range':[min(v for i,v in enumerate(px) if i%4!=3),max(v for i,v in enumerate(px) if i%4!=3)]}
baseline=json.loads((D/'native-inputs.json').read_text());r['original_sources_unchanged']=all(hashlib.sha256((R/v['path']).read_bytes()).hexdigest()==v['sha256'] for v in baseline.values())
assert r['original_sources_unchanged'] and r['mesh_emission_zero'];assert all(x['all_finite'] for x in r['raw'].values())
(D/'reopen-raw-check.json').write_text(json.dumps(r,indent=2)+'\n')
