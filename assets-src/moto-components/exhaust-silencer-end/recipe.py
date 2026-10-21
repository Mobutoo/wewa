"""Rebuild only in an unfrozen working copy; never overwrite a closed source."""
from pathlib import Path
import subprocess,sys
H=Path(__file__).resolve().parent;R=H.parents[2];assert not(H/'preflight-manifest.json').exists(),'Copy to a new revision before rebuilding a frozen asset'
blender=Path('/workspace/wewa-tools/blender-4.3.2-linux-x64/blender')
def py(n):subprocess.run([str(blender),'--background','--threads','1','--python-exit-code','1','--python',str(H/n)],cwd=R,check=True)
def node(n):subprocess.run(['node',str(H/n)],cwd=R,check=True)
py('build.py');node('check_geometry_export.mjs');py('material.py');node('check_export.mjs');node('check_protected_export.mjs');node('check_material_export.mjs');subprocess.run([sys.executable,str(H/'check_exported_map_pixels.py')],cwd=R,check=True)
for n in ['check_self_surface.py','check_openings.py','check_interface.py','check_reference_paths.py']:py(n)
