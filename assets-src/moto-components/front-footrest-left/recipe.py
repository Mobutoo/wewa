"""Staged editable recipe. New sources require their own actual preview review before material."""
from pathlib import Path
import subprocess,sys,json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];assert not(H/'preflight-manifest.json').exists();B='/workspace/wewa-tools/blender-4.3.2-linux-x64/blender';stage=sys.argv[1]if len(sys.argv)>1 else'geometry'
def py(n,*args):subprocess.run([B,'--background','--threads','1','--python-exit-code','1','--python',str(H/n),*(['--',*args]if args else[])],cwd=R,check=True)
def node(n):subprocess.run(['node',str(H/n)],cwd=R,check=True)
if stage=='geometry':
 py('build.py');node('check_geometry_export.mjs');py('check_self_surface.py');py('check_openings.py');py('render_geometry.py','--preflight-only')
elif stage=='material':
 source=H/'front-footrest-left-v1-geometry.blend';review=json.loads((R/'creative/reviews/front-footrest-left-v1/geometry-preview-review.json').read_text());assert review['source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest() and review['ready_for_representative_material'];subprocess.run([sys.executable,str(H/'generate_original_maps.py')],cwd=R,check=True);py('material.py');node('check_export.mjs');node('check_protected_export.mjs');node('check_material_export.mjs');subprocess.run([sys.executable,str(H/'check_exported_map_pixels.py')],cwd=R,check=True)
else:raise ValueError('Use geometry or material; actual review is a separate required step')
