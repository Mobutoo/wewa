"""Append lettering to the existing GLB; one plate material is the only original change."""
import copy
import json
import hashlib
from pathlib import Path
from derive_handlebar_registration_v2 import decode,encode

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets-src/moto-components/seat-plate-v2'
source=ROOT/'assets-src/moto-components/under-tank-completion-v1/motorcycle-completed-candidate.glb'
base,bb=decode(source.read_bytes());add,ab=decode((OUT/'plate-lettering.glb').read_bytes())
assert not any(add.get(k) for k in ['textures','images','animations','skins'])
result=copy.deepcopy(base)
tables=['nodes','meshes','materials','accessors','bufferViews']
offsets={t:len(base[t]) for t in tables}
for node in add['nodes']:
    if 'mesh' in node:node['mesh']+=offsets['meshes']
    if 'children' in node:node['children']=[i+offsets['nodes'] for i in node['children']]
for mesh in add['meshes']:
    for p in mesh['primitives']:
        p['attributes']={k:v+offsets['accessors'] for k,v in p['attributes'].items()}
        p['indices']+=offsets['accessors'];p['material']+=offsets['materials']
for a in add['accessors']:a['bufferView']+=offsets['bufferViews']
for v in add['bufferViews']:v['byteOffset']=v.get('byteOffset',0)+len(bb)
for t in tables:result[t].extend(add[t])
result['buffers']=[{'byteLength':len(bb)+len(ab)}]
result['scenes'][0]['nodes'] += [i+offsets['nodes'] for i in add['scenes'][0]['nodes']]
mat_id=next(i for i,m in enumerate(result['materials']) if m.get('name')=='Original fictitious WEWA game plate front')
result['materials'][mat_id]['name']='Art. 015 plate front - warm white'
pbr=result['materials'][mat_id]['pbrMetallicRoughness'];pbr.pop('baseColorTexture');pbr['baseColorFactor']=[.855,.863,.807,1]
target=OUT/'motorcycle-Art-015.glb';target.write_bytes(encode(result,bb+ab))
actual,binary=decode(target.read_bytes())
assert binary==bb+ab
for t in tables+['images','textures','samplers']:
    old=copy.deepcopy(actual[t][:len(base[t])])
    if t=='materials':old[mat_id]=base[t][mat_id]
    assert old==base[t],t
report={'source':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'output':str(target.relative_to(ROOT)),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
        'original_binary_preserved':True,'original_geometry_and_poses_unchanged':True,
        'changed_original_material':mat_id,'text_lines':['Art.','015'],'new_nodes':len(add['nodes']),
        'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(ROOT/'creative/reviews/seat-plate-v2/composition-check.json').write_text(json.dumps(report,indent=2)+'\n')
print('ART015_COMPOSED',target.stat().st_size)
