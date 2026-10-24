"""Reopen copies outside the checkout and verify self-contained native sources."""
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'assets-src/moto-components/handlebar-registration-v2'
rows = []
with tempfile.TemporaryDirectory(prefix='wewa-registration-') as folder:
    for name in ['handlebar-registration-v2.blend', 'registration-context.blend']:
        source = FOLDER / name
        target = Path(folder) / name
        shutil.copyfile(source, target)
        bpy.ops.wm.open_mainfile(filepath=str(target))
        images = []
        for image in bpy.data.images:
            if image.source != 'FILE':
                continue
            # Blender lazily decodes packed images after opening a .blend.
            # Read a pixel before checking has_data; metadata alone is not a load.
            pixel_count = len(image.pixels)
            first_pixel = list(image.pixels[:4]) if pixel_count else []
            images.append({'name': image.name, 'packed': bool(image.packed_file),
                           'pixels_available': image.has_data and pixel_count > 0,
                           'pixel_values': pixel_count, 'first_pixel': first_pixel})
        assert not bpy.data.libraries
        assert all(image['packed'] and image['pixels_available'] for image in images), images
        rows.append({'source': str(source.relative_to(ROOT)),
                     'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                     'opened_from_unrelated_directory': True, 'linked_libraries': 0, 'images': images})
report = {'sources': rows, 'art_accepted': False,
          'tool_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(ROOT / 'creative/reviews/handlebar-registration-v2/portability-check.json').write_text(json.dumps(report, indent=2) + '\n')
print('PORTABLE_NATIVE_SOURCES', len(rows))
