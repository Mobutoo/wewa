import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from lever_builder import build
build(Path(__file__).resolve().parent)
