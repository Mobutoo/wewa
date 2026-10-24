"""Append new meshes without recompressing any original geometry or texture."""
import copy
import hashlib
import json
from pathlib import Path
from derive_handlebar_registration_v2 import decode, encode

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT/'creative/research/under-tank-completion-v1/plan.json'
OUT = ROOT/'assets-src/moto-components/under-tank-completion-v1'
REVIEW = ROOT/'creative/reviews/under-tank-completion-v1'


def compose():
    plan=json.loads(PLAN.read_text())
    raw=(ROOT/plan['input']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==plan['input_sha256']
    base, bb=decode(raw); add, ab=decode((OUT/'additions.glb').read_bytes())
    assert not any(add.get(k) for k in ['skins','animations','textures','images','cameras'])
    assert set(add.get('extensionsUsed',[])) <= {'KHR_materials_ior','KHR_materials_specular'}, add.get('extensionsUsed')
    result=copy.deepcopy(base)
    tables=['nodes','meshes','materials','accessors','bufferViews']
    offsets={t:len(base.get(t,[])) for t in tables}
    for node in add['nodes']:
        if 'mesh' in node: node['mesh']+=offsets['meshes']
        if 'children' in node:node['children']=[i+offsets['nodes'] for i in node['children']]
    for mesh in add['meshes']:
        for p in mesh['primitives']:
            assert not p.get('targets') and not p.get('extensions')
            p['attributes']={k:v+offsets['accessors'] for k,v in p['attributes'].items()}
            p['indices']+=offsets['accessors'];p['material']+=offsets['materials']
    for a in add['accessors']:
        assert 'sparse' not in a
        a['bufferView']+=offsets['bufferViews']
    for v in add['bufferViews']:
        assert v['buffer']==0
        v['byteOffset']=v.get('byteOffset',0)+len(bb)
    for t in tables:result.setdefault(t,[]).extend(add[t])
    result['buffers']=[{'byteLength':len(bb)+len(ab)}]
    scene=result['scenes'][result.get('scene',0)]
    replaced=[i for i in scene['nodes'] if result['nodes'][i].get('name') in
              {'PARENT ['+k+']' for k in plan['replace_groups']}]
    assert len(replaced)==len(plan['replace_groups'])
    scene['nodes']=[i for i in scene['nodes'] if i not in replaced]
    scene['nodes'] += [i+offsets['nodes'] for i in add['scenes'][add.get('scene',0)]['nodes']]
    scene['name']='WEWA - under tank visual completion candidate'
    result.setdefault('extras',{})['under_tank_completion']={
        'revision':plan['revision'],'dimensions':'estimated from official photographs',
        'replaced_groups':plan['replace_groups'],'art_accepted':False}
    file=OUT/'motorcycle-completed-candidate.glb'
    file.write_bytes(encode(result,bb+ab))
    actual, binary=decode(file.read_bytes())
    assert binary[:len(bb)]==bb and binary[len(bb):]==ab
    assert actual['nodes'][:offsets['nodes']]==base['nodes']
    for t in tables[1:]:assert actual[t][:offsets[t]]==base[t]
    report={'input':plan['input'],'input_sha256':plan['input_sha256'],
            'output':str(file.relative_to(ROOT)),'output_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),
            'base_binary_bytes_preserved':len(bb),'base_nodes_preserved':offsets['nodes'],
            'retained_original_groups':177-len(replaced),'new_groups':10,
            'replaced_groups':plan['replace_groups'],'replaced_node_indices':replaced,
            'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'scope':'Four original groups detached from active scene only. All original buffers and node definitions retained unchanged. Standalone candidate; original file unchanged.',
            'art_accepted':False}
    (REVIEW/'composition-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print('UNDER_TANK_COMPOSE',file.stat().st_size,'bytes')


if __name__=='__main__':compose()
