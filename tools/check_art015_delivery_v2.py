"""Check exact text, immutable original model data, delivered PNG resolution and hashes."""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from derive_handlebar_registration_v2 import decode

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'creative/reviews/seat-plate-v2'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
paths=[]
for folder in ['assets-src/moto-components/seat-plate-v2','creative/reviews/seat-plate-v2','creative/research/seat-plate-v2','tools/seat-plate-review-v2']:
    paths.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and p.name!='manifest.json' and not p.name.endswith('-preview.png'))
paths.extend((ROOT/'tools').glob('*art015*v2.*'))
record=ROOT/'creative/workflow/records/moto-license-plate-art015-002.json';paths.append(record)
if args.write:(OUT/'manifest.json').write_text(json.dumps({'files':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(set(paths))]},indent=2)+'\n')
manifest=json.loads((OUT/'manifest.json').read_text())
for row in manifest['files']:
    p=ROOT/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],row['path']
base,bb=decode((ROOT/'assets-src/moto-components/under-tank-completion-v1/motorcycle-completed-candidate.glb').read_bytes())
new,nb=decode((ROOT/'assets-src/moto-components/seat-plate-v2/motorcycle-Art-015.glb').read_bytes())
_,ab=decode((ROOT/'assets-src/moto-components/seat-plate-v2/plate-lettering.glb').read_bytes())
assert nb==bb+ab
report=json.loads((OUT/'composition-check.json').read_text());idx=report['changed_original_material']
for table in ['nodes','meshes','accessors','bufferViews','images','textures','samplers']:
    assert base[table]==new[table][:len(base[table])],table
for i,mat in enumerate(base['materials']):
    if i!=idx:assert mat==new['materials'][i]
assert 'baseColorTexture' not in new['materials'][idx]['pbrMetallicRoughness']
build=json.loads((OUT/'plate-build.json').read_text());assert [r['text'] for r in build['text_lines']]==['Art.','015']
browser=json.loads((OUT/'browser-check.json').read_text());assert not browser['page_errors'] and not browser['http_failures']
assert len(browser['captures'])==4
for row in browser['captures']:
    data=(OUT/row['file']).read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n'
    width,height=struct.unpack('>II',data[16:24]);expected=(3840,2880) if row['file'].startswith(('front','rear')) else (2560,1920)
    assert (width,height)==expected
    assert hashlib.sha256(data).hexdigest()==row['sha256']
    assert row['runtime']['textures_ready']
assert all(r['issues']['numErrors']==0 for r in json.loads((OUT/'gltf-check.json').read_text()))
print(json.dumps({'valid':True,'text_lines':['Art.','015'],'images':4,'whole_resolution':[3840,2880],'whole_motorcycle_complete':False},indent=2))
