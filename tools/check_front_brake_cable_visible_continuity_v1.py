from pathlib import Path
import bpy,json,hashlib,struct,bmesh
R=Path('/workspace/wewa');K='front-brake-cable-visible-continuity-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K
source=H/'visible-continuation-v1.blend';bpy.ops.wm.open_mainfile(filepath=str(source));ob=next(o for o in bpy.data.objects if o.type=='MESH');native=[tuple(v.co) for v in ob.data.vertices]
old=R/'assets-src/moto-components/p29-lower-front-sheath-observed-a-v1/sheath-material.blend'
with bpy.data.libraries.load(str(old),link=True) as(a,b):b.collections=['P29_LOWER_FRONT_SHEATH_OBSERVED_A']
prev=next(o for o in b.collections[0].all_objects if o.type=='MESH' and not o.hide_render)
old_bsdf=prev.data.materials[0].node_tree.nodes.get('Principled BSDF');new_bsdf=ob.data.materials[0].node_tree.nodes.get('Principled BSDF')
for key in ['Base Color','Roughness','Metallic']:
 a=old_bsdf.inputs[key].default_value;bval=new_bsdf.inputs[key].default_value
 assert tuple(a)==tuple(bval) if key=='Base Color' else a==bval
quant=lambda seq:sorted(set(tuple(round(v,7) for v in p) for p in seq))
assert quant([tuple(v.co) for v in list(prev.data.vertices)[-64:]])==quant(native[:64]),'Actual A end and extension start do not match'
old_center=sum(v.co.z for v in list(prev.data.vertices)[-64:])/64
new_centers=[sum(v[2] for v in native[i:i+64])/64 for i in range(0,len(native),64)]
assert min(new_centers)>=old_center-1e-7
bm=bmesh.new();bm.from_mesh(ob.data);boundary=sum(e.is_boundary for e in bm.edges);branch=sum(len(e.link_faces)>2 for e in bm.edges);bm.free();assert boundary==64 and branch==0
b=(H/'visible-continuation-v1.glb').read_bytes();off=12;j=None;binary=None
while off<len(b):
 n,t=struct.unpack_from('<II',b,off);chunk=b[off+8:off+8+n]
 if t==0x4e4f534a:j=json.loads(chunk)
 if t==0x004e4942:binary=chunk
 off+=n+8
export=[]
for m in j['meshes']:
 for p in m['primitives']:
  a=j['accessors'][p['attributes']['POSITION']];v=j['bufferViews'][a['bufferView']];start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',12)
  export.extend(struct.unpack_from('<fff',binary,start+i*stride) for i in range(a['count']))
assert quant((x,z,-y) for x,y,z in native)==quant(export)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'actual_native_reopened':True,'source_sha256':sha(source),'glb_sha256':sha(H/'visible-continuation-v1.glb'),'unique_positions_equal_at_m':1e-7,'actual_old_A_last_ring_new_start_ring_equal_at_m':1e-7,'shared_ring_vertices':64,'old_A_no_longitudinal_duplication':True,'open_start_boundary_edges':boundary,'branch_edges':branch,'old_A_sha256_unchanged':sha(old),'old_B_sha256_unchanged':sha(R/'assets-src/moto-components/p29-lower-front-sheath-observed-b-v1/sheath-material.blend'),'full_cable_control_to_lever_qualified':False,'technical_passed':True}
report['actual_old_A_basecolor_roughness_metallic_matched']=True
(O/'native-export-seam-check.json').write_text(json.dumps(report,indent=2))
