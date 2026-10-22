import bpy,pathlib,json,hashlib,math,struct
R=pathlib.Path('/workspace/wewa');D=R/'creative/reviews/front-mudguard-red-finish-v2';f=json.loads((D/'main-fragment.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(R/f['source']));o=bpy.data.collections[f['collection']].objects[0];lib=pathlib.Path(bpy.path.abspath(o.data.library.filepath)).resolve();assert lib==R/f['geometry_library'];assert sha(lib)==f['geometry_library_sha256'];assert sha(R/f['glb'])==f['glb_sha256'];assert sha(R/'assets-src/moto-components/front-mudguard/front-mudguard-shell-inspection.glb')==f['old_glb_sha256'];assert all(s.link=='OBJECT'and s.material.library is None for s in o.material_slots);assert not o.modifiers
m=o.material_slots[0].material;assert not any(n.type=='TEX_IMAGE'for n in m.node_tree.nodes)
result={'native_source_reopened':True,'mesh_data_linked_to_original':True,'material_object_override_local':True,'source_sha256':sha(R/f['source']),'old_native_and_glb_unchanged':True,'modifiers':0,'material_images':0,'raw':[]}
def exr_channels(path):
 b=path.read_bytes();at=8;channels=[]
 def z(start):
  end=b.index(0,start);return b[start:end].decode(),end+1
 while True:
  name,at=z(at)
  if not name:break
  kind,at=z(at);n=struct.unpack_from('<I',b,at)[0];at+=4;end=at+n
  if name=='channels':
   while b[at]!=0:
    label,at=z(at);pixel=struct.unpack_from('<i',b,at)[0];channels.append({'name':label,'pixel_type':{0:'UINT32',1:'HALF16',2:'FLOAT32'}[pixel]});at+=16
  at=end
 return channels
for name in ['neutral-quarter' ,'neutral-reverse','raking']:
 p=D/('native96-'+name+'.exr');im=bpy.data.images.load(str(p));pixels=list(im.pixels);values=[v for i,v in enumerate(pixels)if i%4!=3];result['raw'].append({'file':p.name,'sha256':sha(p),'size':list(im.size),'channels':im.channels,'is_float':im.is_float,'finite':all(math.isfinite(v)for v in pixels),'rgb_range':[min(values),max(values)],'channels_actual':exr_channels(p),'storage_requested':'RGBA32 via save_render settings and render protocol'})
assert all(r['finite']and r['is_float']and all(c['pixel_type']=='FLOAT32'for c in r['channels_actual'])for r in result['raw']);(D/'reopen-raw-check.json').write_text(json.dumps(result,indent=2)+'\n')
