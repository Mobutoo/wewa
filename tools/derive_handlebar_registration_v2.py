"""Derive GLB registration candidates without re-encoding any geometry or texture.

Only eight node translations change. All binary chunks, materials, hierarchy,
normals, UVs and quantization transforms retain their original values.
"""
import copy
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets-src/moto-components/handlebar-registration-v2'
REVIEW = ROOT / 'creative/reviews/handlebar-registration-v2'
PLAN = ROOT / 'creative/research/handlebar-registration-v2/plan.json'
JSON_CHUNK = 0x4E4F534A
BIN_CHUNK = 0x004E4942
NAMES = {f'Handlebar clamp {side} {part}' for side in ['L', 'R']
         for part in ['upper', 'lower', 'bolt 1', 'bolt 2']}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def decode(raw):
    if len(raw) < 20 or struct.unpack_from('<4sII', raw) != (b'glTF', 2, len(raw)):
        raise ValueError('Invalid GLB header or length')
    chunks = []
    offset = 12
    while offset < len(raw):
        if offset + 8 > len(raw):
            raise ValueError('Truncated chunk header')
        length, kind = struct.unpack_from('<II', raw, offset)
        offset += 8
        if length % 4 or offset + length > len(raw):
            raise ValueError('Invalid chunk size')
        chunks.append((kind, raw[offset:offset + length]))
        offset += length
    if [kind for kind, _ in chunks] != [JSON_CHUNK, BIN_CHUNK]:
        raise ValueError('Expected exactly one JSON and one BIN chunk')
    return json.loads(chunks[0][1]), chunks[1][1]


def encode(document, binary):
    data = json.dumps(document, separators=(',', ':'), ensure_ascii=False).encode()
    data += b' ' * (-len(data) % 4)
    return (struct.pack('<4sII', b'glTF', 2, 28 + len(data) + len(binary))
            + struct.pack('<II', len(data), JSON_CHUNK) + data
            + struct.pack('<II', len(binary), BIN_CHUNK) + binary)


def derive(raw, shift, full_assembly=False):
    if not 0 < shift < .01:
        raise ValueError('Unexpected registration distance')
    document, binary = decode(raw)
    if document.get('animations') or document.get('skins'):
        raise ValueError('Static registration cannot modify animated or skinned assets')
    result = copy.deepcopy(document)
    nodes = result['nodes']
    if full_assembly:
        parents = [n for n in nodes if n.get('name') == 'PARENT [clamps]']
        if len(parents) != 1:
            raise ValueError('Missing or duplicated clamp parent')
        parent = parents[0]
        if any(k in parent for k in ['matrix', 'rotation', 'scale']):
            raise ValueError('Unexpected clamp parent transform')
        indexes = parent['children']
    else:
        indexes = result['scenes'][result.get('scene', 0)]['nodes']
    if len(indexes) != 8 or {nodes[i].get('name') for i in indexes} != NAMES:
        raise ValueError('Expected exactly eight independently placed clamp parts')
    changes = []
    for i in indexes:
        node = nodes[i]
        if 'matrix' in node or 'mesh' not in node or node.get('children'):
            raise ValueError('Unexpected clamp hierarchy or matrix')
        before = node['translation'][:]
        side = 1 if ' clamp L ' in node['name'] else -1
        if abs(before[0] - side * .045) > .0001:
            raise ValueError('Input is not the original 45 mm registration')
        node['translation'][0] -= side * shift
        changes.append({'name': node['name'], 'node': i, 'before': before,
                        'after': node['translation'][:]})
    output = encode(result, binary)
    actual, actual_binary = decode(output)
    for change in changes:
        actual['nodes'][change['node']]['translation'] = change['before']
    if actual != document or actual_binary != binary:
        raise AssertionError('Unexpected geometry, texture, material or hierarchy change')
    return output, {'changes': changes, 'binary_sha256': sha(binary),
                    'binary_payload_unchanged': True, 'only_eight_translations_changed': True}


def main():
    plan = json.loads(PLAN.read_text())
    native = json.loads((REVIEW / 'native-check.json').read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    sources = [(plan['source_glb'], 'clamps.glb', False),
               ('assets-src/moto-components/motorcycle-exterior-v5/lod/motorcycle-lod.glb',
                'motorcycle-registration-candidate.glb', True)]
    lod_report = json.loads((ROOT / 'assets-src/moto-components/motorcycle-exterior-v5/lod/build-report.json').read_text())
    for source, name, full in sources:
        raw = (ROOT / source).read_bytes()
        if full:
            assert sha(raw) == lod_report['output_sha256'], 'Base LOD differs from frozen delivery'
        output, checks = derive(raw, plan['translation_per_side_m'], full)
        for change in checks['changes']:
            expected = next(r for r in native['changes'] if r['name'] == change['name'])
            assert abs((change['after'][0] - change['before'][0])
                       - (expected['after_m'][0] - expected['before_m'][0])) < 1e-7
        file = OUT / name
        file.write_bytes(output)
        rows.append({'input': source, 'input_sha256': sha(raw),
                     'output': str(file.relative_to(ROOT)), 'output_sha256': sha(output),
                     'output_bytes': len(output), **checks})
        assert sha((ROOT / source).read_bytes()) == sha(raw)
    report = {'schema': 1, 'plan_sha256': sha(PLAN.read_bytes()),
              'tool_sha256': sha(Path(__file__).read_bytes()), 'files': rows,
              'art_accepted': False, 'game_integrated': False}
    (REVIEW / 'derivation-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print('REGISTRATION_EXPORTS', len(rows))


if __name__ == '__main__':
    main()
