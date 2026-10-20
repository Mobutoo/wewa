"""Original Viva Wewa cargo: folded kraft carton, tape, tied cord and fictional label.

blender --background --python assets-src/cargo-lot01/generate_cargo.py
Output defaults to /workspace/wewa-assets/cargo-lot01; override WEWA_CARGO_OUTPUT.
Source shaders are baked with Blender; no third-party photo/model is used.
"""
import bpy
from mathutils import Vector
from pathlib import Path
import math
import json
import hashlib
import os
import random

OUT = Path(os.environ.get('WEWA_CARGO_OUTPUT', '/workspace/wewa-assets/cargo-lot01'))
SOURCE = Path(__file__).resolve().parent
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'textures-2k').mkdir(exist_ok=True)
(OUT / 'textures-1k').mkdir(exist_ok=True)
random.seed(31020)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 8
scene.cycles.use_denoising = False
scene.render.bake.margin = 8
materials = {}
parts = []


def original_surface(name, base_a, base_b, roughness, grain_strength):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    nodes, links = tree.nodes, tree.links
    shader = nodes.get('Principled BSDF')
    tex = nodes.new('ShaderNodeTexCoord')
    cloud = nodes.new('ShaderNodeTexNoise')
    cloud.inputs['Scale'].default_value = 5.2
    cloud.inputs['Detail'].default_value = 3.0
    links.new(tex.outputs['UV'], cloud.inputs['Vector'])
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*base_a, 1)
    ramp.color_ramp.elements[1].color = (*base_b, 1)
    links.new(cloud.outputs['Fac'], ramp.inputs[0])
    links.new(ramp.outputs['Color'], shader.inputs['Base Color'])
    stretch = nodes.new('ShaderNodeVectorMath')
    stretch.operation = 'MULTIPLY'
    stretch.inputs[1].default_value = (1.8, 17.0, 1)
    links.new(tex.outputs['UV'], stretch.inputs[0])
    grain = nodes.new('ShaderNodeTexNoise')
    grain.inputs['Scale'].default_value = 92
    grain.inputs['Detail'].default_value = 2
    grain.inputs['Roughness'].default_value = 0.72
    links.new(stretch.outputs[0], grain.inputs['Vector'])
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = grain_strength
    bump.inputs['Distance'].default_value = 0.00022
    links.new(grain.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], shader.inputs['Normal'])
    r = nodes.new('ShaderNodeMapRange')
    r.inputs['To Min'].default_value = max(0.0, roughness - 0.07)
    r.inputs['To Max'].default_value = min(1.0, roughness + 0.07)
    links.new(grain.outputs['Fac'], r.inputs['Value'])
    links.new(r.outputs[0], shader.inputs['Roughness'])
    materials[name] = mat
    return mat


kraft = original_surface('Carton kraft original', (.32,.185,.082), (.46,.30,.145), .86, .26)
tape = original_surface('Ruban adhésif ambre original', (.31,.155,.056), (.40,.22,.085), .32, .10)
cord = original_surface('Ficelle trois brins originale', (.42,.30,.15), (.62,.49,.29), .82, .25)


def simple_material(name, color, roughness=0.75):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    s = mat.node_tree.nodes.get('Principled BSDF')
    s.inputs['Base Color'].default_value = (*color, 1)
    s.inputs['Roughness'].default_value = roughness
    materials[name] = mat
    return mat


paper = simple_material('Étiquette papier sans marque', (.78,.75,.65), .95)
ink = simple_material('Encre imprimée fictive', (.025,.021,.017), .82)


def bake_surface(mat):
    bpy.ops.mesh.primitive_plane_add(size=1)
    board = bpy.context.object
    board.name = 'TEMP_baking_board'
    board.data.materials.append(mat)
    bpy.context.view_layer.objects.active = board
    board.select_set(True)
    tree = mat.node_tree
    shader = tree.nodes.get('Principled BSDF')
    baked = {}
    for channel in ['basecolor', 'roughness', 'normal']:
        slug = {'Carton kraft original':'kraft','Ruban adhésif ambre original':'tape','Ficelle trois brins originale':'cord'}[mat.name]
        cached = OUT / 'textures-2k' / f'{slug}_{channel}_2k.png'
        if cached.exists():
            image = bpy.data.images.load(str(cached), check_existing=True)
            image.colorspace_settings.name = 'sRGB' if channel == 'basecolor' else 'Non-Color'
            baked[channel] = image
            continue
        image = bpy.data.images.new(mat.name + '_' + channel + '_2k', width=2048, height=2048)
        image.colorspace_settings.name = 'sRGB' if channel == 'basecolor' else 'Non-Color'
        target = tree.nodes.new('ShaderNodeTexImage')
        target.image = image
        tree.nodes.active = target
        if channel == 'basecolor':
            scene.render.bake.use_pass_direct = False
            scene.render.bake.use_pass_indirect = False
            scene.render.bake.use_pass_color = True
            bpy.ops.object.bake(type='DIFFUSE')
        elif channel == 'normal':
            scene.render.bake.normal_space = 'TANGENT'
            bpy.ops.object.bake(type='NORMAL')
        else:
            bpy.ops.object.bake(type='ROUGHNESS')
        slug = {'Carton kraft original':'kraft','Ruban adhésif ambre original':'tape','Ficelle trois brins originale':'cord'}[mat.name]
        image.filepath_raw = str(OUT / 'textures-2k' / f'{slug}_{channel}_2k.png')
        image.file_format = 'PNG'
        image.save()
        baked[channel] = image
    # Retain editable original shaders as well as their baked runtime equivalents.
    original = mat.copy()
    original.name = 'SOURCE procedural ' + mat.name
    original.use_fake_user = True
    # Exportable PBR tree made from the original baked materials.
    tree.nodes.clear()
    output = tree.nodes.new('ShaderNodeOutputMaterial')
    shader = tree.nodes.new('ShaderNodeBsdfPrincipled')
    tree.links.new(shader.outputs[0], output.inputs[0])
    for channel, image in baked.items():
        node = tree.nodes.new('ShaderNodeTexImage')
        node.name = 'PBR_' + channel
        node.image = image
        if channel == 'basecolor':
            tree.links.new(node.outputs['Color'], shader.inputs['Base Color'])
        elif channel == 'roughness':
            tree.links.new(node.outputs['Color'], shader.inputs['Roughness'])
        else:
            normal = tree.nodes.new('ShaderNodeNormalMap')
            tree.links.new(node.outputs['Color'], normal.inputs['Color'])
            tree.links.new(normal.outputs['Normal'], shader.inputs['Normal'])
    bpy.data.objects.remove(board, do_unlink=True)


for surface in [kraft, tape, cord]:
    bake_surface(surface)


def finish(obj, material, bevel=0):
    obj.data.materials.append(material)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    if bevel:
        mod = obj.modifiers.new('Coins papier doucement écrasés', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        bpy.ops.object.modifier_apply(modifier=mod.name)
    if not obj.data.uv_layers:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=1.15192, island_margin=0.025)
        bpy.ops.object.mode_set(mode='OBJECT')
    parts.append(obj)
    bpy.ops.object.select_all(action='DESELECT')
    return obj


def mesh(name, vertices, faces, material, bevel=0):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    return finish(obj, material, bevel)


def panel(name, location, dimensions, material, bevel=.00065):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, material, bevel)


# Four connected walls with subtle bulging and true paper-thickness top edge.
outline = []
for cx,cy,start in [(.166,.146,0),(-.166,.146,90),(-.166,-.146,180),(.166,-.146,270)]:
    for k in range(5):
        a = math.radians(start + k*90/4)
        outline.append((cx + .004*math.cos(a),cy + .004*math.sin(a)))
vertices = []
levels = [.001, .012, .080, .164, .232, .238]
for z in levels:
    bulge = math.sin(z/.24*math.pi)*.0007
    for x,y in outline:
        vertices.append((x + math.copysign(bulge,x), y + math.copysign(bulge*.65,y),z))
n = len(outline)
faces = []
for j in range(len(levels)-1):
    for k in range(n):
        faces.append((j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k))
walls = mesh('Parois continues et plis verticaux du carton',vertices,faces,kraft)
bpy.context.view_layer.objects.active=walls
mod=walls.modifiers.new('Épaisseur carton ondulé 1,8mm','SOLIDIFY')
mod.thickness=.0018
mod.offset=-1
bpy.ops.object.modifier_apply(modifier=mod.name)
for face in walls.data.polygons:
    face.use_smooth=True
# Bottom flaps and closed folded top; split seam stays visible under the tape.
panel('Rabats du fond',(0,0,.0011),(.332,.292,.0022),kraft)
panel('Rabat intérieur avant',(0,-.076,.2358),(.332,.143,.0015),kraft)
panel('Rabat intérieur arrière',(0,.076,.2358),(.332,.143,.0015),kraft)
left=panel('Rabat extérieur gauche',(-.0838,0,.2388),(.1665,.293,.0024),kraft)
right=panel('Rabat extérieur droit',(.0838,0,.23855),(.1665,.293,.0024),kraft)
# Discreet carton manufacturer's glue overlap on the rear face.
panel('Languette de collage du dos',(.145,.1476,.118),(.016,.001,.224),kraft,.0004)
# Thin scored fold-lines at the two hinges, physical paper depressions.
for side in [-1,1]:
    panel('Pli marqué du rabat',(side*.1646,0,.2372),(.0014,.285,.0008),kraft,.00025)


# Continuous tape passes from front wall, across the central seam, onto rear wall.
tape_path=[(-.1506,.176),(-.1506,.226),(-.1495,.2375),(-.145,.2404),(-.105,.2406),(-.04,.2408),(.04,.2407),(.105,.2405),(.145,.2404),(.1501,.2372),(.1507,.222),(.1507,.179)]
verts=[]
for j,(y,z) in enumerate(tape_path):
    edge_wobble=.0006*math.sin(j*2.3)
    verts.extend([(-.024+edge_wobble,y,z),(.024+edge_wobble,y,z)])
faces=[(j*2,j*2+1,j*2+3,j*2+2) for j in range(len(tape_path)-1)]
ribbon=mesh('Ruban central de fermeture et retours sur les faces',verts,faces,tape)
uv=ribbon.data.uv_layers.active or ribbon.data.uv_layers.new(name='UVMap')
for poly in ribbon.data.polygons:
    for li in poly.loop_indices:
        vi=ribbon.data.loops[li].vertex_index
        uv.data[li].uv=(vi%2,vi//2/(len(tape_path)-1))
bpy.context.view_layer.objects.active=ribbon
mod=ribbon.modifiers.new('Film adhésif fin','SOLIDIFY');mod.thickness=.00012
bpy.ops.object.modifier_apply(modifier=mod.name)


def sample_closed_polyline(points, count):
    pts=[Vector(p) for p in points]
    distances=[0]
    for a,b in zip(pts,pts[1:]):distances.append(distances[-1]+(b-a).length)
    result=[]
    for j in range(count+1):
        d=distances[-1]*j/count
        i=next((i for i in range(len(distances)-1) if distances[i+1]>=d),len(distances)-2)
        t=(d-distances[i])/(distances[i+1]-distances[i])
        result.append(pts[i].lerp(pts[i+1],t))
    return result


def tube(name, points, radius, material, sides=5):
    points=[Vector(p) for p in points]
    vv=[]
    for i,p in enumerate(points):
        tangent=(points[min(i+1,len(points)-1)]-points[max(i-1,0)]).normalized()
        other=Vector((1,0,0)) if abs(tangent.x)<.85 else Vector((0,1,0))
        axis=tangent.cross(other).normalized()
        second=tangent.cross(axis).normalized()
        for k in range(sides):
            a=2*math.pi*k/sides
            vv.append(p+radius*(axis*math.cos(a)+second*math.sin(a)))
    ff=[]
    for i in range(len(points)-1):
        for k in range(sides):ff.append((i*sides+k,i*sides+(k+1)%sides,(i+1)*sides+(k+1)%sides,(i+1)*sides+k))
    ff.extend([tuple(reversed(range(sides))),tuple((len(points)-1)*sides+k for k in range(sides))])
    obj=mesh(name,vv,ff,material)
    for p in obj.data.polygons:p.use_smooth=True
    uv=obj.data.uv_layers.active
    for poly in obj.data.polygons:
        for li in poly.loop_indices:
            vi=obj.data.loops[li].vertex_index
            if poly.index >= (len(points)-1)*sides:
                angle=2*math.pi*(vi%sides)/sides
                uv.data[li].uv=(.5+.45*math.cos(angle),.5+.45*math.sin(angle))
            else:
                uv.data[li].uv=((vi%sides)/sides,(vi//sides)/max(1,len(points)-1)*4)
    return obj


# Two independent lashing loops: taut across the carton, rounded around its edges.
for x in [-.104,.104]:
    path=[(x,-.145,-.0015),(x,-.151,.003),(x,-.152,.014),(x,-.152,.228),(x,-.150,.239),(x,-.143,.242),(x,.143,.242),(x,.150,.239),(x,.152,.228),(x,.152,.014),(x,.151,.003),(x,.145,-.0015),(x,-.145,-.0015)]
    centre=sample_closed_polyline(path,98)
    # Three twisted plies form a real silhouette, not a smooth rubber cable.
    for strand in range(3):
        pp=[]
        for i,p in enumerate(centre):
            tangent=(centre[min(i+1,len(centre)-1)]-centre[max(i-1,0)]).normalized()
            axis=tangent.cross(Vector((1,0,0))).normalized()
            second=tangent.cross(axis).normalized()
            angle=2*math.pi*(i/len(centre)*24+strand/3)
            pp.append(p+.00067*(axis*math.cos(angle)+second*math.sin(angle)))
        tube('Ficelle trois brins tendue',pp,.00072,cord,5)
    # Practical crossing at the rear upper surface, small knot and two loose ends.
    for s in [-1,1]:
        knot=[]
        for j in range(29):
            a=2*math.pi*j/28
            knot.append((x+.0068*math.sin(a),.076+s*.0035*math.cos(a),.2442+.0024*math.sin(2*a)))
        tube('Nœud serré au dos du colis',knot,.00125,cord,6)
    tube('Bout de ficelle court',[(x,.078,.244),(x+.016,.088,.243),(x+.028,.104,.242),(x+.032,.117,.242)],.0011,cord,6)
    tube('Bout de ficelle descendant',[(x,.078,.244),(x-.012,.109,.243),(x-.017,.139,.242),(x-.016,.153,.234),(x-.018,.154,.218)],.0011,cord,6)


# A small, slightly skewed paper shipping label. All text is invented geometry.
label=panel('Étiquette papier fictive',( -.057,-.018,.2410),(.071,.096,.00018),paper,.0004)
label.rotation_euler[2]=math.radians(-3)


def print_text(body, location, size, align='LEFT'):
    curve=bpy.data.curves.new('Impression fictive '+body,'FONT')
    curve.body=body
    curve.size=size
    curve.align_x=align
    curve.resolution_u=2
    obj=bpy.data.objects.new('Impression fictive '+body,curve)
    bpy.context.collection.objects.link(obj)
    obj.location=location
    obj.rotation_euler[2]=math.radians(-3)
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
    bpy.context.view_layer.objects.active=obj
    bpy.ops.object.convert(target='MESH')
    return finish(bpy.context.object,ink)


print_text('GOMBE',(-.087,.006,.24116),.0082)
print_text('DEPOT 02',(-.086,-.006,.24117),.005)
print_text('014',(-.086,-.023,.24117),.010)
for i in range(23):
    width=.0005 if i%3 else .00105
    panel('Code fictif sans donnée personnelle',(-.085+i*.00225,-.048,.24117),(width,.012,.00003),ink,.00001)


# Merge only by material; keep five lightweight runtime draw groups.
meshes=[]
for material in [kraft,tape,cord,paper,ink]:
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.data.materials and o.data.materials[0]==material]
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.object.join()
    obj=bpy.context.object
    obj.name={'Carton kraft original':'cargo_kraft','Ruban adhésif ambre original':'cargo_tape','Ficelle trois brins originale':'cargo_rope','Étiquette papier sans marque':'cargo_label','Encre imprimée fictive':'cargo_ink'}[material.name]
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    meshes.append(obj)
    # Consistent geometric normals, especially on scored flap edges.
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT')


def statistics(objects):
    verts=[obj.matrix_world @ Vector(c) for obj in objects for c in obj.bound_box]
    minimum=[min(v[i] for v in verts) for i in range(3)]
    maximum=[max(v[i] for v in verts) for i in range(3)]
    triangles=0
    for obj in objects:obj.data.calc_loop_triangles();triangles+=len(obj.data.loop_triangles)
    return {'triangles':triangles,'meshes':len(objects),'bounds_min_blender_m':minimum,'bounds_max_blender_m':maximum,'dimensions_blender_m':[b-a for a,b in zip(minimum,maximum)]}


high=statistics(meshes)
for image in bpy.data.images:
    if image.name not in ['Render Result','Viewer Node'] and image.source in ['FILE','GENERATED']:image.pack()
scene['asset_status']='original fabrication candidate, user art validation pending'
scene['nominal_carton_dimensions_m']=[.34,.30,.24]
scene['attachment_blender_xyz']=[0,.67,.84]
# Preserve editable original sources with 2K baked maps.
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'cargo-lot01.blend'))
for material in [kraft,tape,cord]:
    for node in material.node_tree.nodes:
        if node.type=='TEX_IMAGE' and node.image:
            image=node.image.copy()
            image.name=node.image.name.replace('_2k','_1k')
            if image.packed_file:
                image.unpack(method='REMOVE')
            image.scale(1024,1024)
            image.filepath_raw=str(OUT/'textures-1k'/(Path(node.image.filepath_raw).name.replace('_2k','_1k')))
            image.file_format='PNG';image.save();node.image=image
bpy.ops.object.select_all(action='DESELECT')
for obj in meshes:obj.select_set(True)
bpy.context.view_layer.objects.active=meshes[0]
for obj in meshes:
    bpy.context.view_layer.objects.active=obj
    triangulate=obj.modifiers.new('Triangulation export et tangentes','TRIANGULATE')
    bpy.ops.object.modifier_apply(modifier=triangulate.name)
bpy.ops.export_scene.gltf(filepath=str(OUT/'cargo-lot01.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_tangents=True,export_cameras=False,export_lights=False)


# Inspection rendering: original model in Blender, explicitly separate from runtime.
ground=simple_material('Sol du plateau de contrôle',(.095,.105,.11),.88)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.004))
bpy.context.object.data.materials.append(ground)
world=bpy.data.worlds.new('Plateau lumière diffuse');world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.38,.43,.49,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.45
scene.world=world
for location,power,size in [((-1.8,-2.3,3.0),320,2.3),((1.6,.8,1.7),200,1.8),((-.5,1.5,2.1),160,1.2)]:
    bpy.ops.object.light_add(type='AREA',location=location)
    obj=bpy.context.object;obj.data.energy=power;obj.data.shape='DISK';obj.data.size=size
    obj.rotation_euler=(Vector((0,0,.12))-obj.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(.67,.81,.61))
camera=bpy.context.object;camera.rotation_euler=(Vector((0,0,.12))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO';camera.data.ortho_scale=.60
scene.camera=camera
scene.view_settings.view_transform='AgX'
scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.cycles.samples=64;scene.cycles.use_denoising=False
scene.render.filepath=str(OUT/'blender-cargo-rear-quarter.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'cargo-inspection.blend'))
bpy.ops.render.render(write_still=True)
camera.location=(-.61,-.72,.55);camera.rotation_euler=(Vector((0,0,.12))-camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(OUT/'blender-cargo-front-quarter.png')
bpy.ops.render.render(write_still=True)

report={'asset_id':'cargo-lot01','name':'Original strapped cardboard parcel validation variant','status':'fabricated_candidate_not_artistically_accepted','original_creation':True,'external_meshes_or_photos':False,'license':'Original project creation for Viva Wewa; no third-party asset incorporated','source_blender':'assets-src/cargo-lot01/cargo-lot01.blend','generator':'assets-src/cargo-lot01/generate_cargo.py','coordinate_convention':'Blender X right / Z up / -Y front; GLB X right / Y up / +Z front','origin':'centre underneath carton body; cord projects slightly below','nominal_carton_dimensions_m':[.34,.30,.24],'suggested_attachment_blender_xyz_m':[0,.67,.84],'geometry':high,'materials':5,'textures':{'source':'Original Blender procedural paper, adhesive and fibre shaders baked 2048px','validation':'1024px basecolor sRGB, roughness and tangent normal non-color','not_photographic_scan':True},'fictitious_label':'GOMBE / DEPOT 02 / 014 and non-encoding decorative bars; no third-party brand','inventory_warning':'Pure graphic validation loadout; does not establish carried inventory in the game','bag_clearance':'Front of carton nominal Y=.52m after attachment; rider backpack near Y=.20m; combined-scene intersection still to inspect','limitations':['Not accepted artistically','No physical Safari qualification','Ropes do not dynamically deform with cargo','No original satellite or press photograph used as texture','Renderings are Blender inspection images, not gameplay evidence'],'files':[]}
for path in sorted(OUT.glob('textures-*/*.png'))+list(OUT.glob('*.glb')):
    data=path.read_bytes();report['files'].append({'path':str(path.relative_to(OUT)),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
(OUT/'provenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(SOURCE/'provenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('WEWA_CARGO_REPORT '+json.dumps(report))
