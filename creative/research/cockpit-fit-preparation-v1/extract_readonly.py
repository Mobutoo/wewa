"""Read-only evaluated source frames/bounds; no import/export, placement, render or save."""
import bpy
import hashlib
import json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
snapshot = json.loads((HERE / 'input-snapshot.json').read_text())
rows = []
for entry in snapshot['entries']:
    source = ROOT / entry['source']
    assert sha(source) == entry['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source))
    bpy.context.view_layer.update()
    scene = bpy.context.scene
    depsgraph = bpy.context.evaluated_depsgraph_get()
    objects = list(bpy.data.collections[entry['collection']].all_objects)
    row = {'key': entry['key'], 'source': entry['source'],
           'source_sha256': sha(source), 'collection': entry['collection'],
           'scene_frame': scene.frame_current,
           'scene_scale_length': scene.unit_settings.scale_length,
           'objects': []}
    all_min, all_max = [], []
    for obj in objects:
        item = {'name': obj.name, 'type': obj.type,
                'parent': obj.parent.name if obj.parent else None,
                'hide_render': obj.hide_render,
                'matrix_world_Blender': [list(v) for v in obj.matrix_world],
                'matrix_local': [list(v) for v in obj.matrix_local],
                'matrix_parent_inverse': [list(v) for v in obj.matrix_parent_inverse],
                'has_active_action': bool(obj.animation_data and obj.animation_data.action)}
        if obj.type == 'MESH':
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            try:
                coords = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
                mesh.vertices.foreach_get('co', coords)
                coords = coords.reshape(-1, 3).astype(float)
                matrix = np.array(evaluated.matrix_world, dtype=float)
                world = coords @ matrix[:3, :3].T + matrix[:3, 3]
                low, high = world.min(0), world.max(0)
                all_min.append(low)
                all_max.append(high)
                item.update(vertices=len(coords), world_bounds_m={'min': low.tolist(), 'max': high.tolist()})
                if entry['key'] == 'cockpit-cables':
                    # Frozen generator builds each ring as48outer +48inner vertices.
                    # These are actual evaluated vertex rings, not inferred from browser matrices.
                    assert len(coords) % 96 == 0
                    item['actual_terminal_outer_ring_centres_world_m'] = [
                        world[:48].mean(0).tolist(), world[-96:-48].mean(0).tolist()]
            finally:
                evaluated.to_mesh_clear()
        row['objects'].append(item)
    row['world_bounds_m'] = {'min': np.min(all_min, axis=0).tolist(),
                             'max': np.max(all_max, axis=0).tolist()}
    assert sha(source) == entry['source_sha256']
    rows.append(row)
    print('COCKPIT_FRAME_READ', entry['key'], len(objects), flush=True)
report = {'schema': 'wewa.cockpit-fit-readonly-source-frames.v1',
          'extractor_sha256': sha(__file__),
          'input_snapshot_sha256': sha(HERE / 'input-snapshot.json'),
          'Blender_version': bpy.app.version_string, 'source_frames': rows,
          'source_saved': False, 'rendered': False, 'exported': False,
          'transforms_assigned_or_geometry_changed': False}
path = HERE / 'evaluated-source-frames.json'
assert not path.exists()
path.write_text(json.dumps(report, indent=2) + '\n')
print('COCKPIT_FRAMES_COMPLETE', len(rows), flush=True)
