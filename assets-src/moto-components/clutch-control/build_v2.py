from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'clutch-control'))
from lever_builder_v2 import build
build(HERE)
