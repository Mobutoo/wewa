"""Save exact author-frozen files, resume unpublished attempts, preserve verbatim log whitespace; never assert package completion."""
import argparse,hashlib,json,os,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];parser=argparse.ArgumentParser();parser.add_argument('tables',nargs='+');args=parser.parse_args();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for table in args.tables:
 tab=Path(table);assert not tab.is_absolute()and'..'not in tab.parts;key=tab.parent.name
 data=json.loads((R/tab).read_text());rows=list(data.get('files',data.get('frozen_files',[])));assert rows
 manifest=Path('creative/reviews/continuation-backup-v1')/(key+'.json');
 if (R/manifest).exists():
  published=subprocess.run(['git','cat-file','-e','HEAD:'+str(manifest)],cwd=R,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
  assert not published,('Published backup is immutable',str(manifest))
  assert json.loads((R/manifest).read_text())['author_frozen_table_sha256']==sha(R/tab),'Incomplete backup input changed'

 for row in rows:
  p=Path(row['path']);assert not p.is_absolute()and'..'not in p.parts;f=R/p;assert f.stat().st_size==row['bytes']and sha(f)==row['sha256'],row['path'];assert row['bytes']<100*1024**2
 paths={row['path']for row in rows};paths.update([str(tab),'tools/'+Path(__file__).name]);proof={'scope':'Exact frozen author source backup; no new coordination, fitted pose or artistic reception','author_frozen_table':str(tab),'author_frozen_table_sha256':sha(R/tab),'backup_protocol':'tools/'+Path(__file__).name,'backup_protocol_sha256':sha(Path(__file__)),'files':rows,'verbatim_logs_policy':'Exact frozen log bytes retained including original trailing whitespace; Git whitespace check still covers every non-log path','art_accepted':False,'package_complete':False};(R/manifest).write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n');paths.add(str(manifest))
 staged=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=R,text=True).splitlines();assert set(staged)<=paths,('Unrelated staged changes',staged)
 subprocess.run(['git','add','--sparse','-f','--',*sorted(paths)],cwd=R,check=True)
 for row in rows:
  b=subprocess.check_output(['git','show',':'+row['path']],cwd=R);assert len(b)==row['bytes']and hashlib.sha256(b).hexdigest()==row['sha256'],row['path']
 for p in subprocess.check_output(['git','diff','--cached','--name-only'],cwd=R,text=True).splitlines():
  if p.endswith('.json'):json.loads(subprocess.check_output(['git','show',':'+p],cwd=R))
 subprocess.run(['git','diff','--cached','--check','--','.',':(glob,exclude)**/*.log'],cwd=R,check=True);subprocess.run(['git','commit','-m','Back up frozen '+key+' source and native evidence'],cwd=R,check=True,stdout=subprocess.DEVNULL);subprocess.run(['git','-c','pack.window=0','push','origin','HEAD:main'],cwd=R,check=True,env=os.environ|{'GIT_NO_LAZY_FETCH':'1','GIT_TERMINAL_PROMPT':'0'});print('BACKED_UP',key,len(rows),flush=True)
