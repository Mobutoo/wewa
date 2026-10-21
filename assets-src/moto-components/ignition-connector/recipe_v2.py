"""Explicit additive recipe; frozen stages are read-only by default."""
from pathlib import Path
import subprocess,sys,json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];B='/workspace/wewa-tools/blender-4.3.2-linux-x64/blender'
stage=sys.argv[1]if len(sys.argv)>1 else'verify'
def py(name,*args):subprocess.run([B,'--background','--threads','1','--python-exit-code','1','--python',str(H/name),*args],cwd=R,check=True)
def node(name):subprocess.run(['node',str(H/name)],cwd=R,check=True)
if stage=='geometry':
    assert not(H/'preflight-manifest-v2.json').exists();py('build_v2.py');node('check_geometry_export_v2.mjs');py('check_pose_containment_v2.py')
elif stage=='material':
    assert not(H/'preflight-manifest-v2.json').exists();py('material_v2.py');py('check_source_material_v2.py');node('check_export_v2.mjs');node('check_material_export_v2.mjs')
elif stage=='verify':
    M=json.loads((H/'preflight-manifest-v2.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    for row in M['files']:
        p=R/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],row['path']
    print('CONNECTOR_V2_FROZEN_INPUTS_VERIFIED',len(M['files']))
else:raise ValueError('geometry, material, or verify; no source mutation after freeze')
