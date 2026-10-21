import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import stage
review,source_dir,mode=sys.argv[sys.argv.index('--')+1:];stage(review,source_dir,mode)
