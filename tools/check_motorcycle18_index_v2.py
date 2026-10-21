"""V2: check every numbered review page in addition to the original exact-tree checks.
Verify repository JSON, manifest file bytes/hashes and catalogue files in an exact Git tree.
Default: staged index. --ref: immutable commit/tree. No visual or hardware qualification.
"""
import subprocess,json,hashlib,posixpath,argparse,tempfile,re
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from pathlib import Path
repo=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ref');p.add_argument('--output',type=Path,default=Path(tempfile.gettempdir())/'wewa18-index-check.json');args=p.parse_args()
command=['git','ls-tree','-r','-z',args.ref]if args.ref else['git','ls-files','--stage','-z']
r=subprocess.run(command,cwd=repo,capture_output=True,check=True).stdout
entries={}
for row in r.split(b'\0'):
 if not row:continue
 meta,path=row.split(b'\t',1)
 if args.ref:
  mode,kind,oid=meta.decode().split()
  if kind!='blob':continue
 else:
  mode,oid,stage=meta.decode().split();assert stage=='0'
  if mode=='160000':continue
 entries[path.decode()]=oid
cache={}
def blob(path):
 oid=entries[path]
 if oid not in cache:cache[oid]=subprocess.run(['git','cat-file','blob',oid],cwd=repo,capture_output=True,check=True).stdout
 return cache[oid]
errors=[];jsons=0;checked=0;manifests=0;checkpoint_pngs=0
for path in entries:
 if not path.endswith('.json'):continue
 try:d=json.loads(blob(path));jsons+=1
 except Exception as ex:errors.append([path,'json',str(ex)]);continue
 if Path(path).name=='render-checkpoints.json' and isinstance(d,dict) and isinstance(d.get('views'),dict):
  for name,v in d['views'].items():
   if not v.get('PNG_path') or not v.get('PNG_sha256'):continue
   ref=v['PNG_path'];target=ref.removeprefix(str(repo)+'/')
   if target.startswith('/'):continue
   if target not in entries:errors.append([path,'missing_checkpoint_png',name,ref]);continue
   checkpoint_pngs+=1
   if hashlib.sha256(blob(target)).hexdigest()!=v['PNG_sha256']:errors.append([path,'checkpoint_png_hash',name,ref])
 if 'manifest' not in Path(path).name or not isinstance(d,dict) or not isinstance(d.get('files'),list):continue
 manifests+=1
 for e in d['files']:
  if not isinstance(e,dict) or not e.get('sha256') or not e.get('path'):continue
  ref=e['path']
  if ref.startswith('/'):continue
  target=ref if ref in entries else posixpath.normpath(posixpath.join(posixpath.dirname(path),ref))
  if target not in entries:errors.append([path,'missing',ref]);continue
  value=blob(target);actual=hashlib.sha256(value).hexdigest();checked+=1
  if actual!=e['sha256']:errors.append([path,'hash',ref,e['sha256'],actual])
  if 'bytes' in e and e['bytes']!=len(value):errors.append([path,'bytes',ref,e['bytes'],len(value)])
# The curated catalogue must be self-contained in this exact staged tree.
catalog=json.loads(blob('tools/motorcycle-lab/catalog.json'))
for key,c in catalog['assets'].items():
 for ref in [c['source'],*c['files']]:
  target='assets-src/moto-components/'+ref
  if target not in entries:errors.append(['catalog','missing',key,target])
class Links(HTMLParser):
 def __init__(self):super().__init__();self.urls=[]
 def handle_starttag(self,tag,attrs):self.urls.extend(v for k,v in attrs if k in {'href','src'} and v)
links_checked=0
for page in ['creative/reviews/motorcycle18-gallery/index.html','creative/reviews/motorcycle18-components.md', *sorted(p for p in entries if re.fullmatch(r'creative/reviews/motorcycle18-checkpoint-\d+\.md', p))]:
 if page not in entries:continue
 value=blob(page).decode();parser=Links();parser.feed(value)
 urls=parser.urls+[m.group(1) for m in re.finditer(r'!?\[[^\]]*\]\(([^)]+)\)',value)]
 for url in urls:
  split=urlsplit(url.strip('<>'))
  if split.scheme or split.netloc or not split.path:continue
  path=unquote(split.path);target=posixpath.normpath(path.lstrip('/') if path.startswith('/') else posixpath.join(posixpath.dirname(page),path));links_checked+=1
  if target not in entries and not any(p.startswith(target.rstrip('/')+'/') for p in entries):errors.append([page,'missing_review_link',url,target])
report={'scope':'git_ref' if args.ref else 'git_index','requested_ref':args.ref,'resolved_tree':subprocess.run(['git','rev-parse',args.ref+'^{tree}'],cwd=repo,capture_output=True,text=True,check=True).stdout.strip() if args.ref else subprocess.run(['git','write-tree'],cwd=repo,capture_output=True,text=True,check=True).stdout.strip(),'json_files':jsons,'manifests':manifests,'file_hashes':checked,'checkpoint_png_hashes':checkpoint_pngs,'review_links_checked':links_checked,'catalogue_assets':len(catalog['assets']),'errors':errors}
print(json.dumps(report,indent=2))
args.output.write_text(json.dumps(report,indent=2)+'\n')
raise SystemExit(bool(errors))
