"""Change the actual model plate to two editable text lines; preserve motorcycle geometry."""
import bpy
import math
import json
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets-src/moto-components/seat-plate-v2'
REVIEW=ROOT/'creative/reviews/seat-plate-v2'
SOURCE=ROOT/'assets-src/moto-components/under-tank-completion-v1/motorcycle-completed-context.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene
plate_parent=bpy.data.objects['PARENT [license-plate-wewa-v2]']
plate=next(o for o in plate_parent.children_recursive if o.type=='MESH')
front=next(m for m in plate.data.materials if m.name=='Original fictitious WEWA game plate front')
nodes=front.node_tree.nodes
bsdf=nodes.get('Principled BSDF')
for link in list(bsdf.inputs['Base Color'].links):front.node_tree.links.remove(link)
bsdf.inputs['Base Color'].default_value=(.855,.863,.807,1)
front.name='Art. 015 plate front - warm white'
ink=bpy.data.materials.new('Art. 015 black lettering');ink.use_nodes=True
shader=ink.node_tree.nodes.get('Principled BSDF')
shader.inputs['Base Color'].default_value=(.006,.007,.008,1)
shader.inputs['Roughness'].default_value=.49
parent=bpy.data.objects.new('REVISION [plate-Art-015]',None);scene.collection.objects.link(parent)
font=bpy.data.fonts.load(str(OUT/'DejaVuSans-Bold.ttf'))
created=[];lines=[]
for body,z,height in [('Art.',-.454,.030),('015',-.497,.036)]:
    c=bpy.data.curves.new('Editable plate line '+body,'FONT');c.body=body
    c.font=font;c.align_x='CENTER';c.align_y='CENTER';c.size=.05
    c.extrude=.000035;c.resolution_u=12
    o=bpy.data.objects.new('Plate text '+body,c);scene.collection.objects.link(o)
    o.parent=parent;o.rotation_euler=(math.pi/2,0,math.pi);o.location=(0,1.2109,z)
    c.materials.append(ink);bpy.context.view_layer.update()
    scale=height/o.dimensions.y;o.scale=(scale,scale,scale);bpy.context.view_layer.update()
    assert o.dimensions.x<.145
    created.append(o);lines.append({'text':body,'height_m':o.dimensions.y,'width_m':o.dimensions.x,'centre_blender_m':list(o.location)})
# Thin rounded black border on the existing plate; no raster decal or photo retouch.
c=bpy.data.curves.new('Plate border curve','CURVE');c.dimensions='3D';c.bevel_depth=.00042;c.bevel_resolution=3
s=c.splines.new('POLY');coords=[]
for cx,cz,start in [(.078,-.438,0),(-.078,-.438,90),(-.078,-.516,180),(.078,-.516,270)]:
    for i in range(13):
        a=math.radians(start+i*90/12);coords.append((cx+.005*math.cos(a),1.21094,cz+.005*math.sin(a),1))
s.points.add(len(coords)-1)
for v,co in zip(s.points,coords):v.co=co
s.use_cyclic_u=True
o=bpy.data.objects.new('Art. 015 rounded border',c);scene.collection.objects.link(o);o.parent=parent;c.materials.append(ink);created.append(o)
bpy.ops.file.pack_all();bpy.context.preferences.filepaths.save_version=0
scene['revision']='seat-plate-v2';scene['plate_text']='Art.\n015';scene['art_accepted']=False
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'motorcycle-Art-015.blend'),compress=True)
bpy.ops.object.select_all(action='DESELECT');parent.select_set(True)
for o in created:o.select_set(True)
bpy.context.view_layer.objects.active=created[0]
bpy.ops.export_scene.gltf(filepath=str(OUT/'plate-lettering.glb'),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False)
(REVIEW/'plate-build.json').write_text(json.dumps({'text_lines':lines,'plate_dimensions_m':[.18,.105,.0015],
    'method':'Editable Blender text with bundled licensed DejaVu font; original plate mesh and holes unchanged.',
    'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'art_accepted':False},indent=2)+'\n')
print('ART015_PLATE_BUILT',lines)
