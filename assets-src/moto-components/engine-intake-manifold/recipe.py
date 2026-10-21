"""Rebuild this unfrozen candidate in three explicit stages, never overwrite a gel."""
from pathlib import Path
import subprocess
H=Path(__file__).resolve().parent
assert not (H/'preflight-manifest.json').exists(), 'Frozen candidate: use a separate revision'
B='/workspace/wewa-tools/blender-4.3.2-linux-x64/blender'
for script in ['build.py','topology_stage.py','material.py']:
    subprocess.run([B,'--background','--threads','1','--python-exit-code','1','--python',str(H/script)],check=True)
