"""Blender production assembly from licensed anatomical/clothing sources.

Uses MakeHuman CC0 graphical data, NOT its AGPL program code.
Run: blender --background --python assets-src/hero-lot01/build_rider.py -- --config /path/to/inputs.json
The source rig, original UVs and skinning are retained. No game asset is overwritten.
"""
import argparse
import gzip
import json
import math
import re
from pathlib import Path
import sys

import bpy
import bmesh
from mathutils import Matrix, Vector

parser = argparse.ArgumentParser()
parser.add_argument('--config', type=Path, required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
cfg = json.loads(args.config.read_text())
out = Path(cfg['output']).resolve(); out.mkdir(parents=True, exist_ok=True)
data = Path(cfg['anatomy']).resolve()
bpy.ops.wm.read_factory_settings(use_empty=True)


def read_obj(path):
    vertices, uvs, faces, face_uvs, groups = [], [], [], [], {}
    group = 'default'
    for line in path.read_text().splitlines():
        fields = line.split()
        if not fields: continue
        if fields[0] == 'v': vertices.append(Vector(tuple(map(float, fields[1:4]))))
        elif fields[0] == 'vt': uvs.append(tuple(map(float, fields[1:3])))
        elif fields[0] == 'g': group = fields[1]
        elif fields[0] == 'f':
            fields = [s.split('/') for s in fields[1:]]
            indices = [int(s[0]) - 1 for s in fields]
            groups.setdefault(group, set()).update(indices)
            faces.append((indices, group))
            face_uvs.append([int(s[1])-1 if len(s)>1 and s[1] else 0 for s in fields])
    return vertices, uvs, faces, face_uvs, groups


base, base_uv, base_faces, base_face_uv, group_vertices = read_obj(data/'base.obj')
for line in gzip.decompress((data/'african-male-young.target.gz').read_bytes()).decode().splitlines():
    fields = line.split()
    if len(fields) == 4 and not fields[0].startswith('#'):
        base[int(fields[0])] += Vector(tuple(map(float, fields[1:])))
body_indices = group_vertices['body']
minimum_y = min(base[i].y for i in body_indices)
height = max(base[i].y for i in body_indices)-minimum_y
scale = 1.74 / height
def convert(v): return Vector((v.x*scale, -v.z*scale, (v.y-minimum_y)*scale))
body_coords = [convert(v) for v in base]
rig_spec = json.loads((data/'rig.game_engine.json').read_text())
source_weights = json.loads((data/'weights.game_engine.json').read_text())['weights']
by_vertex = [{} for _ in base]
for bone, pairs in source_weights.items():
    for i, weight in pairs:
        if weight > .0001: by_vertex[i][bone] = weight


def joint(spec):
    if spec.get('strategy') == 'CUBE': ids = group_vertices[spec['cube_name']]
    elif spec.get('vertex_indices'): ids = spec['vertex_indices']
    else:
        # Default positions are stored in Blender metres in the MPFB rig.
        p = Vector(spec['default_position'])
        return Vector((p.x, p.y, p.z-minimum_y*scale))
    return sum((body_coords[i] for i in ids), Vector()) / len(ids)


arm_data = bpy.data.armatures.new('Source anatomical skeleton')
arm = bpy.data.objects.new('SourceRig', arm_data); bpy.context.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm; arm.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
for name, desc in rig_spec.items():
    bone = arm_data.edit_bones.new(name); bone.head = joint(desc['head']); bone.tail = joint(desc['tail'])
    if (bone.tail-bone.head).length < .001: bone.tail = bone.head+Vector((0,0,.02))
    bone.roll = desc.get('roll',0)
for name, desc in rig_spec.items():
    if desc.get('parent'): arm_data.edit_bones[name].parent=arm_data.edit_bones[desc['parent']]
bpy.ops.object.mode_set(mode='OBJECT')


def pbr(name, color, rough=.6, metal=0, texture=None, normal=None, tint=None):
    material = bpy.data.materials.new(name); material.use_nodes=True
    material.diffuse_color=(*color,1)
    bsdf=material.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value=(*color,1);bsdf.inputs['Roughness'].default_value=rough;bsdf.inputs['Metallic'].default_value=metal
    if texture:
        image=bpy.data.images.load(str(texture),check_existing=True)
        node=material.node_tree.nodes.new('ShaderNodeTexImage');node.image=image
        if tint:
            multiply=material.node_tree.nodes.new('ShaderNodeMixRGB');multiply.blend_type='MULTIPLY';multiply.inputs[0].default_value=1;multiply.inputs[2].default_value=(*tint,1)
            material.node_tree.links.new(node.outputs['Color'],multiply.inputs[1]);material.node_tree.links.new(multiply.outputs['Color'],bsdf.inputs['Base Color'])
        else:material.node_tree.links.new(node.outputs['Color'],bsdf.inputs['Base Color'])
    if normal:
        image=bpy.data.images.load(str(normal),check_existing=True);image.colorspace_settings.name='Non-Color'
        node=material.node_tree.nodes.new('ShaderNodeTexImage');node.image=image
        n=material.node_tree.nodes.new('ShaderNodeNormalMap')
        material.node_tree.links.new(node.outputs['Color'],n.inputs['Color']);material.node_tree.links.new(n.outputs['Normal'],bsdf.inputs['Normal'])
    return material


skin=pbr('Skin CC0 photographic source',(.18,.085,.045),.62,texture=Path(cfg['skin']) if cfg.get('skin') else None)
cloth=pbr('Backpack dark brown woven textile',(.045,.028,.012),.86,texture=Path(cfg['backpack_albedo']) if cfg.get('backpack_albedo') else None,normal=Path(cfg['backpack_normal']) if cfg.get('backpack_normal') else None)
shell=pbr('Helmet satin charcoal',(.015,.019,.022),.34)
rubber=pbr('Helmet trim and buckles',(.008,.01,.012),.76)
metal=pbr('Fasteners brushed alloy',(.35,.37,.39),.32,.8)
seam=pbr('Backpack seam thread',(.10,.095,.075),.85)


def mesh_object(name, coords, faces, uvs, face_uvs, weights, material, parent_rig=arm):
    # Remove unused hidden source vertices; preserve authoritative weights and UV seams.
    used=sorted({i for face in faces for i in face}); remap={old:i for i,old in enumerate(used)}
    mesh=bpy.data.meshes.new(name);mesh.from_pydata([coords[i] for i in used],[],[[remap[i] for i in face] for face in faces]);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);mesh.materials.append(material)
    uv=mesh.uv_layers.new(name='UVMap')
    for polygon, indices in zip(mesh.polygons,face_uvs):
        polygon.use_smooth=True
        for loop, index in zip(polygon.loop_indices,indices): uv.data[loop].uv=uvs[index] if uvs else (0,0)
    groups={}
    for old,new in remap.items():
        ww=sorted([(k,v) for k,v in weights[old].items() if v>0],key=lambda x:-x[1])[:4]; total=sum(v for _,v in ww)
        if total < .0001: ww=[('pelvis',1)]; total=1
        for name,weight in ww:
            if name not in groups: groups[name]=obj.vertex_groups.new(name=name)
            groups[name].add([new],weight/total,'REPLACE')
    mod=obj.modifiers.new('Anatomical skinning','ARMATURE');mod.object=parent_rig
    obj.parent=parent_rig
    return obj


outfit_objects=[]; hidden=set()
for clothing_path in cfg.get('clothes',[]):
    path=Path(clothing_path)
    lines=path.read_text().splitlines();header={};bindings=[];section='header';delete=[]
    for line in lines:
        text=line.strip()
        if not text or text.startswith('#'):continue
        fields=text.split()
        if text in ['verts 0','verts']:section='verts';continue
        if text=='delete_verts':section='delete';continue
        if section=='header':header[fields[0]]=fields[1:]
        elif section=='verts':
            if fields[0].lstrip('-').isdigit():bindings.append(fields)
            else:section='other'
        elif section=='delete': delete.extend(fields)
    for token in re.findall(r'\d+(?:\s*-\s*\d+)?',' '.join(delete)):
        if '-' in token:
            try:a,b=map(int,token.split('-'));hidden.update(range(a,b+1))
            except ValueError:pass
        elif token.isdigit():hidden.add(int(token))
    objpath=path.parent/' '.join(header['obj_file'])
    vv,uvs,faces,fuvs,_=read_obj(objpath)
    fitted=[];ww=[]
    axis_scale=[]
    for axis,key in enumerate(['x_scale','y_scale','z_scale']):
        values=header.get(key)
        axis_scale.append(abs(base[int(values[0])][axis]-base[int(values[1])][axis])/float(values[2]) if values else 1)
    if len(bindings)!=len(vv): raise ValueError(f'Binding count differs: {path}: {len(bindings)} vs {len(vv)}')
    for binding in bindings:
        if len(binding)==1:ids=[int(binding[0])]; factors=[1];offset=Vector()
        else:
            ids=list(map(int,binding[:3]));factors=list(map(float,binding[3:6]));offset=Vector(tuple(float(v)*s for v,s in zip(binding[6:9],axis_scale)))
        p=sum((base[i]*factor for i,factor in zip(ids,factors)),Vector())+offset
        fitted.append(convert(p));weights={}
        for i,factor in zip(ids,factors):
            for name,value in by_vertex[i].items():weights[name]=weights.get(name,0)+value*factor
        ww.append(weights)
    mat_path=path.parent/' '.join(header.get('material',[]))
    mat_header={}
    if mat_path.is_file():
        for l in mat_path.read_text().splitlines():
            fields=l.split(maxsplit=1)
            if len(fields)==2:mat_header[fields[0]]=fields[1]
    texture=path.parent/mat_header['diffuseTexture'] if mat_header.get('diffuseTexture') else None
    normal=path.parent/mat_header['normalmapTexture'] if mat_header.get('normalmapTexture') else None
    material=pbr(path.stem,tuple(map(float,mat_header.get('diffuseColor','.15 .18 .22').split()[:3])),.8,texture=texture if texture and texture.exists() else None,normal=normal if normal and normal.exists() else None,tint=(.15,.21,.29) if 'casualsuit' in path.stem else None)
    outfit_objects.append(mesh_object('Garment_'+path.stem,fitted,[f for f,_ in faces],uvs,fuvs,ww,material))

visible=[(i,face) for i,(face,group) in enumerate(base_faces) if group=='body' and not any(v in hidden for v in face)]
body=mesh_object('Rider_anatomical_skin',body_coords,[face for i,face in visible],base_uv,[base_face_uv[i] for i,face in visible],by_vertex,skin)
outfit_objects.append(body)

# Pose the real anatomical skeleton using end effectors at grips and pegs.
for name in ['spine_01','spine_02','spine_03']:
    pb=arm.pose.bones[name];pb.rotation_mode='XYZ';pb.rotation_euler.x=.075
arm.pose.bones['neck_01'].rotation_mode='XYZ';arm.pose.bones['neck_01'].rotation_euler.x=-.12
bpy.context.view_layer.update()
hip=arm.pose.bones['pelvis'].head.copy()
translation=Vector((0,.09,.875))-hip
arm.location+=translation
bpy.context.view_layer.update()
targets=[]
for side,sign in [('l',1),('r',-1)]:
    for bone,point,pole,desired_joint in [
        ('calf_'+side,(sign*.18,.04,.365),(sign*.45,-.6,.62),(sign*.21,-.29,.60)),
        ('lowerarm_'+side,(sign*.31,-.240,.983),(sign*.5,-.10,1.06),(sign*.28,-.08,1.13))]:
        target=bpy.data.objects.new('IK_'+bone,None);bpy.context.collection.objects.link(target);target.location=point
        pole_obj=bpy.data.objects.new('Pole_'+bone,None);bpy.context.collection.objects.link(pole_obj);pole_obj.location=pole
        ik=arm.pose.bones[bone].constraints.new('IK');ik.target=target;ik.pole_target=pole_obj;ik.chain_count=2
        options=[]
        for angle in [0,math.pi/2,-math.pi/2,math.pi]:
            ik.pole_angle=angle;bpy.context.view_layer.update()
            joint_position=arm.matrix_world@arm.pose.bones[bone].head
            options.append(((joint_position-Vector(desired_joint)).length,angle))
        ik.pole_angle=min(options)[1];targets.extend([target,pole_obj])
    # Keep feet along the peg; hands aim forward around the rubber grip.
    for bone in ['foot_'+side,'hand_'+side]:
        pb=arm.pose.bones[bone];pb.rotation_mode='QUATERNION'
        bpy.context.view_layer.update()
        desired=Vector((0,-1,.04 if bone.startswith('hand') else .03))
        current=(pb.tail-pb.head).normalized()
        matrix=desired.rotation_difference(current)
        # Global alignment, preserving anatomical joint position.
        q=current.rotation_difference(desired)
        m=pb.matrix.copy();m=q.to_matrix().to_4x4()@m;m.translation=pb.head;pb.matrix=m
    for finger in ['index','middle','ring','pinky']:
        for j,angle in [(1,.4),(2,.65),(3,.55)]:
            pb=arm.pose.bones[f'{finger}_{j:02d}_{side}'];pb.rotation_mode='XYZ';pb.rotation_euler.x=angle
bpy.context.view_layer.update()

# Freeze the fitted pose into a seated rest skeleton while keeping weights editable.
deps=bpy.context.evaluated_depsgraph_get()
posed_bones={b.name:(arm.matrix_world@b.matrix,b.length) for b in arm.pose.bones}
(out/'pose-debug.json').write_text(json.dumps({'arm_location':list(arm.location),'source_posed':{b.name:{'head':list(arm.matrix_world@b.head),'tail':list(arm.matrix_world@b.tail),'matrix_translation':list((arm.matrix_world@b.matrix).translation)} for b in arm.pose.bones if b.name in ['pelvis','head','hand_l','foot_l','spine_03']}},indent=2))
for obj in outfit_objects:
    evaluated=obj.evaluated_get(deps)
    evaluated_mesh=bpy.data.meshes.new_from_object(evaluated,depsgraph=deps)
    world=obj.matrix_world.copy();obj.modifiers.clear();obj.parent=None;obj.matrix_world=Matrix.Identity(4)
    for v in evaluated_mesh.vertices:v.co=world@v.co
    obj.data=evaluated_mesh
new_data=bpy.data.armatures.new('Seated production rig')
rig=bpy.data.objects.new('RiderRig',new_data);bpy.context.collection.objects.link(rig)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
for name,(matrix,length) in posed_bones.items():
    bone=new_data.edit_bones.new(name);bone.head=(0,0,0);bone.tail=(0,length,0);bone.matrix=matrix;bone.length=length
for name,desc in rig_spec.items():
    if desc.get('parent'):new_data.edit_bones[name].parent=new_data.edit_bones[desc['parent']]
bpy.ops.object.mode_set(mode='OBJECT')
for obj in outfit_objects:
    obj.parent=rig;mod=obj.modifiers.new('Production seated skinning','ARMATURE');mod.object=rig
bpy.data.objects.remove(arm,do_unlink=True)
for obj in targets:bpy.data.objects.remove(obj,do_unlink=True)


def attach(obj,material,bone='spine_03'):
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
    obj.data.materials.append(material)
    bpy.context.view_layer.objects.active=obj;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    if not obj.data.uv_layers:
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
    vg=obj.vertex_groups.new(name=bone);vg.add(list(range(len(obj.data.vertices))),1,'REPLACE')
    obj.parent=rig;mod=obj.modifiers.new('Equipment follows rider','ARMATURE');mod.object=rig
    for p in obj.data.polygons:p.use_smooth=True
    outfit_objects.append(obj)
    return obj


def box(name,center,size,material,bevel=.015,bone='spine_03'):
    bpy.ops.mesh.primitive_cube_add(size=1,location=center);obj=bpy.context.object;obj.name=name;obj.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=obj.modifiers.new('Sewn soft edge','BEVEL');mod.width=bevel;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
    # Real UV coordinates before source photo texture assignment.
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
    return attach(obj,material,bone)


def tube(name,points,radius,material,bone='spine_03'):
    bpy.ops.object.select_all(action='DESELECT')
    curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.resolution_u=8;curve.bevel_depth=radius;curve.bevel_resolution=2
    spline=curve.splines.new('POLY');spline.points.add(len(points)-1)
    for point,co in zip(spline.points,points):point.co=(*co,1)
    obj=bpy.data.objects.new(name,curve);bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj;obj.select_set(True)
    bpy.ops.object.convert(target='MESH');obj=bpy.context.object
    return attach(obj,material,bone)


def ribbon(name,points,width,material):
    vertices=[];faces=[]
    for point in points:
        for side in [-1,1]:vertices.append((point[0]+side*width/2,point[1],point[2]))
    for i in range(len(points)-1):faces.append((2*i,2*i+1,2*i+3,2*i+2))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
    sub=obj.modifiers.new('Soft webbing curvature','SUBSURF');sub.levels=2;bpy.ops.object.modifier_apply(modifier=sub.name)
    solid=obj.modifiers.new('Woven webbing thickness','SOLIDIFY');solid.thickness=.004;bpy.ops.object.modifier_apply(modifier=solid.name)
    return attach(obj,material)


# Backpack has a rounded sewn volume, flat pockets, piping, hardware and fabric straps.
chest=rig.data.bones['spine_03'].tail_local
coat=next(obj for obj in outfit_objects if obj.name.startswith('Garment_male_casualsuit'))
def back_surface(z):
    candidates=[v.co.y for v in coat.data.vertices if abs(v.co.x)<.13 and abs(v.co.z-z)<.035]
    return max(candidates) if candidates else chest.y+.02
pack_z=chest.z-.025
pack_angle=max(0,min(.45,math.atan2(back_surface(pack_z-.12)-back_surface(pack_z+.12),.24)))
pack_rotation=Matrix.Rotation(pack_angle,3,'X')
pack_center=Vector((0,back_surface(pack_z)+.06*math.cos(pack_angle)+.006,pack_z))
def pack_point(point):return tuple(pack_center+pack_rotation@Vector(point))
box('Backpack main sewn body',pack_center,(.29,.12,.35),cloth,.045)
box('Backpack zipped front pocket',pack_center+Vector((0,.074,-.065)),(.245,.045,.18),cloth,.025)
for sign in [-1,1]:
    tube('Backpack perimeter seam',[(sign*.126,pack_center.y+.067,pack_center.z-.125),(sign*.138,pack_center.y+.066,pack_center.z+.08),(sign*.10,pack_center.y+.06,pack_center.z+.15)],.0013,seam)
    ribbon('Curved fabric shoulder strap',[pack_point((sign*.105,-.04,.14)),(sign*.13,chest.y-.045,chest.z+.16),(sign*.145,chest.y-.17,chest.z+.12),(sign*.15,chest.y-.23,chest.z+.02),(sign*.16,chest.y-.20,chest.z-.10),(sign*.18,chest.y-.055,chest.z-.16),pack_point((sign*.12,-.04,-.14))],.032,cloth)
    box('Webbing adjustment buckle',(sign*.16,chest.y-.20,chest.z-.075),(.035,.012,.026),rubber,.004)
    box('Side elastic pocket',pack_center+Vector((sign*.145,.01,-.065)),(.025,.08,.11),cloth,.012)
tube('Backpack carry handle',[tuple(pack_center+Vector((x,-.01,z))) for x,z in [(-.045,.17),(-.035,.20),(.035,.20),(.045,.17)]],.006,cloth)
box('Backpack zipper slider',pack_center+Vector((.10,.102,.02)),(.009,.008,.018),metal,.002)
# Fit the bag against the actual jacket surface and lean it with the back.
# Shoulder webbing follows its own body-contact path rather than rotating as a rigid box.
for obj in outfit_objects:
    if obj.name.startswith(('Backpack','Side elastic pocket')):
        for vertex in obj.data.vertices:vertex.co=pack_center+pack_rotation@(vertex.co-pack_center)

# Original open-face helmet follows the head; proper cut-out rather than a full sphere.
head=rig.data.bones['head']; center=(head.head_local+head.tail_local)/2
center.z-=.01; center.y-=.015
verts=[];faces=[];rings=14;segments=48
for j in range(rings+1):
    phi=.02+(math.pi*.69-.02)*j/rings
    for i in range(segments):
        theta=i*math.tau/segments
        verts.append((center.x+.122*math.sin(phi)*math.cos(theta),center.y+.132*math.sin(phi)*math.sin(theta),center.z+.135*math.cos(phi)))
for j in range(rings):
    for i in range(segments):
        theta=(i+.5)*math.tau/segments
        # Leave the front face open below the brow, with cheeks covered on each side.
        if j>6 and math.sin(theta)<-.63:continue
        faces.append((j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i))
mesh=bpy.data.meshes.new('Helmet shaped shell');mesh.from_pydata(verts,[],faces);mesh.update()
helmet=bpy.data.objects.new('Helmet original jet shell',mesh);bpy.context.collection.objects.link(helmet)
bpy.context.view_layer.objects.active=helmet
solid=helmet.modifiers.new('Shell and inner edge thickness','SOLIDIFY');solid.thickness=.005;bpy.ops.object.modifier_apply(modifier=solid.name)
attach(helmet,shell,'head')
for sign in [-1,1]:
    box('Helmet visor hinge',(sign*.119,center.y-.01,center.z+.005),(.009,.025,.025),metal,.007,'head')
    tube('Helmet chin strap',[(sign*.10,center.y-.01,center.z-.07),(sign*.075,center.y-.075,center.z-.145),(sign*.02,center.y-.085,center.z-.15)],.006,rubber,'head')
box('Helmet strap buckle',(.02,center.y-.088,center.z-.15),(.027,.014,.016),rubber,.003,'head')

# A subtle real skeletal animation is included for inspection, not an artificial camera effect.
bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=61
for frame,angle in [(1,0),(16,.006),(31,0),(46,-.006),(61,0)]:
    for name in ['spine_02','spine_03']:
        pb=rig.pose.bones[name];pb.rotation_mode='XYZ';pb.rotation_euler.z=angle
        pb.keyframe_insert(data_path='rotation_euler',frame=frame,group=name)
if rig.animation_data and rig.animation_data.action:rig.animation_data.action.name='Rider seated idle - review only'
bpy.context.scene.frame_set(1)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
for obj in outfit_objects:obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'rider-review.glb'),export_format='GLB',use_selection=True,export_yup=True,export_tangents=True,export_animations=True,export_skins=True,export_morph=False,export_cameras=False,export_lights=False)

# Separate first-person sleeves/hands use the very same anatomical surface and grip pose.
# They omit the head/torso/backpack, which would obstruct an eye-level camera.
viewmodels=[]
for source in outfit_objects:
    if source!=body and not source.name.startswith('Garment_male_casualsuit'):continue
    clone=source.copy();clone.data=source.data.copy();clone.name='FirstPerson_'+source.name;bpy.context.collection.objects.link(clone)
    groups={g.index:g.name for g in clone.vertex_groups}
    def arm_weight(vertex):
        return sum(g.weight for g in vertex.groups if any(word in groups[g.group] for word in ['arm','hand','index','middle','ring','pinky','thumb']))
    allowed={v.index for v in clone.data.vertices if arm_weight(v)>.35}
    bm=bmesh.new();bm.from_mesh(clone.data);bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index not in allowed],context='VERTS');bm.to_mesh(clone.data);bm.free()
    viewmodels.append(clone)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
for obj in viewmodels:obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'firstperson-review.glb'),export_format='GLB',use_selection=True,export_yup=True,export_tangents=True,export_animations=False,export_skins=True,export_morph=False,export_cameras=False,export_lights=False)
for obj in viewmodels:bpy.data.objects.remove(obj,do_unlink=True)

# Save a source scene before adding the motorcycle and studio presentation.
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'rider-production.blend'))
for obj in outfit_objects:obj.data.calc_loop_triangles()
stats={'status':'fabricated_for_user_review_not_accepted','source':'MakeHuman CC0 graphical data + original equipment and assembly',
       'standing_anatomical_height_m':1.74,'bones':len(rig.data.bones),'meshes':len(outfit_objects),
       'triangles':sum(len(obj.data.loop_triangles) for obj in outfit_objects),
       'hands_world_m':{side:list(rig.data.bones['hand_'+side].head_local) for side in ['l','r']},
       'feet_world_m':{side:list(rig.data.bones['foot_'+side].head_local) for side in ['l','r']},
       'helmet_center_blender_xyz':list(center),
       'backpack_fit':{'center_blender_xyz':list(pack_center),'forward_tilt_radians':pack_angle,'target_back_clearance_m':.006},
       'firstperson_export':'firstperson-review.glb: separate sleeves and anatomical hands using the same grip pose',
       'limitations':['First fabricated rider lot awaiting art and posture review.','Idle only; dynamic steering/grip adaptation and physical iPhone qualification pending.','City rendering unchanged.']}
(out/'fabrication-report.json').write_text(json.dumps(stats,indent=2)+'\n')
print('FABRICATION_REPORT '+json.dumps(stats),flush=True)
if not cfg.get('render',True):sys.exit(0)

if cfg.get('motorcycle'):
    bpy.ops.import_scene.gltf(filepath=str(Path(cfg['motorcycle'])))
    # The glTF importer restores Blender Z up and forward -Y.
if cfg.get('cargo'):
    previous=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(Path(cfg['cargo'])))
    imported=set(bpy.data.objects)-previous
    for obj in imported:
        if obj.parent not in imported:obj.location+=Vector((0,.67,.83))
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.004));ground=bpy.context.object;ground.name='Studio ground - not exported'
ground.data.materials.append(pbr('Studio ground',(.09,.105,.11),.86))
for loc,power,size in [((3,-4,5),650,4),((-3,-1,3),350,3),((0,4,4),850,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object;light.data.energy=power;light.data.size=size
    light.rotation_euler=(Vector((0,0,.9))-light.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene
if scene.world is None:scene.world=bpy.data.worlds.new('Studio ambient')
scene.world.color=(.2,.2,.2);scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.use_denoising=False
scene.render.resolution_x=1280;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX'
bpy.ops.object.camera_add();camera=bpy.context.object;scene.camera=camera;camera.data.type='ORTHO';camera.data.ortho_scale=2.65
for name,location in [('rear-quarter',(2.6,4,2.2)),('side', (4.5,.1,1.65)),('front-quarter',(2.6,-4,2.1))]:
    if cfg.get('render_views') and name not in cfg['render_views']:continue
    camera.location=location;camera.rotation_euler=(Vector((0,0,.95))-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'combined-review.blend'))
