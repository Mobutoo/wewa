"""Download or verify the exact original Blender/glTF resource tree from public GitHub; never overwrite changed files."""
import argparse,json,hashlib,urllib.request,urllib.parse,tempfile,os
from pathlib import Path,PurePosixPath
p=argparse.ArgumentParser();p.add_argument('--manifest',default='creative/research/motorcycle-assembled-v1/portable-files.json');p.add_argument('--destination',required=True);p.add_argument('--ref',default='main');p.add_argument('--format',choices=['native','runtime','all'],default='all');p.add_argument('--verify-local',action='store_true');a=p.parse_args();data=json.loads(Path(a.manifest).read_text());dest=Path(a.destination).resolve();checked=0;downloaded=0;missing=[]
for row in data['files']:
 if a.format!='all' and a.format not in row['usage']:continue
 rel=PurePosixPath(row['path']);assert not rel.is_absolute()and'..'not in rel.parts;target=dest/str(rel);assert target.resolve().is_relative_to(dest)
 if target.exists():
  raw=target.read_bytes();assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['sha256'],('Existing file differs; preserved without overwrite',str(target));checked+=1;continue
 if a.verify_local:missing.append(str(rel));continue
 target.parent.mkdir(parents=True,exist_ok=True);url='https://raw.githubusercontent.com/Mobutoo/wewa/'+urllib.parse.quote(a.ref,safe='')+'/'+urllib.parse.quote(str(rel),safe='/');req=urllib.request.Request(url,headers={'User-Agent':'WEWA-model-resource-fetch/1.0'});tmp=None
 try:
  with urllib.request.urlopen(req,timeout=90)as response,tempfile.NamedTemporaryFile(dir=target.parent,delete=False)as f:
   tmp=Path(f.name);digest=hashlib.sha256();size=0
   while True:
    b=response.read(1024*1024)
    if not b:break
    f.write(b);digest.update(b);size+=len(b)
  assert size==row['bytes']and digest.hexdigest()==row['sha256'],('Downloaded bytes differ from frozen model manifest',str(rel));assert not target.exists();os.replace(tmp,target);tmp=None;downloaded+=1;print('DOWNLOADED',rel,flush=True)
 finally:
  if tmp and tmp.exists():tmp.unlink()
assert not missing,('Missing local resources',missing)
print(json.dumps(dict(verified_existing=checked,downloaded=downloaded,format=a.format,destination=str(dest),scope='Exact frozen file tree only; no Unity/editor/hardware qualification')))
