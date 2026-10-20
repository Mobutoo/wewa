"""Open selected downloaded sources in Blender; record actual dimensions and save an editable board.

blender --background --python tools/inspect_art_library_blender.py -- --library /workspace/wewa-asset-library
This is source inspection, not a game scene or an artistic acceptance render.
"""
import argparse
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

args_parser = argparse.ArgumentParser()
args_parser.add_argument('--library', type=Path, required=True)
args = args_parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
root = Path(__file__).resolve().parents[1]
library = args.library.resolve()
manifest = json.loads((root / 'creative/library/manifest.json').read_text())
selected = ['plastic_monobloc_chair_01', 'old_tyre', 'barrel_03', 'plastic_crate_02', 'fern_02']
bpy.ops.wm.read_factory_settings(use_empty=True)
rows = []
for index, name in enumerate(selected):
    entry = next(e for e in manifest['assets'] if e['id'] == 'ph:' + name)
    relative = next(f['path'] for f in entry['files'] if f['path'].endswith('.gltf'))
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(library / relative))
    imported = set(bpy.data.objects) - before
    meshes = [obj for obj in imported if obj.type == 'MESH']
    vertices = [obj.matrix_world @ Vector(corner) for obj in meshes for corner in obj.bound_box]
    minimum = Vector(tuple(min(v[i] for v in vertices) for i in range(3)))
    maximum = Vector(tuple(max(v[i] for v in vertices) for i in range(3)))
    triangles = 0
    for obj in meshes:
        obj.data.calc_loop_triangles()
        triangles += len(obj.data.loop_triangles)
    missing = []
    for image in bpy.data.images:
        if image.source == 'FILE' and not image.packed_file and not Path(bpy.path.abspath(image.filepath)).exists():
            missing.append(image.name)
    rows.append({'id': entry['id'], 'dimensions_m_blender_xyz_z_up': list(maximum - minimum),
                 'triangles_all_imported_meshes': triangles, 'mesh_objects': len(meshes),
                 'missing_images': missing, 'artistic_acceptance': False,
                 'note': 'Unchanged provider mesh; dimensions of the complete asset, possibly multiple variants.'})
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    for obj in imported:
        for old in list(obj.users_collection):
            old.objects.unlink(obj)
        collection.objects.link(obj)
        if obj.parent not in imported:
            obj.location.x += index * 2.5
    bpy.context.view_layer.update()
bpy.context.scene['purpose'] = 'Downloaded candidate source inspection, not Viva Wewa runtime or final art'
bpy.context.scene['source_manifest'] = 'creative/library/manifest.json'
bpy.ops.file.pack_all()
staging = library / 'blender-inspection'
staging.mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(staging / 'source-candidates.blend'))
report = {'schema': 1, 'blender_version': bpy.app.version_string,
          'source_board': 'blender-inspection/source-candidates.blend',
          'runtime_integrated': False, 'models': rows}
(root / 'creative/library/blender-inspection.json').write_text(json.dumps(report, indent=2) + '\n')
print('WEWA_SOURCE_INSPECTION ' + json.dumps(report))
