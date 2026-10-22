"""CLI exemplar wrapper over callable build/render functions; zero physical-ID increment."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build import build,render,normalize_object,export

def main(argv=None):
 argv=list(sys.argv[sys.argv.index('--')+1:] if argv is None and '--' in sys.argv else argv or [])
 mode=argv[0] if argv else 'build'
 if mode=='build':build()
 elif mode in ['gray','preview']:render(mode)
 elif mode=='final':
  import runpy
  runpy.run_path('/workspace/wewa/creative/research/right-side-cover-coordinate-conversion-v1/render-final.py',run_name='__main__')
 else:raise ValueError(mode)
if __name__=='__main__':main()
