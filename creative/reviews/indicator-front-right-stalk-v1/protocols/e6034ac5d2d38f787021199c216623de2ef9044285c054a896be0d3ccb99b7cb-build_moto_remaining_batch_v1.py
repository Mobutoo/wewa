"""Staged production of two documented exterior candidates; no automatic art reception."""
import argparse
import bpy
import hashlib
import json
import math
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from motorcycle_remaining_surfaces_v1 import right_stalk, seat_damper
from blender_component_camera_preflight import check_component_camera

CONFIG = {
 'right-stalk': {'revision':'indicator-front-right-stalk-v1',
   'folder':'indicators-front/right-stalk','id':'MOTO-INDICATOR-FRONT-RIGHT-STALK-001',
   'collection':'WEWA_FRONT_INDICATOR_RIGHT_STALK','builder':right_stalk,
   'plan':'creative/research/indicator-front-right-stalk/G0-G2-plan-v1.json',
   'target':[.03075,0,0], 'color':[.012,.013,.012,1], 'roughness':.40,
   'views':[{'name':'whole-quarter','eye':[.105,-.13,.075],'target':[.03075,0,0],'lens':70},
            {'name':'whole-opposite','eye':[.005,.14,.065],'target':[.03075,0,0],'lens':70},
            {'name':'grooves-detail','eye':[.070,-.058,.030],'target':[.0466,0,0],'lens':85,'crop':True}]},
 'seat-damper': {'revision':'seat-damper-v1','folder':'seat-damper','id':'MOTO-SEAT-DAMPER-001',
   'collection':'WEWA_SEAT_DAMPER_CONTACT_SKIN','builder':seat_damper,
   'plan':'creative/research/seat-damper/G0-G2-front-skin-plan-v1.json',
   'target':[0,0,-.002], 'color':[.012,.013,.012,1], 'roughness':.47,
   'views':[{'name':'whole-contact-face','eye':[.075,-.09,.085],'target':[0,0,-.002],'lens':70},
            {'name':'open-review-boundaries','eye':[-.06,.085,-.065],'target':[0,0,-.002],'lens':70},
            {'name':'grooves-mouth-detail','eye':[.022,-.035,.038],'target':[0,0,-.0006],'lens':70,'crop':True}]},
}
parser=argparse.ArgumentParser()
parser.add_argument('component',choices=CONFIG)
parser.add_argument('stage',choices=['geometry','gray','material','preview','final'])
a=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
c=CONFIG[a.component];rev=c['revision'];H=ROOT/'assets-src/moto-components'/c['folder']
O=ROOT/'creative/reviews'/rev;O.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
protocol=sha(Path(__file__))
params=H/('parameters-study-v2.json'if a.component=='right-stalk'else'parameters-study-v1.json');P=json.loads(params.read_text())
gray_source=H/(rev.replace('-v1','-study-v1')+'.blend')
gray_export=H/(rev.replace('-v1','-study-v1')+'.glb')
source=H/(rev+'.blend');export=H/(rev+'.glb')

def write(name,d):
    (O/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')

def digest(mesh):
    mesh.calc_loop_triangles()
    def f(values):return hashlib.sha256(struct.pack('<'+'f'*len(values),*values)).hexdigest()
    return {'P':f([x for v in mesh.vertices for x in v.co]),
            'N':f([x for n in mesh.corner_normals for x in n.vector]),
            'UV':f([x for v in mesh.uv_layers.active.data for x in v.uv]),
            'I':hashlib.sha256(repr([tuple(t.vertices)for t in mesh.loop_triangles]).encode()).hexdigest()}

def export_selected(path,ob,root):
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);root.select_set(True)
    bpy.context.view_layer.objects.active=ob
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,
        export_apply=True,export_yup=True,export_normals=True,export_texcoords=True,
        export_tangents=False,export_animations=False,export_extras=False)

def configure_scene(s):
    s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=12
    s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False
    s.cycles.max_bounces=6;s.render.threads_mode='FIXED';s.render.threads=2
    s.view_layers[0].cycles.denoising_store_passes=True
    s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100
    s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
    s.view_settings.exposure=0;s.view_settings.gamma=1

if a.stage=='geometry':
    assert (ROOT/c['plan']).exists()
    vertices,normals,faces,uv,meta=c['builder'](P)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version=0
    s=bpy.context.scene;s.unit_settings.system='METRIC';configure_scene(s)
    collection=bpy.data.collections.new(c['collection']);s.collection.children.link(collection)
    root=bpy.data.objects.new(c['id']+' UNPLACED REVIEW DATUM',None);collection.objects.link(root)
    mesh=bpy.data.meshes.new(c['id']+' original bounded exterior')
    mesh.from_pydata(vertices,[],faces);mesh.update()
    assert not mesh.validate(clean_customdata=False)
    layer=mesh.uv_layers.new(name='Original source surface charts');cn=[]
    for poly in mesh.polygons:
        poly.use_smooth=True
        for k,li in enumerate(poly.loop_indices):
            layer.data[li].uv=uv[poly.index][k];cn.append(normals[mesh.loops[li].vertex_index])
    mesh.normals_split_custom_set(cn);mesh.update();mesh.calc_loop_triangles()
    ob=bpy.data.objects.new(c['id']+' exterior candidate',mesh);collection.objects.link(ob);ob.parent=root
    mat=bpy.data.materials.new('Neutral shape gray - no final finish');mat.use_nodes=True
    bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.18,.18,.18,1)
    bs.inputs['Roughness'].default_value=.32;mesh.materials.append(mat)
    edges=Counter(tuple(sorted((i,j)))for f in faces for i,j in zip(f,f[1:]+f[:1]))
    assert all(n in(1,2)for n in edges.values())
    boundary=[e for e,n in edges.items()if n==1];graph=defaultdict(set)
    for i,j in boundary:graph[i].add(j);graph[j].add(i)
    assert all(len(v)==2 for v in graph.values())
    unseen=set(graph);loops=[]
    while unseen:
        stack=[unseen.pop()];count=0
        while stack:
            v=stack.pop();count+=1
            for k in graph[v]:
                if k in unseen:unseen.remove(k);stack.append(k)
        loops.append(count)
    assert sorted(loops)==sorted(meta['expected_boundary_loops']),(loops,meta)
    areas=[t.area for t in mesh.loop_triangles];assert min(areas)>0
    mindot=1.
    for t in mesh.loop_triangles:
        x,y,z=[mesh.vertices[k].co for k in t.vertices];n=(y-x).cross(z-x).normalized()
        for li in t.loops:mindot=min(mindot,n.dot(mesh.corner_normals[li].vector))
    assert mindot>.90,mindot
    world=bpy.data.worlds.new('Original neutral studio');world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Color'].default_value=(.16,.16,.16,1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value=.3;s.world=world
    target=Vector(c['target'])
    for name,offset,power,size in [('Key',(-.05,-.12,.12),1.5,.12),('Fill',(.10,.09,.06),.8,.10),('Rim',(.08,-.06,-.07),1.,.08)]:
        data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='RECTANGLE'
        data.size=size;data.size_y=size*.55;lamp=bpy.data.objects.new(name,data);s.collection.objects.link(lamp)
        lamp.location=target+Vector(offset);lamp.rotation_euler=(target-lamp.location).to_track_quat('-Z','Y').to_euler()
    cam=bpy.data.objects.new('Isolated component camera',bpy.data.cameras.new('Isolated component camera'))
    s.collection.objects.link(cam);s.camera=cam;cam.data.clip_start=.0001;cam.data.clip_end=10
    cam.location=c['views'][0]['eye'];cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=c['views'][0]['lens'];cam.data.sensor_fit='HORIZONTAL';cam.data.sensor_width=36
    ob['scope']=meta['scope'];ob['dimensions']='Authored estimates, not OEM or physical measurements'
    ob['hidden_geometry']='Unmade; review cuts are not manufactured ends';ob['art_accepted']=False
    bpy.ops.wm.save_as_mainfile(filepath=str(gray_source),compress=True);export_selected(gray_export,ob,root)
    write('geometry-build-report.json',{'schema':1,'component_id':c['id'],'revision':gray_source.stem,
        'source_sha256':sha(gray_source),'export_sha256':sha(gray_export),'protocol_sha256':protocol,
        'surface_builder_sha256':sha(ROOT/'tools/motorcycle_remaining_surfaces_v1.py'),
        'parameters_sha256':sha(params),'preparation_sha256':sha(ROOT/c['plan']),
        'object':ob.name,'root':root.name,'collection':c['collection'],'vertices':len(vertices),
        'triangles':len(faces),'minimum_source_triangle_area_m2':min(areas),
        'minimum_source_face_corner_normal_dot':mindot,'boundary_loops':loops,
        'all_other_edges_valence2':True,'metadata':meta,'art_accepted':False})
    print('GEOMETRY_BUILT',rev,len(faces),loops,mindot,flush=True)
    raise SystemExit(0)

geometry=json.loads((O/'geometry-build-report.json').read_text())
assert sha(gray_source)==geometry['source_sha256'] and sha(gray_export)==geometry['export_sha256']
if a.stage=='material':
    gate=json.loads((O/'gray-review.json').read_text())
    assert gate['read_by_agent'] and gate['passed_for_material'] and gate['source_sha256']==sha(gray_source)
    bpy.ops.wm.open_mainfile(filepath=str(gray_source));bpy.context.preferences.filepaths.save_version=0
    ob=bpy.data.objects[geometry['object']];root=bpy.data.objects[geometry['root']];before=digest(ob.data)
    bs=ob.data.materials[0].node_tree.nodes['Principled BSDF']
    bs.inputs['Base Color'].default_value=c['color'];bs.inputs['Metallic'].default_value=0
    bs.inputs['Roughness'].default_value=c['roughness'];bs.inputs['IOR'].default_value=1.46
    ob.data.materials[0].name='Original clean dark exterior - chemistry unmeasured'
    assert before==digest(ob.data)
    bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True);export_selected(export,ob,root)
    bpy.ops.wm.open_mainfile(filepath=str(source));assert before==digest(bpy.data.objects[geometry['object']].data)
    write('source-geometry-check.json',{'schema':1,'component_id':c['id'],'revision':rev,
        'source_sha256':sha(source),'export_sha256':sha(export),'gray_source_sha256':sha(gray_source),
        'object':geometry['object'],'objects':[geometry['object']],'root':geometry['root'],
        'collection':c['collection'],'before_geometry_digests':before,'after_geometry_digests':digest(bpy.data.objects[geometry['object']].data),
        'source_geometry_normals_UV_topology_protected':True,'source_geometry':geometry,
        'material':{'base_color_linear_RGBA':c['color'],'roughness':c['roughness'],'IOR':1.46,'metallic':0,
                    'original_constant_proposal':True,'measured_chemistry_or_hardness':False,'images':[]},
        'scope':geometry['metadata']['scope'],'protocol_sha256':protocol,'art_accepted':False})
    print('MATERIAL_BUILT',rev,flush=True);raise SystemExit(0)

is_gray=a.stage=='gray'
current=gray_source if is_gray else source
check=geometry if is_gray else json.loads((O/'source-geometry-check.json').read_text())
assert sha(current)==check['source_sha256']
if a.stage=='final':
    gate=json.loads((O/'material-preview-review.json').read_text())
    assert gate['read_by_agent'] and gate['passed_for_final_render'] and gate['source_sha256']==sha(source)

def environment(scene,ev=0):
    for ob in scene.objects:
        if ob.type=='LIGHT':ob.hide_render=True
    hdr=ROOT/'app/public/materials/kloppenheim_06_puresky_1k.hdr'
    world=bpy.data.worlds.new('Unchanged source material, neutral sky only');world.use_nodes=True
    nodes=world.node_tree.nodes;links=world.node_tree.links;nodes.clear()
    tex=nodes.new('ShaderNodeTexEnvironment');tex.image=bpy.data.images.load(str(hdr),check_existing=True)
    sky=nodes.new('ShaderNodeBackground');sky.inputs['Strength'].default_value=.3;links.new(tex.outputs['Color'],sky.inputs['Color'])
    back=nodes.new('ShaderNodeBackground');back.inputs['Color'].default_value=(.12,.12,.12,1);back.inputs['Strength'].default_value=2**(-ev)
    ray=nodes.new('ShaderNodeLightPath');mix=nodes.new('ShaderNodeMixShader')
    links.new(ray.outputs['Is Camera Ray'],mix.inputs[0]);links.new(sky.outputs[0],mix.inputs[1]);links.new(back.outputs[0],mix.inputs[2])
    out=nodes.new('ShaderNodeOutputWorld');links.new(mix.outputs[0],out.inputs['Surface']);scene.world=world
    scene.view_settings.exposure=ev
    return {'HDR_sha256':sha(hdr),'HDR_strength':.3,'exposure_EV':ev,'backdrop_compensation':2**(-ev),
            'material_or_white_balance_changed':False,'radiometrically_calibrated':False}

def render_files(scene,name):
    raw=O/'raw';raw.mkdir(exist_ok=True)
    exr=raw/(name+'.exr');png=O/(name+'.png')
    scene.render.image_settings.file_format='OPEN_EXR_MULTILAYER';scene.render.image_settings.color_depth='32'
    scene.render.image_settings.exr_codec='ZIP';scene.render.filepath=str(exr);bpy.ops.render.render(write_still=True)
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_depth='8'
    bpy.data.images['Render Result'].save_render(str(png),scene=scene)
    return {'PNG_path':str(png.relative_to(ROOT)),'PNG_sha256':sha(png),
            'EXR_path':str(exr.relative_to(ROOT)),'EXR_sha256':sha(exr),'actually_saved':True}

views=[]
if is_gray:
    views=[{**v,'name':'gray-'+v['name']}for v in c['views']]
    views.append({**c['views'][2],'name':'reflection-'+c['views'][2]['name'],'reflection':True})
elif a.stage=='preview':
    views=[{**c['views'][0],'name':'preview-studio'},
           {**c['views'][0],'name':'preview-neutral','neutral':True}]
else:
    views=[c['views'][0],c['views'][2],{**c['views'][0],'name':'neutral-outdoor','neutral':True}]

report_name={'gray':'gray-render-report.json','preview':'preview-render-report.json','final':'render-report.json'}[a.stage]
report={'schema':1,'revision':rev,'source_sha256':sha(current),
        'export_sha256':sha(gray_export if is_gray else export),'protocol_sha256':protocol,
        'renderer':'Blender4.3.2 Cycles/OpenImageDenoise CPU','samples':96 if a.stage=='final'else 12,
        'views':[],'art_accepted':False,'physical_iphone_tested':False}
for v in views:
    bpy.ops.wm.open_mainfile(filepath=str(current));s=bpy.context.scene;configure_scene(s)
    s.cycles.samples=96 if a.stage=='final' else 12
    cam=s.camera;cam.location=v['eye'];cam.rotation_euler=(Vector(v['target'])-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type='PERSP';cam.data.lens=v['lens'];cam.data.sensor_fit='HORIZONTAL';cam.data.sensor_width=36
    ob=bpy.data.objects[geometry['object']]
    lighting={'preset':'Unchanged source studio','exposure_EV':0}
    if v.get('reflection'):
        bs=ob.data.materials[0].node_tree.nodes['Principled BSDF'];bs.inputs['Roughness'].default_value=.1
        bs.inputs['Metallic'].default_value=.6
    if v.get('neutral'):
        card_report=O/'neutral-exposure-reference.json'
        if a.stage=='preview':
            lighting=environment(s);ob.hide_render=True
            t=Vector(v['target']);normal=(cam.location-t).normalized();right=cam.matrix_world.to_quaternion()@Vector((1,0,0))
            up=normal.cross(right).normalized();right=up.cross(normal).normalized();size=.015
            me=bpy.data.meshes.new('Original 18 percent diffuse reference card')
            me.from_pydata([tuple(t+size*(x*right+y*up))for x,y in[(-1,-1),(1,-1),(1,1),(-1,1)]],[],[(0,1,2,3)])
            card=bpy.data.objects.new('Actually rendered diffuse18percent reference',me);s.collection.objects.link(card)
            mat=bpy.data.materials.new('Original exact linear diffuse18percent');mat.use_nodes=True
            n=mat.node_tree.nodes;n.clear();bs=n.new('ShaderNodeBsdfDiffuse');bs.inputs['Color'].default_value=(.18,.18,.18,1)
            out=n.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(bs.outputs[0],out.inputs['Surface']);me.materials.append(mat)
            proof=render_files(s,'exposure-reference');im=bpy.data.images.load(str(ROOT/proof['EXR_path']),check_existing=False)
            pixels=list(im.pixels);w,h=im.size;values=[]
            for yy in range(h//2-8,h//2+8):
                for xx in range(w//2-8,w//2+8):
                    i=(yy*w+xx)*4;values.append(.2126*pixels[i]+.7152*pixels[i+1]+.0722*pixels[i+2])
            luminance=sum(values)/len(values);assert luminance>1e-6
            ev=math.log2(.18/luminance);assert -8<ev<8
            card_report.write_text(json.dumps({**proof,'source_sha256':sha(current),
                'HDR_sha256':lighting['HDR_sha256'],'linear_reference_color':.18,
                'actual_center_linear_luminance':luminance,'exposure_EV':ev,
                'scope':'Actual diffuse card and original HDR, not a radiometric calibration'},indent=2)+'\n')
            card.hide_render=True;ob.hide_render=False;lighting=environment(s,ev)
        else:
            proof=json.loads(card_report.read_text());assert proof['source_sha256']==sha(current)
            lighting=environment(s,proof['exposure_EV']);assert lighting['HDR_sha256']==proof['HDR_sha256']
    bpy.context.view_layer.update();frame=check_component_camera(s,[ob],allow_crop=v.get('crop',False),margin=.005)
    cfg={'source_sha256':sha(current),'view':v,'camera_matrix':[list(row)for row in cam.matrix_world],
         'near_far_m':[cam.data.clip_start,cam.data.clip_end],'lens_mm':cam.data.lens,
         'sensor_width_mm':36,'resolution_px':[1000,800],'samples':s.cycles.samples,
         'lighting':lighting,'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,
         'gamma':s.view_settings.gamma,'protocol_sha256':protocol,'source_saved':False,
         'reflection_override_in_memory_only':bool(v.get('reflection'))}
    row={'name':v['name'],**render_files(s,v['name']),'configuration':cfg,
         'configuration_sha256':hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest(),
         'frame_check':frame,'actually_read':False}
    report['views'].append(row);write(report_name,report);print('SAVED',rev,v['name'],flush=True)
assert sha(current)==report['source_sha256']
