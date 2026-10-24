"""Verify committed source, export, reference records and rendered evidence."""
import argparse
import hashlib
import json
from pathlib import Path
from derive_handlebar_registration_v2 import decode

ROOT=Path(__file__).resolve().parents[1]
REVIEW=ROOT/'creative/reviews/under-tank-completion-v1'
MANIFEST=REVIEW/'production-manifest.json'


def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    paths=[]
    for folder in ['creative/research/under-tank-completion-v1','creative/reviews/under-tank-completion-v1',
                   'assets-src/moto-components/under-tank-completion-v1','tools/under-tank-review-v1']:
        paths.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and p!=MANIFEST)
    paths.extend((ROOT/'tools').glob('*under_tank*.*'))
    paths.extend((ROOT/'creative/workflow/records').glob('moto-under-tank-*.json'))
    paths=sorted(set(paths))
    if args.write:
        MANIFEST.write_text(json.dumps({'revision':'under-tank-completion-v1','files':[
            {'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths]},indent=2)+'\n')
    manifest=json.loads(MANIFEST.read_text())
    assert {r['path'] for r in manifest['files']}=={str(p.relative_to(ROOT)) for p in paths}
    for row in manifest['files']:
        p=ROOT/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],row['path']
    plan=json.loads((ROOT/'creative/research/under-tank-completion-v1/plan.json').read_text())
    assert sha(ROOT/plan['input'])==plan['input_sha256']
    base,bb=decode((ROOT/plan['input']).read_bytes())
    candidate,cb=decode((ROOT/'assets-src/moto-components/under-tank-completion-v1/motorcycle-completed-candidate.glb').read_bytes())
    additions,ab=decode((ROOT/'assets-src/moto-components/under-tank-completion-v1/additions.glb').read_bytes())
    assert cb==bb+ab
    for t in ['nodes','meshes','materials','accessors','bufferViews','images','textures','samplers']:
        assert candidate[t][:len(base[t])]==base[t],t
    assert len(candidate['scenes'][0]['nodes'])==183
    native=json.loads((REVIEW/'native-check.json').read_text())
    assert len(native['mesh_checks'])==75
    assert all(r['non_manifold_edges']==0 and r['volume_m3']>0 for r in native['mesh_checks'])
    exported=json.loads((REVIEW/'export-check.json').read_text())
    assert exported['triangles']==33562
    assert all(r['issues']['numErrors']==0 for r in exported['validations'])
    browser=json.loads((REVIEW/'browser-check.json').read_text())
    assert not browser['page_errors'] and not browser['http_failures'] and browser['touch_controls_checked']
    assert len(browser['captures'])==12
    for row in browser['captures']:assert sha(ROOT/row['path'])==row['sha256']
    for i in range(0,12,2):
        a,b=browser['captures'][i:i+2]
        assert a['runtime']['camera']==b['runtime']['camera']
        assert a['sha256']!=b['sha256']
    assert browser['captures'][1]['runtime']['visible_triangles']==973765
    print(json.dumps({'valid':True,'files':len(paths),'new_closed_meshes':75,'active_groups':183,
                      'new_triangles':33562,'whole_triangles':973765,'paired_captures':12,
                      'art_accepted':False},indent=2))


if __name__=='__main__':main()
