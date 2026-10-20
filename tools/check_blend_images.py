"""Check that a source Blender scene carries its file textures for delivery.

blender --background source.blend --python-exit-code 1 \
    --python tools/check_blend_images.py -- report.json
This check reads the opened scene and never saves or changes it.
"""
import bpy
import json
import sys
from pathlib import Path

arguments = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
if len(arguments) != 1:
    raise ValueError('Pass one report.json path after --')
rows = []
for image in bpy.data.images:
    if image.name in ['Render Result', 'Viewer Node'] or image.source not in ['FILE', 'TILED']:
        continue
    rows.append({'name': image.name, 'size': list(image.size),
                 'packed': bool(image.packed_file), 'path': image.filepath})
report = {'source': bpy.data.filepath, 'images': rows,
          'unpacked': [row['name'] for row in rows if not row['packed']]}
Path(arguments[0]).write_text(json.dumps(report, indent=2) + '\n')
assert not report['unpacked'], report['unpacked']
