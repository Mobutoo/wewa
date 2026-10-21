"""Unfrozen working-copy recipe, no rebuilding over a closed source."""
from pathlib import Path
import subprocess,sys
H=Path(__file__).resolve().parent;R=H.parents[2];assert not(H/'preflight-manifest.json').exists();B='/workspace/wewa-tools/blender-4.3.2-linux-x64/blender'
def py(name):subprocess.run([B,'--background','--threads','1','--python-exit-code','1','--python',str(H/name)],cwd=R,check=True)
def node(name):subprocess.run(['node',str(H/name)],cwd=R,check=True)
py('build.py');node('check_geometry_export.mjs');py('material.py');node('check_export.mjs');node('check_protected_export.mjs');node('check_material_export.mjs');subprocess.run([sys.executable,str(H/'check_exported_map_pixels.py')],cwd=R,check=True)
for name in ['check_self_surface.py','check_openings.py','check_mounting_scope.py','check_reference_paths.py']:py(name)
