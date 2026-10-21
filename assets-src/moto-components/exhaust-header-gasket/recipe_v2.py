"""Additive material2 only, never overwrite manifest1 or geometry1."""
from pathlib import Path
import subprocess,sys
H=Path(__file__).resolve().parent;R=H.parents[2];assert not(H/'preflight-manifest-v2.json').exists();B='/workspace/wewa-tools/blender-4.3.2-linux-x64/blender'
def py(n):subprocess.run([B,'--background','--threads','1','--python-exit-code','1','--python',str(H/n)],cwd=R,check=True)
def node(n):subprocess.run(['node',str(H/n)],cwd=R,check=True)
subprocess.run([sys.executable,str(H/'generate_normal_v2.py')],cwd=R,check=True);py('material_v2.py')
for n in ['check_export_v2.mjs','check_protected_export_v2.mjs','check_material_export_v2.mjs']:node(n)
subprocess.run([sys.executable,str(H/'check_exported_map_pixels_v2.py')],cwd=R,check=True)
for n in ['check_self_surface_v2.py','check_openings_v2.py','check_mounting_scope_v2.py','check_reference_paths_v2.py']:py(n)
