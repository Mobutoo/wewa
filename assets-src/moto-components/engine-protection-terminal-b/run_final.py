"""One sequential Blender worker with persistent actual exit state; no hidden queue."""
from pathlib import Path
import json,hashlib,datetime,subprocess,sys,os,shutil
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-protection-terminal-b-v1';W=Path('/workspace/wewa-assets/work-in-progress');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=H/'engine-protection-terminal-b-v1.blend';before=sha(source);log=W/'engine-protection-terminal-b-v1-final-render.log';p=O/'render-worker.json'
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
if p.exists():shutil.copyfile(p,W/('engine-protection-terminal-b-v1-worker-before-'+stamp+'.json'))
if log.exists():shutil.copyfile(log,W/('engine-protection-terminal-b-v1-log-before-'+stamp+'.txt'))
q={'source_sha256':before,'state':'running','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'worker_pid':os.getpid(),'exit_code':None,'log_private':str(log)};p.write_text(json.dumps(q,indent=2)+'\n')
with log.open('w')as f:
 process=subprocess.Popen(['/workspace/wewa-tools/blender-4.3.2-linux-x64/blender','--background','--threads','1','--python-exit-code','1','--python',str(H/'render.py'),'--','--final'],cwd=R,stdout=f,stderr=subprocess.STDOUT);q['blender_pid']=process.pid;p.write_text(json.dumps(q,indent=2)+'\n');code=process.wait()
q.update(state='completed'if code==0 else'failed',exit_code=code,source_unchanged=sha(source)==before,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());p.write_text(json.dumps(q,indent=2)+'\n');assert code==0 and q['source_unchanged'];print('TERMINAL_B_FINAL_WORKER_EXIT0',flush=True)
