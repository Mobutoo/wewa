from pathlib import Path
import subprocess,sys
H=Path(__file__).resolve().parent;R=H.parents[2];B='/workspace/wewa-tools/blender-4.3.2-linux-x64/blender';stage=sys.argv[1]if len(sys.argv)>1 else'verify'
def py(n):subprocess.run([B,'--background','--threads','1','--python-exit-code','1','--python',str(H/n)],cwd=R,check=True)
if stage=='geometry':
 assert not(H/'preflight-manifest-v3.json').exists();py('build_v3.py')
elif stage!='verify':raise ValueError('geometry or verify; rerender/rebind proof after any sourcehash change')
for n in ['check_export_v3.mjs','check_protected_export_v3.mjs','check_material_lineage_v3.mjs']:subprocess.run(['node',str(H/n)],cwd=R,check=True)
py('check_current_geometry_v3.py')
