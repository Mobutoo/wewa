"""Material-only original black vinyl/WEWA proposal on immutable gray4 cover."""
import bpy,json,hashlib,struct
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/seat-envelope-v1';O.mkdir(parents=True,exist_ok=True);W=Path('/workspace/wewa-assets/work-in-progress/seat-envelope-v1');W.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();master=H/'seat-envelope-study-v4.blend';g=json.loads((R/'creative/reviews/seat-envelope-study-v4/build-report.json').read_text());read=json.loads((R/'creative/reviews/seat-envelope-study-v4/gray-reflection-reading.json').read_text());assert sha(master)==g['source_sha256']==read['source_sha256']and read['read_by_agent']and read['permitted_bounded_material_candidate'];images=json.loads((O/'original-material-images-provenance.json').read_text())
for row in images['outputs']:assert sha(R/row['path'])==row['sha256']
bpy.ops.wm.open_mainfile(filepath=str(master));body=bpy.data.objects[g['object']];black=((36/255+.055)/1.055)**2.4;loaded={}
for filename in ['wewa-seat-body-original-normal-v1.png','wewa-seat-caps-original-normal-v1.png','wewa-seat-rear-original-basecolor-v1.png']:
 im=bpy.data.images.load(str(H/'textures'/filename),check_existing=True);im.colorspace_settings.name='sRGB'if'basecolor'in filename else'Non-Color';im.pack();im.filepath='//textures/'+filename;loaded[filename]=im
values=[]
def material(name,color,roughness,normal=None,base=None):
 mat=bpy.data.materials.new(name);mat.use_nodes=True;nodes=mat.node_tree.nodes;bs=nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=0;bs.inputs['Roughness'].default_value=roughness;bs.inputs['IOR'].default_value=1.46
 if normal:
  tx=nodes.new('ShaderNodeTexImage');tx.image=loaded[normal];nm=nodes.new('ShaderNodeNormalMap');nm.uv_map='Original seat parameter UV';nm.inputs['Strength'].default_value=1;mat.node_tree.links.new(tx.outputs['Color'],nm.inputs['Color']);mat.node_tree.links.new(nm.outputs['Normal'],bs.inputs['Normal'])
 if base:
  tx=nodes.new('ShaderNodeTexImage');tx.image=loaded[base];mat.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
 values.append({'name':name,'base_linear':list(color),'roughness':roughness,'metallic':0,'IOR':1.46,'normal_image':normal,'base_image':base,'not_measured_OEM':True});return mat
bn='wewa-seat-body-original-normal-v1.png';cn='wewa-seat-caps-original-normal-v1.png';mats=[material('Original black vinyl - long outer envelope',(black,)*3,.5,bn),material('Original black vinyl - front cap',(black,)*3,.5,cn),material('Original WEWA rear vinyl graphic',(black,)*3,.5,cn,'wewa-seat-rear-original-basecolor-v1.png'),material('Dark inner inspection - not OEM substrate',(.012,)*3,.75),material('Original black rear piping',(.012,)*3,.55),material('Original dark thread strands',(.022,)*3,.72)]
body.data.materials.clear()
for mat in mats[:4]:body.data.materials.append(mat)
for p in body.data.polygons:
 reg=body.data.attributes['COVER_SKIN_REGION'].data[p.index].value;sec=body.data.attributes['EXTERIOR_SECTION'].data[p.index].value;p.material_index=(2 if sec==2 else 1 if sec==1 else 0)if reg==0 else 3
for name,mat in [('Observed related rear panel piping - estimated',mats[4]),('Rear piping stitch strands - estimated pitch',mats[5])]:
 ob=bpy.data.objects[name];ob.data.materials.clear();ob.data.materials.append(mat)
body['material_scope']='Original black vinyl / grain / WEWA proposal, exact current cover embossing and measured material unknown';bpy.ops.object.select_all(action='DESELECT')
for name in g['objects']+['SEAT_ENVELOPE_ESTIMATED_DATUM']:bpy.data.objects[name].select_set(True)
bpy.context.view_layer.objects.active=body;source=H/'seat-envelope-v1.blend';export=H/'seat-envelope-inspection.glb';raw=W/'raw-before-unused-tangent-removal.glb';bpy.ops.wm.save_as_mainfile(filepath=str(source));bpy.ops.export_scene.gltf(filepath=str(raw),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=True,export_materials='EXPORT',export_extras=True)
# Transport-only removal of unused tangent attributes; binary buffers are unchanged.
data=raw.read_bytes();assert data[:4]==b'glTF';chunks=[];off=12
while off<len(data):
 n,typ=struct.unpack_from('<II',data,off);payload=data[off+8:off+8+n];chunks.append((typ,payload));off+=8+n
j=json.loads(chunks[0][1]);removed=[]
for mi,mesh in enumerate(j['meshes']):
 for pi,prim in enumerate(mesh['primitives']):
  mat=j['materials'][prim['material']]
  if not mat.get('normalTexture')and'TANGENT'in prim['attributes']:removed.append({'mesh':mesh.get('name',mi),'primitive':pi,'accessor':prim['attributes'].pop('TANGENT'),'reason':'No normalTexture; unused attribute only'})
jsonbytes=json.dumps(j,separators=(',',':')).encode();jsonbytes+=b' '*((-len(jsonbytes))%4);newchunks=[(chunks[0][0],jsonbytes)]+chunks[1:];total=12+sum(8+len(c)for _,c in newchunks);result=struct.pack('<4sII',b'glTF',2,total)+b''.join(struct.pack('<II',len(c),t)+c for t,c in newchunks);export.write_bytes(result);bin_before=[c for t,c in chunks if t==0x004e4942];bin_after=[c for t,c in newchunks if t==0x004e4942];assert bin_before==bin_after
report={'schema':1,'source_sha256':sha(source),'export_sha256':sha(export),'gray_source_sha256':g['source_sha256'],'gray_export_sha256':g['export_sha256'],'builder_sha256':sha(Path(__file__)),'object':g['object'],'objects':g['objects'],'collection':g['collection'],'triangles':g['triangles'],'materials':values,'original_material_images':images,'raw_export_private_path':str(raw),'raw_export_sha256':sha(raw),'unused_tangent_attributes_removed':removed,'binary_payload_byte_identical_after_attribute_removal':True,'BIN_sha256':hashlib.sha256(bin_before[0]).hexdigest(),'only_declared_unused_TANGENT_JSON_references_removed':True,'external_libraries':len(bpy.data.libraries),'images':[{'name':im.name,'path':im.filepath,'packed':bool(im.packed_file),'colorspace':im.colorspace_settings.name}for im in loaded.values()],'scope':'Original material candidate only, estimated exterior cover and rear seam, not full seat, exactcurrent embossing/mount/foam/base unknown.','art_accepted':False};(O/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');assert sha(master)==g['source_sha256'];print(json.dumps(report))
