"""Build in an unfrozen copy only; no mutation of closed candidate sources."""
from pathlib import Path
import subprocess
H=Path(__file__).resolve().parent;R=H.parents[2];assert not(H/'preflight-manifest.json').exists();B='/workspace/wewa-tools/blender-4.3.2-linux-x64/blender'
def py(name):subprocess.run([B,'--background','--threads','1','--python-exit-code','1','--python',str(H/name)],cwd=R,check=True)
def node(name):subprocess.run(['node',str(H/name)],cwd=R,check=True)
py('build.py');node('check_export.mjs');node('check_uv_material.mjs')
for name in ['check_self_surface.py','check_interface.py','check_reference_paths.py']:py(name)
