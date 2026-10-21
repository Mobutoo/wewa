"""Bake our legacy procedural rubber on its unchanged inspection surface.

No old file is saved. Normal map encodes the original bump once, roughness is
baked through a temporary emission copy. No displacement, retopology or new UV.
Use --preflight-only before the expensive atlas bake. Checkpoints verify source,
geometry, shader parameters, bake settings and PNG before any bake reuse.
"""
from pathlib import Path
import hashlib,json,sys,struct,zlib,time
import bpy
import numpy as np
from mathutils import Vector

H=Path(__file__).resolve().parent;R=H.parents[3]
O=R/'creative/reviews/front-tyre-v2';D=R/'creative/research/front-tyre-material-v2'
T=H/'textures';T.mkdir(exist_ok=True);O.mkdir(exist_ok=True)
P=json.loads((H/'parameters.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=R/P['base_source']['path'];oldglb=R/P['baseline_export']['path']
assert sha(source)==P['base_source']['sha256'] and sha(oldglb)==P['baseline_export']['sha256']
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
col=bpy.data.collections.new('WEWA_FRONT_TYRE_V2_UNCHANGED_INSPECTION');s.collection.children.link(col)
with bpy.data.libraries.load(str(source),link=False)as(a,b):
    assert 'Front tyre - inspection export'in a.objects
    assert 'Original rubber - no photo textures'in a.materials
    b.objects=['Front tyre - inspection export'];b.materials=['Original rubber - no photo textures']
o=b.objects[0];donor=b.materials[0];donor.use_fake_user=True
col.objects.link(o);o.hide_render=False;o.hide_set(False);bpy.context.view_layer.objects.active=o;o.select_set(True)
m=o.data;m.calc_loop_triangles();assert not o.modifiers and len(m.uv_layers)==1
uvname=m.uv_layers[0].name;m.uv_layers.active_index=0;m.uv_layers[0].active_render=True

def digest():
    v=np.empty(len(m.vertices)*3,dtype=np.float32);m.vertices.foreach_get('co',v)
    n=np.empty(len(m.corner_normals)*3,dtype=np.float32);m.corner_normals.foreach_get('vector',n)
    uv=np.empty(len(m.loops)*2,dtype=np.float32);m.uv_layers[0].data.foreach_get('uv',uv)
    li=np.empty(len(m.loops),dtype=np.int32);m.loops.foreach_get('vertex_index',li)
    tri=np.empty(len(m.loop_triangles)*3,dtype=np.int32);m.loop_triangles.foreach_get('loops',tri)
    smooth=np.array([p.use_smooth for p in m.polygons],dtype=np.uint8)
    return hashlib.sha256(b''.join(x.tobytes()for x in[v,n,uv,li,tri,smooth,np.array(o.matrix_world,dtype=np.float64)])).hexdigest()

geometry_digest=digest()
vs=np.array([v.co[:]for v in m.vertices],dtype=np.float64)
ti=np.array([t.vertices[:]for t in m.loop_triangles],dtype=np.int32)
tl=np.array([t.loops[:]for t in m.loop_triangles],dtype=np.int32)
uv=np.array([q.uv[:]for q in m.uv_layers[0].data],dtype=np.float64)
area=np.linalg.norm(np.cross(vs[ti[:,1]]-vs[ti[:,0]],vs[ti[:,2]]-vs[ti[:,0]]),axis=1)*.5
du=uv[tl[:,1]]-uv[tl[:,0]];dv=uv[tl[:,2]]-uv[tl[:,0]];uvarea=np.abs(du[:,0]*dv[:,1]-du[:,1]*dv[:,0])*.5
p=donor.node_tree.nodes.get('Principled BSDF');assert p
fine=next(n for n in donor.node_tree.nodes if n.type=='TEX_NOISE'and n.name=='Rubber micro-grain in physical object metres')
coarse=next(n for n in donor.node_tree.nodes if n.type=='TEX_NOISE'and n.name=='Broad restrained roughness variation, not dirt')
bump=next(n for n in donor.node_tree.nodes if n.type=='BUMP');ramp=next(n for n in donor.node_tree.nodes if n.type=='VALTORGB')
donor_settings={'baseColor_linear':list(p.inputs['Base Color'].default_value),'IOR':p.inputs['IOR'].default_value,
 'metallic':p.inputs['Metallic'].default_value,'fine_noise_scale_per_object_m':fine.inputs['Scale'].default_value,
 'fine_noise_detail':fine.inputs['Detail'].default_value,'coarse_noise_scale_per_object_m':coarse.inputs['Scale'].default_value,
 'coarse_noise_detail':coarse.inputs['Detail'].default_value,'bump_strength':bump.inputs['Strength'].default_value,
 'bump_distance_m':bump.inputs['Distance'].default_value,
 'roughness_ramp':[{'position':q.position,'linear_RGBA':list(q.color)}for q in ramp.color_ramp.elements]}
assert abs(donor_settings['fine_noise_scale_per_object_m']-4300)<.01 and abs(donor_settings['bump_strength']-.18)<1e-6
before={'component_id':P['component_id'],'revision':P['revision'],'old_source_sha256':sha(source),'old_export_sha256':sha(oldglb),
 'script_sha256':sha(Path(__file__)),'scope':'Existing inspection only, no old geometry/UV/modifiers changed; original donor nodes actually loaded.',
 'object':o.name,'source_vertices':len(vs),'source_triangles':len(ti),'loop_count':len(m.loops),'UV_name':uvname,
 'source_native_POSITION_N_UV_topology_matrix_digest':geometry_digest,'min_area_m2':float(area.min()),
 'triangles_area_at_or_below_1e18_m2':int((area<=1e-18).sum()),'UV_collapsed_at_1e20':int((uvarea<=1e-20).sum()),
 'bounds_native_m':{'min':vs.min(axis=0).tolist(),'max':vs.max(axis=0).tolist()},'donor_actual_settings':donor_settings,
 'old_geometric_uncertainties_and_G3_rework_retained':True,'art_accepted':False}
(O/'transfer-preflight.json').write_text(json.dumps(before,indent=2)+'\n')
assert not before['triangles_area_at_or_below_1e18_m2']and not before['UV_collapsed_at_1e20'],before
if '--preflight-only'in sys.argv:
    print('TYRE_MATERIAL_TRANSFER_PREFLIGHT_ONLY',json.dumps(before),flush=True);raise SystemExit

s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=P['bake_samples']
s.render.threads_mode='FIXED';s.render.threads=1
s.render.bake.use_selected_to_active=False;s.render.bake.use_clear=True;s.render.bake.margin=P['bake_margin_pixels']
s.render.bake.normal_space='TANGENT';s.render.bake.normal_r='POS_X';s.render.bake.normal_g='POS_Y';s.render.bake.normal_b='POS_Z'

def png_rgb(path,rgb):
    """Raw8bit RGB, no scene-view transform. Input image rows are bottom-up."""
    rgb=np.asarray(rgb,dtype=np.uint8);h,w,_=rgb.shape
    def chunk(f,kind,data):
        f.write(struct.pack('>I',len(data)));f.write(kind);f.write(data);f.write(struct.pack('>I',zlib.crc32(kind+data)&0xffffffff))
    with path.open('wb')as f:
        f.write(b'\x89PNG\r\n\x1a\n');chunk(f,b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))
        compressor=zlib.compressobj(6);batch=bytearray()
        for row in rgb[::-1]:
            batch.extend(compressor.compress(b'\x00'+row.tobytes()))
            if len(batch)>1024*1024:chunk(f,b'IDAT',bytes(batch));batch.clear()
        batch.extend(compressor.flush());chunk(f,b'IDAT',bytes(batch));chunk(f,b'IEND',b'')

def bake(kind,size,path):
    spec={'old_source_sha256':sha(source),'geometry_digest':geometry_digest,'donor_actual_settings':donor_settings,
      'kind':kind,'size':size,'samples':P['bake_samples'],'margin':P['bake_margin_pixels'],'normal_space':'TANGENT','normal_channels':['POS_X','POS_Y','POS_Z']}
    signature=hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest();cp=O/('checkpoint-bake-'+kind.lower()+'.json')
    if cp.exists():
        q=json.loads(cp.read_text());assert q['signature']==signature and q['PNG_sha256']==sha(path)
        print('REUSE_VERIFIED_BAKE',kind,path,flush=True);return q
    target=bpy.data.images.new('BAKE_TARGET_'+kind,width=size[0],height=size[1],alpha=True,float_buffer=True)
    target.colorspace_settings.name='Non-Color'
    material=donor.copy();material.name='TEMPORARY_BAKE_'+kind;o.data.materials.clear();o.data.materials.append(material)
    nodes=material.node_tree.nodes;links=material.node_tree.links
    if kind=='EMIT':
        ramp_copy=next(n for n in nodes if n.type=='VALTORGB');em=nodes.new('ShaderNodeEmission');links.new(ramp_copy.outputs['Color'],em.inputs['Color']);em.inputs['Strength'].default_value=1
        output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL');links.new(em.outputs['Emission'],output.inputs['Surface'])
    tex=nodes.new('ShaderNodeTexImage');tex.image=target;nodes.active=tex
    bpy.context.view_layer.update();start=time.time();bpy.ops.object.bake(type=kind)
    pixels=np.empty(size[0]*size[1]*4,dtype=np.float32);target.pixels.foreach_get(pixels);pixels=pixels.reshape(size[1],size[0],4)
    assert np.isfinite(pixels).all()and float(pixels[:,:,3].min())>.99,'Atlas uncovered/nonfinite pixels'
    rgb=np.rint(np.clip(pixels[:,:,:3],0,1)*255).astype(np.uint8)
    if kind=='EMIT':rgb=np.stack((np.full(rgb.shape[:2],255,dtype=np.uint8),rgb[:,:,0],np.zeros(rgb.shape[:2],dtype=np.uint8)),axis=-1)
    png_rgb(path,rgb)
    assert path.stat().st_size<95000000,'Keep oversized bake diagnostic, do not silently seal'
    q={'signature':signature,'settings':spec,'PNG_path':str(path.relative_to(R)),'PNG_sha256':sha(path),'PNG_bytes':path.stat().st_size,
      'RGB_min':rgb.min(axis=(0,1)).tolist(),'RGB_max':rgb.max(axis=(0,1)).tolist(),'bake_seconds':time.time()-start,
      'rows_written_top_down_from_Blender_bottom_up':True,'view_transform_applied_to_data':False,'raw_PNG_bits':8,
      'all_pixel_alpha_covered':True,'geometry_digest_unchanged':digest()==geometry_digest}
    assert q['geometry_digest_unchanged'];cp.write_text(json.dumps(q,indent=2)+'\n')
    # No global orphan purge; remove only our temporary material/image.
    o.data.materials.clear();bpy.data.materials.remove(material);bpy.data.images.remove(target)
    print('REAL_NATIVE_BAKE_FINISHED',kind,json.dumps(q),flush=True);return q

normal_path=T/'original-rubber-baked-tangent-normal.png';orm_path=T/'original-rubber-baked-metallic-roughness.png'
normal_check=bake('NORMAL',P['normal_resolution_px'],normal_path)
rough_check=bake('EMIT',P['roughness_resolution_px'],orm_path)
mat=bpy.data.materials.new('Original procedural rubber converted to portable atlas - candidate');mat.use_nodes=True
nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=nodes.get('Principled BSDF')
p.inputs['Base Color'].default_value=donor_settings['baseColor_linear'];p.inputs['IOR'].default_value=donor_settings['IOR'];p.inputs['Metallic'].default_value=0
uvnode=nodes.new('ShaderNodeUVMap');uvnode.uv_map=uvname
normal_image=bpy.data.images.load(str(normal_path),check_existing=False);normal_image.colorspace_settings.name='Non-Color';normal_image.pack();normal_image.filepath='//textures/'+normal_path.name
rough_image=bpy.data.images.load(str(orm_path),check_existing=False);rough_image.colorspace_settings.name='Non-Color';rough_image.pack();rough_image.filepath='//textures/'+orm_path.name
nt=nodes.new('ShaderNodeTexImage');nt.image=normal_image;nt.interpolation='Linear';links.new(uvnode.outputs['UV'],nt.inputs['Vector'])
nm=nodes.new('ShaderNodeNormalMap');nm.uv_map=uvname;nm.inputs['Strength'].default_value=1.;links.new(nt.outputs['Color'],nm.inputs['Color']);links.new(nm.outputs['Normal'],p.inputs['Normal'])
rt=nodes.new('ShaderNodeTexImage');rt.image=rough_image;rt.interpolation='Linear';links.new(uvnode.outputs['UV'],rt.inputs['Vector'])
sep=nodes.new('ShaderNodeSeparateColor');links.new(rt.outputs['Color'],sep.inputs['Color']);links.new(sep.outputs['Green'],p.inputs['Roughness']);links.new(sep.outputs['Blue'],p.inputs['Metallic'])
o.data.materials.clear();o.data.materials.append(mat);o['revision']=P['revision'];o['geometry_change']='None; exact native inspection and UV0 retained';o['art_accepted']=False
assert digest()==geometry_digest
glb=H/'front-tyre-v2-inspection.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True)
assert glb.stat().st_size<95000000
s.world=bpy.data.worlds.new('TYRE MATERIAL REVIEW WORLD');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.18,.20,.23,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.25
for name,loc,power,size in [('KEY',(.7,-.7,1),30,.6),('FILL',(-.5,-.3,.6),12,.6),('EDGE',(.25,.7,.65),20,.5)]:
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;light=bpy.data.objects.new(name,data);s.collection.objects.link(light);light.location=loc;light.rotation_euler=(Vector((0,0,.29))-light.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('FRONT_TYRE_MATERIAL_CAMERA',bpy.data.cameras.new('FRONT_TYRE_MATERIAL_CAMERA'));s.collection.objects.link(cam);s.camera=cam;cam.location=(.7,-.9,.65);cam.rotation_euler=(Vector((0,0,.29))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.72;cam.data.clip_start=.001;cam.data.clip_end=5
s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-.5
newsource=H/'front-tyre-v2.blend';bpy.ops.wm.save_as_mainfile(filepath=str(newsource),compress=True,relative_remap=False)
assert newsource.stat().st_size<95000000 and sha(source)==P['base_source']['sha256']and sha(oldglb)==P['baseline_export']['sha256']
out={**before,'source_sha256':sha(newsource),'export_sha256':sha(glb),'source_bytes':newsource.stat().st_size,'export_bytes':glb.stat().st_size,
 'normal_bake':normal_check,'roughness_bake':rough_check,'native_geometry_digest_preserved':digest()==geometry_digest,
 'original_donor_material_retained':donor.name,'native_comparison_geometry':'Same inspection object, original donor assigned in memory only',
 'normal_strength':1,'PNG_sources_original_procedural_nodes':True,'bake_is_not_an_exact_continuous_shader_or_mobile_qualification':True,
 'new_physical_component_created':False,'art_accepted':False}
(O/'material-build-report.json').write_text(json.dumps(out,indent=2)+'\n');print('FRONT_TYRE_MATERIAL_REVISION_BUILT',json.dumps(out),flush=True)
