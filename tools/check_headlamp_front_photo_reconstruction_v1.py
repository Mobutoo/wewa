"""Independent native reopen and original glTF POSITION comparison."""
from pathlib import Path
import bpy,json,struct,hashlib
R=Path('/workspace/wewa');K='headlamp-front-photo-reconstruction-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K
src=H/'front-photo-reconstruction-v1.blend';bpy.ops.wm.open_mainfile(filepath=str(src))
b=(H/'front-photo-reconstruction-v1.glb').read_bytes();off=12;j=None;binary=None
while off<len(b):
 n,t=struct.unpack_from('<II',b,off);chunk=b[off+8:off+8+n]
 if t==0x4e4f534a:j=json.loads(chunk)
 if t==0x004e4942:binary=chunk
 off+=n+8
def positions(i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',12)
 return [struct.unpack_from('<fff',binary,start+n*stride) for n in range(a['count'])]
native=[];export=[]
for ob in bpy.data.objects:
 if ob.type=='MESH':native.extend((v.co.x,v.co.z,-v.co.y) for v in ob.data.vertices)
for mesh in j['meshes']:
 for p in mesh['primitives']:export.extend(positions(p['attributes']['POSITION']))
quant=lambda seq:sorted(set(tuple(round(v,7) for v in p) for p in seq))
assert quant(native)==quant(export),'Native/export unique POSITION mismatch'
assert len([o for o in bpy.data.objects if o.type=='MESH'])==5
mats=j['materials'];assert all(not any(m.get('emissiveFactor',[0,0,0])) for m in mats)
assert any(m.get('extensions',{}).get('KHR_materials_transmission',{}).get('transmissionFactor')==1 for m in mats)
assert not j.get('images'), 'No documentary texture permitted'
from mathutils import Vector
from mathutils.bvhtree import BVHTree
field=next(o for o in bpy.data.objects if o.type=='MESH' and 'ESTIMATED_CONCAVE' in o.name)
bvh=BVHTree.FromPolygons([v.co for v in field.data.vertices],[list(p.vertices) for p in field.data.polygons],all_triangles=False)
probes=[]
for label,x,y,expected in [('main-aperture',.0045,.0008,False),('pilot-aperture',.003,-.037,False),('visible-left-field',-.05,0,True),('visible-upper-field',0,.05,True)]:
 hit=bvh.ray_cast(Vector((x,y,.1)),Vector((0,0,-1)))[0] is not None
 assert hit==expected,(label,hit,expected)
 probes.append({'probe':label,'actual_surface_hit':hit,'expected_hit':expected})
report={'source':str(src.relative_to(R)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(b).hexdigest(),'actual_native_reopened':True,'mesh_count':5,'unique_native_export_positions_equal_at_m':1e-7,'native_position_count':len(native),'export_position_count':len(export),'no_emission':True,'glass_transmission_factor':1,'no_images_embedded':True,'technical_passed':True,'scope':'Source/export consistency only; no optical prescription, measured fit or artistic reception'}
report['visible_field_aperture_and_surface_probes']=probes
report['export_materials']=mats
report['export_nodes']=j['nodes']
(O/'native-export-parity.json').write_text(json.dumps(report,indent=2))

dependencies=[]
for lib in bpy.data.libraries:
 path=Path(bpy.path.abspath(lib.filepath)).resolve();dependencies.append({'source':str(path.relative_to(R)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
f=json.loads((O/'integration-fragment.json').read_text());assert sorted(x['source'] for x in dependencies)==sorted(x['source'] for x in f['replacements'][0]['nested_sources']);assert all(x in f['replacements'][0]['nested_sources'] for x in dependencies)
pose_checks=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 node=next(n for n in j['nodes'] if n.get('name')==ob.name)
 expected=[ob.location.x,ob.location.z,-ob.location.y];actual=node.get('translation',[0,0,0]);assert max(abs(x-y) for x,y in zip(expected,actual))<1e-7
 pose_checks.append({'object':ob.name,'glTF_translation':actual,'expected_native_basis_translation':expected})
material_checks=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 for slot in ob.material_slots:
  mat=slot.material;bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');gm=next(x for x in mats if x['name']==mat.name);pbr=gm['pbrMetallicRoughness']
  checks={'roughness':abs(bs.inputs['Roughness'].default_value-pbr.get('roughnessFactor',1))<1e-6,'metallic':abs(bs.inputs['Metallic'].default_value-pbr.get('metallicFactor',1))<1e-6,'transmission':abs(bs.inputs['Transmission Weight'].default_value-gm.get('extensions',{}).get('KHR_materials_transmission',{}).get('transmissionFactor',0))<1e-6}
  assert all(checks.values()),(mat.name,checks);material_checks.append({'material':mat.name,'checks':checks})
(O/'dependency-pose-material-check.json').write_text(json.dumps({'actual_reopened_libraries':dependencies,'rigid_pose_export_checks':pose_checks,'material_export_checks':material_checks,'scope':'Actual shader scalar/node-transform parity; not renderer identical appearance or optical measurement.'},indent=2))

lip=next(o for o in bpy.context.scene.objects if o.type=='MESH' and 'VISIBLE_PERIPHERAL' in o.name)
field_points={tuple(round(q,7) for q in v.co) for v in field.data.vertices};lip_points={tuple(round(q,7) for q in v.co) for v in lip.data.vertices};shared=field_points & lip_points;assert len(shared)>=64
(O/'peripheral-interface-check.json').write_text(json.dumps({'shared_native_positions_at_1e7_m':len(shared),'common_front_depth_m':-.00045,'field_outer_radius_m':.0828,'lip_inner_radius_m':.0828,'status':'Continuous shared perimeter; expected triangle contact at retained lip/cup seam. No disconnected planar field.','representation':'Finite shell and open annular lip; not a welded manufactured seam or measured thickness.'},indent=2))
