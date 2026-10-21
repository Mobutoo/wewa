"""Staged short sheath recipe; actual G3/G4 preview reads required before freezing."""
from pathlib import Path
import subprocess,sys
H=Path(__file__).resolve().parent;R=H.parents[2];B='/workspace/wewa-tools/blender-4.3.2-linux-x64/blender';assert not(H/'preflight-manifest.json').exists();stage=sys.argv[1]if len(sys.argv)>1 else'geometry'
def py(n,*args):subprocess.run([B,'--background','--threads','1','--python-exit-code','1','--python',str(H/n),*(['--',*args]if args else[])],cwd=R,check=True)
def node(n):subprocess.run(['node',str(H/n)],cwd=R,check=True)
if stage=='geometry':py('build.py');node('check_geometry_export.mjs');py('check_self_surface.py');py('check_interface.py');py('render_geometry.py','--preflight-only')
elif stage=='material':py('material.py');node('check_export.mjs');node('check_protected_export.mjs');py('check_current_source_geometry.py');py('check_interface.py','--final');py('check_reference_paths.py');py('render.py','--preflight-only')
else:raise ValueError('Choose geometry or material; actual reviewed previews required between stages')
