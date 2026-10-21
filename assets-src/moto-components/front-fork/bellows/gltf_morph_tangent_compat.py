"""Asset-local compatibility fix for Blender 4.3.2 morph tangent transport.

Derived from io_scene_gltf2 PrimitiveCreator.__calc_morph_tangents:
SPDX-FileCopyrightText: 2018-2021 The glTF-Blender-IO authors
SPDX-License-Identifier: Apache-2.0
Modification 2026: transport actively from base normal to target normal.
See LICENSE-gltf-morph-tangent.txt. No installed file or GLB buffer is edited.
This preserves native normal-based transport; it does NOT recalculate MikkTSpace
for each target, and interpolated weights must be checked independently.
"""
from contextlib import contextmanager
import hashlib
import inspect
import json
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector
from io_scene_gltf2.blender.exp import primitive_extract

EXPECTED_MODULE_SHA256 = 'af539328c81432c23213e5c1d300b0b1646b528c3b419a5b18bfaa21597ad9ae'
METHOD = '_PrimitiveCreator__calc_morph_tangents'


@contextmanager
def corrected_morph_tangent_export(report_path):
    """Temporarily replace the guarded native routine only in this process."""
    assert bpy.app.version[:3] == (4, 3, 2), 'Re-audit compatibility for another Blender version'
    cls = primitive_extract.PrimitiveCreator
    original = getattr(cls, METHOD)
    module_path = Path(inspect.getsourcefile(cls)).resolve()
    initial_sha = hashlib.sha256(module_path.read_bytes()).hexdigest()
    assert initial_sha == EXPECTED_MODULE_SHA256, 'Installed exporter differs: do not patch blindly'
    assert 'rotation = morph_n.rotation_difference(n)' in inspect.getsource(original)
    rows = []

    def calc_morph_tangents(self):
        self.morph_tangents = np.empty((len(self.normals), 3), dtype=np.float32)
        before, after = 0.0, 0.0
        for i in range(len(self.normals)):
            n = Vector(self.normals[i])
            morph_n = n + Vector(self.morph_normals[i])
            t = Vector(self.tangents[i, :3])
            # Active rotation: base normal -> target normal. Native reverses it.
            rotation = n.rotation_difference(morph_n)
            t_morph = Vector(t)
            t_morph.rotate(rotation)
            self.morph_tangents[i] = t_morph - t
            before = max(before, abs(n.normalized().dot(t.normalized())))
            after = max(after, abs(morph_n.normalized().dot(t_morph.normalized())))
        rows.append({'vertices': len(self.normals), 'base_max_abs_normal_dot_tangent': before,
                     'target_max_abs_normal_dot_transported_tangent': after})

    setattr(cls, METHOD, calc_morph_tangents)
    completed = False
    try:
        yield
        completed = True
    finally:
        setattr(cls, METHOD, original)
        final_sha = hashlib.sha256(module_path.read_bytes()).hexdigest()
        restored = getattr(cls, METHOD) is original
        assert final_sha == initial_sha and restored
        report = {'installed_module': str(module_path), 'installed_module_sha256_before': initial_sha,
                  'installed_module_sha256_after': final_sha, 'installed_file_unchanged': True,
                  'native_method_restored': restored, 'export_completed': completed,
                  'routine': METHOD, 'correction': 'n.rotation_difference(morph_n)',
                  'scope': 'temporary asset export process only; no GLB buffer editing',
                  'base_tangent_w_preserved': True, 'UV_and_geometry_untouched': True,
                  'not_recomputed_Mikk_per_target': True, 'calls': rows,
                  'helper_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        Path(report_path).write_text(json.dumps(report, indent=2) + '\n')
