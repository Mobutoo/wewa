"""Blender: photo-guided related fuel-tap exterior only; originals and concealed mechanism are excluded."""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'assets-src/moto-components/fuel-tap-visible-body-v1'
REVIEW=ROOT/'creative/reviews/fuel-tap-visible-body-v1'
parser=argparse.ArgumentParser();parser.add_argument('--finish',action='store_true')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
FOLDER.mkdir(parents=True,exist_ok=True);REVIEW.mkdir(parents=True,exist_ok=True);(REVIEW/'raw').mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parts=[]


def cylinder(name,axis,start,end,radius,center,vertices=128):
    midpoint=Vector(center);midpoint[axis]=(start+end)/2
    direction=Vector(tuple(1 if i==axis else 0 for i in range(3)))
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=end-start,location=midpoint)
    obj=bpy.context.object;obj.name=name;obj.rotation_euler=direction.to_track_quat('Z','Y').to_euler()
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    return obj


def boolean(target,other,operation):
    bpy.context.view_layer.objects.active=target
    modifier=target.modifiers.new('Exterior construction '+operation,'BOOLEAN');modifier.operation=operation;modifier.solver='EXACT';modifier.object=other
    bpy.ops.object.modifier_apply(modifier=modifier.name);bpy.data.objects.remove(other,do_unlink=True)


def rounded(obj,width):
    bpy.context.view_layer.objects.active=obj
    bevel=obj.modifiers.new('Bounded small edge radii','BEVEL');bevel.width=width;bevel.segments=5;bevel.limit_method='ANGLE';bevel.angle_limit=math.radians(35)
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    # Exact boolean/bevel intersections can leave nanometre slivers. Clean in the native
    # surface before calculating normals; the subsequent closed/area/volume check remains strict.
    bm=bmesh.new();bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free();obj.data.update()
    for face in obj.data.polygons:face.use_smooth=True
    obj.data.set_sharp_from_angle(angle=math.radians(35))
    if 'casting' not in obj.name:
        weighted=obj.modifiers.new('Native weighted corner normals','WEIGHTED_NORMAL');weighted.keep_sharp=True;weighted.weight=50
        bpy.ops.object.modifier_apply(modifier=weighted.name)



if not args.finish:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    body=cylinder('Observed casting and selector exterior',0,-.040,.009,.011,(0,-.022,0))
    selector=cylinder('Observed transverse selector boss',1,-.025,-.002,.010,(-.006,0,0))
    boolean(body,selector,'UNION')
    outlet=cylinder('Observed outlet neck',2,.005,.021,.0045,(-.029,-.027,0))
    boolean(body,outlet,'UNION')
    bore=cylinder('Visible outlet mouth only, blind review end',2,.012,.025,.0028,(-.029,-.027,0))
    boolean(body,bore,'DIFFERENCE');rounded(body,.0003);parts.append(body)
    cap=cylinder('Observed terminal six-flat exterior, related photo',0,-.0562,-.0402,.0115,(0,-.022,0),6);rounded(cap,.00035);parts.append(cap)
    mount=cylinder('Observed filter-side six-flat mounting exterior',0,.0092,.0252,.015,(0,-.022,0),6);rounded(mount,.00035);parts.append(mount)
    gray=bpy.data.materials.new('Neutral form review');gray.diffuse_color=(.2,.2,.2,1);gray.use_nodes=True
    gray.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.2,.2,.2,1)
    gray.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.45
    rows=[]
    for obj in parts:
        mesh=bmesh.new();mesh.from_mesh(obj.data);bmesh.ops.triangulate(mesh,faces=list(mesh.faces))
        closed=all(len(e.link_faces)==2 for e in mesh.edges);area=min(f.calc_area() for f in mesh.faces);volume=mesh.calc_volume(signed=True)
        if not closed or area<=1e-15 or volume<=0:raise ValueError((obj.name,closed,area,volume))
        rows.append({'object':obj.name,'triangles':len(mesh.faces),'closed':closed,'minimum_triangle_area_m2':area,'signed_volume_m3':volume});mesh.free()
        obj.data.materials.clear();obj.data.materials.append(gray)
    (REVIEW/'source-geometry-check.json').write_text(json.dumps({'parts':rows,'all_dimensions_estimated':True,'plan':'creative/research/fuel-tap-visible-body-v1/plan.json','scope':'Exterior finite review bodies, not internal cast wall thickness or flow mechanism','art_accepted':False},indent=2)+'\n')
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    world=bpy.data.worlds.new('Neutral review world');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.13,.13,.13,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45;scene.world=world
    target=Vector((-.015,-.016,.003))
    for name,eye,power,size in [('Key',(-.15,-.12,.20),1,.15),('Fill',(.15,.1,.13),.5,.12)]:
        light=bpy.data.lights.new(name,'AREA');light.energy=power;light.shape='DISK';light.size=size;ob=bpy.data.objects.new(name,light);scene.collection.objects.link(ob);ob.location=eye;ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
    camera=bpy.data.objects.new('Whole tap review camera',bpy.data.cameras.new('Whole tap review camera'));scene.collection.objects.link(camera);scene.camera=camera;camera.data.type='ORTHO';camera.data.ortho_scale=.115;camera.data.clip_start=.001;camera.data.clip_end=10
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=16;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=960;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
    camera.location=(.09,-.10,.14);camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(FOLDER/'child-gray.blend'),compress=True)
else:
    bpy.ops.wm.open_mainfile(filepath=str(FOLDER/'child-gray.blend'));scene=bpy.context.scene;parts=[o for o in scene.objects if o.type=='MESH']
    for obj in parts:
        material=bpy.data.materials.new('Proposed clean tap metal '+obj.name);material.use_nodes=True;bs=material.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.32,.30,.23,1) if 'six-flat'in obj.name else (.34,.36,.35,1);bs.inputs['Metallic'].default_value=.8;bs.inputs['Roughness'].default_value=.32
        obj.data.materials.clear();obj.data.materials.append(material)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(FOLDER/'child-candidate.blend'),compress=True)

phase='candidate' if args.finish else 'gray'
bpy.ops.object.select_all(action='DESELECT')
for obj in parts:obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(FOLDER/f'child-{phase}.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_animations=False)
scene=bpy.context.scene;target=Vector((-.015,-.016,.003));views=[]
for name,eye in ([('front',(0,-.016,.24)),('quarter',(.09,-.10,.14)),('reverse',(-.10,.08,-.16))] if args.finish else [('gray-quarter',(.09,-.10,.14))]):
    scene.camera.location=eye;scene.camera.rotation_euler=(target-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.cycles.samples=96 if args.finish else 16
    scene.render.image_settings.file_format='OPEN_EXR_MULTILAYER';scene.render.image_settings.color_depth='32';scene.render.filepath=str(REVIEW/'raw'/f'{name}.exr');bpy.ops.render.render(write_still=True)
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(REVIEW/f'{name}.png'),scene=scene)
    views.append({'view':name,'samples':scene.cycles.samples,'denoised':False,'png_sha256':sha(REVIEW/f'{name}.png'),'exr_sha256':sha(REVIEW/'raw'/f'{name}.exr')})
(REVIEW/f'{phase}-render-report.json').write_text(json.dumps({'phase':phase,'source_sha256':sha(FOLDER/f'child-{phase}.blend'),'export_sha256':sha(FOLDER/f'child-{phase}.glb'),'builder_sha256':sha(Path(__file__)),'views':views,'art_accepted':False},indent=2)+'\n')
