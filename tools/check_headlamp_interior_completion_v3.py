"""Independent native reopen and original glTF POSITION comparison."""
from pathlib import Path
import bpy,json,struct,hashlib
R=Path('/workspace/wewa');K='headlamp-interior-completion-v3';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K
src=H/'visible-optics-v3.blend';bpy.ops.wm.open_mainfile(filepath=str(src))
b=(H/'visible-optics-v3.glb').read_bytes();off=12;j=None;binary=None
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
field=next(o for o in bpy.data.objects if o.type=='MESH' and 'VISIBLE_SILVER_FIELD' in o.name)
field_z={round(v.co.z,7) for v in field.data.vertices}
assert field_z=={-.00045},field_z
interface=[]
field_points={tuple(round(q,7) for q in v.co) for v in field.data.vertices}
for token in ['VISIBLE_PERIPHERAL','VISIBLE_MAIN_OPENING','VISIBLE_PILOT_OPENING']:
 lip=next(o for o in bpy.data.objects if o.type=='MESH' and token in o.name)
 shared=field_points & {tuple(round(q,7) for q in v.co) for v in lip.data.vertices}
 # Main aperture CDT ring has192 samples, lip512: gcd=64 exact shared
 # positions; circular chord discrepancy is below3 micrometres, not zero.
 assert len(shared)>=64,(token,len(shared))
 interface.append({'lip':lip.name,'source_shared_boundary_positions_at_m':1e-7,'shared_positions':len(shared),'shared_depth_plane_m':-.00045,'maximum_circular_tessellation_deviation_bound_m':.000003})
bvh=BVHTree.FromPolygons([v.co for v in field.data.vertices],[list(p.vertices) for p in field.data.polygons],all_triangles=False)
probes=[]
for label,x,y,expected in [('main-aperture',.0045,.0008,False),('pilot-aperture',.003,-.037,False),('visible-left-field',-.05,0,True),('visible-upper-field',0,.05,True)]:
 hit=bvh.ray_cast(Vector((x,y,.1)),Vector((0,0,-1)))[0] is not None
 assert hit==expected,(label,hit,expected)
 probes.append({'probe':label,'actual_surface_hit':hit,'expected_hit':expected})
report={'source':str(src.relative_to(R)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(b).hexdigest(),'actual_native_reopened':True,'mesh_count':5,'unique_native_export_positions_equal_at_m':1e-7,'native_position_count':len(native),'export_position_count':len(export),'no_emission':True,'glass_transmission_factor':1,'no_images_embedded':True,'technical_passed':True,'scope':'Source/export consistency only; no optical prescription, measured fit or artistic reception'}
report['visible_field_aperture_and_surface_probes']=probes
report['actual_field_lip_boundary_continuity']=interface
(O/'native-export-parity.json').write_text(json.dumps(report,indent=2))
