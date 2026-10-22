"""One native reopen: exact dependency/pose checks, evaluated bounds, and portable-resource inventory."""
import runpy,sys,bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:];rev=args[0];native='assets-src/moto-components/'+rev+'/'+rev+'.blend'
for script,argv in [('check_whole_exterior_coverage_v3.py',['--',rev]),('read_whole_native_bounds_v1.py',['--',rev]),('collect_motorcycle_portable_files_v1.py',['--',native,'assets-src/moto-components/motorcycle-assembled-v1.gltf','creative/research/motorcycle-assembled-v1/portable-files.json'])]:
 sys.argv=[script,*argv];runpy.run_path(str(R/'tools'/script),run_name='__main__')
print('NATIVE_SOURCE_BOUNDS_RESOURCES_COLLECTED',rev)
