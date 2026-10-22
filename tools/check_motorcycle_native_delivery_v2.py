"""Reopen exact native delivery, check all linked poses, and optionally inventory portable glTF resources."""
import bpy,sys,runpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:];rev=args[0];native='assets-src/moto-components/'+rev+'/'+rev+'.blend';assert Path(bpy.data.filepath).resolve()==(R/native).resolve()
for script in ['check_whole_exterior_coverage_v3.py','read_whole_native_bounds_v1.py']:
 sys.argv=[script,'--',rev];runpy.run_path(str(R/'tools'/script),run_name='__main__')
if len(args)==3:
 script='collect_motorcycle_portable_files_v1.py';sys.argv=[script,'--',native,args[1],args[2]];runpy.run_path(str(R/'tools'/script),run_name='__main__')
print('ACTUAL_NATIVE_DELIVERY_CHECKED',rev)
