"""Bind independently checkpointed isolated views for the v3 candidate."""
from pathlib import Path
import sys,subprocess
subprocess.run([sys.executable,str(Path(__file__).resolve().parent.parent/'throttle-control/record_checkpoint_review.py'),'handlebar-grips'],check=True)
