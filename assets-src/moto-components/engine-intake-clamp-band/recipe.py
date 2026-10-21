"""Staged portable recipe; actual gray/reflection and PBR reviews remain separate gates."""
from pathlib import Path
import subprocess,sys
H=Path(__file__).resolve().parent;R=H.parents[2];B='/workspace/wewa-tools/blender-4.3.2-linux-x64/blender';assert not(H/'preflight-manifest.json').exists();stage=sys.argv[1]if len(sys.argv)>1 else'geometry'
def py(n,*args):subprocess.run([B,'--background','--threads','1','--python-exit-code','1','--python',str(H/n),*(['--',*args]if args else[])],cwd=R,check=True)
def node(n):subprocess.run(['node',str(H/n)],cwd=R,check=True)
if stage=='geometry':py('build.py');node('check_geometry_export.mjs');py('check_self_surface.py');py('check_openings.py');py('check_return_continuity.py');py('render_geometry.py','--preflight-only')
elif stage=='material':py('material_atlas.py');node('check_atlas_export.mjs');subprocess.run([sys.executable,str(H/'generate_original_color.py')],cwd=R,check=True);py('material.py');node('check_export.mjs');node('check_protected_export.mjs');subprocess.run([sys.executable,str(H/'check_exported_color_pixels.py')],cwd=R,check=True);py('check_self_surface.py','--final');py('check_openings.py','--final');py('check_reference_paths.py');py('render.py','--preflight-only')
else:raise ValueError('Choose geometry or material; actual image reviews are required between stages')
