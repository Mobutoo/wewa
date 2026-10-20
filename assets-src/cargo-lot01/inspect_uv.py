import bpy
import math
import json
import sys
from pathlib import Path

out = Path('/workspace/wewa-assets/cargo-lot01')
source = Path(__file__).resolve().parent
if '--pack' in sys.argv:
    for image in bpy.data.images:
        if image.name not in ['Render Result','Viewer Node'] and image.source in ['FILE','GENERATED']:
            image.pack()
    bpy.context.scene['attachment_blender_xyz']=[0,.67,.83]
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
rows = []
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    uv = obj.data.uv_layers.active
    invalid = 0
    zero_area = 0
    obj.data.calc_loop_triangles()
    if uv:
        for item in uv.data:
            if not all(math.isfinite(v) for v in item.uv):
                invalid += 1
        for tri in obj.data.loop_triangles:
            a,b,c = [uv.data[i].uv for i in tri.loops]
            cross = (b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x)
            if abs(cross) < 1e-12:
                zero_area += 1
    rows.append({'object':obj.name,'uv_layer':uv.name if uv else None,
                 'invalid_uv_values':invalid,'zero_area_uv_triangles':zero_area,
                 'triangles':len(obj.data.loop_triangles),
                 'has_texture':obj.name in ['cargo_kraft','cargo_tape','cargo_rope']})
images = [{'name':i.name,'dimensions':list(i.size),'packed':bool(i.packed_file),
           'colorspace':i.colorspace_settings.name} for i in bpy.data.images
          if i.name not in ['Render Result','Viewer Node']]
report={'scope':'Source Blender UV/packing inspection, not artistic approval',
        'meshes':rows,'source_images':images,
        'note':'Zero-area UV on narrow bevel/solidify rim faces is reported; untextured ink/paper does not require a texture atlas.'}
(out/'uv-inspection.json').write_text(json.dumps(report,indent=2)+'\n')
(source/'uv-inspection.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
