"""Structural checks on the uncompressed GLBs produced by prepare_pilot.py.
Not a replacement for Khronos Validator or an actual engine import.
"""
import json,struct,math,argparse
from pathlib import Path
def check(path):
    b=path.read_bytes();magic,ver,length=struct.unpack_from('<4sII',b)
    assert (magic,ver,length)==(b'glTF',2,len(b)),path
    n,kind=struct.unpack_from('<I4s',b,12);assert kind==b'JSON'
    d=json.loads(b[20:20+n]);offset=20+n;bn,bkind=struct.unpack_from('<I4s',b,offset);assert bkind==b'BIN\0'
    blob=b[offset+8:offset+8+bn];assert len(blob)==bn and d['buffers'][0]['byteLength']<=bn
    for v in d['bufferViews']:assert v.get('byteOffset',0)+v['byteLength']<=len(blob)
    a=d['accessors'][0];na=d['accessors'][1];assert a['count']==na['count'] and a['count']%3==0
    v=d['bufferViews'][a['bufferView']];positions=struct.unpack_from('<'+'f'*(a['count']*3),blob,v.get('byteOffset',0))
    v=d['bufferViews'][na['bufferView']];normals=struct.unpack_from('<'+'f'*(na['count']*3),blob,v.get('byteOffset',0))
    assert all(math.isfinite(x) for x in positions+normals)
    for k in range(0,len(normals),3):assert abs(sum(x*x for x in normals[k:k+3])-1)<1e-4
    for j in range(3):
        lo,hi=min(positions[j::3]),max(positions[j::3]);assert abs(lo-a['min'][j])<.001 and abs(hi-a['max'][j])<.001
    return a['count']//3
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder');p.add_argument('--out',required=True);a=p.parse_args()
    files=sorted(Path(a.folder).rglob('*.glb'));assert files,'No models'
    result={'status':'passed_structural_checks_only','files':len(files),'triangles':sum(check(f) for f in files),'engine_import':'not_tested','fps':'not_measured'}
    Path(a.out).write_text(json.dumps(result,indent=2));print(json.dumps(result))
