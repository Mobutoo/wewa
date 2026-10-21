"""Geometry -> explicit preserved stage -> local topology -> baked native PBR.

Run only in an isolated unmanifested working copy. Review checks and human
readings are separate steps; rebuilding never inherits an old reception.
"""
from pathlib import Path
import subprocess,shutil
H=Path(__file__).resolve().parent
assert not (H/'preflight-manifest-v2.json').exists(),'Frozen revision: rebuild in a new isolated revision, never overwrite the manifest witness.'
B='/workspace/wewa-tools/blender-4.3.2-linux-x64/blender'
for name in ['build_v2.py','topology_stage_v2.py','material_v2.py']:
    subprocess.run([B,'--background','--threads','1','--python-exit-code','1','--python',str(H/name)],check=True)
    if name=='build_v2.py':shutil.copy2(H/'engine-spark-cap-v2.blend',H/'engine-spark-cap-v2-geometry.blend')
