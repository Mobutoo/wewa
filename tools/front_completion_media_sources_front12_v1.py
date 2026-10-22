"""Exact-code media followup, originals private; not a geometry or fidelity decision."""
from pathlib import Path
import urllib.request,urllib.parse,sys,json,hashlib
key,code=sys.argv[1:3];O=Path('/workspace/wewa/creative/research')/key;P=Path('/workspace/wewa-assets/references')/key;O.mkdir(exist_ok=False);P.mkdir(exist_ok=False);url='https://bajajmatriz.com/wp-json/wp/v2/media?'+urllib.parse.urlencode({'search':code,'per_page':30});report={'code':code,'query':url,'images':[],'actually_viewed':False,'originals_public':False}
try:
 with urllib.request.urlopen(url,timeout=25)as f:d=json.load(f)
 report['api_results']=len(d)
 for im in d:
  u=im.get('source_url','')
  if code.lower()not in u.lower():continue
  with urllib.request.urlopen(u,timeout=25)as f:b=f.read()
  p=P/(code+'-'+str(len(report['images']))+'.jpg');p.write_bytes(b);report['images'].append({'url':u,'private_path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'rights':'Private documentary reference only'})
except Exception as e:report['error']=str(e)
(O/'source-register.json').write_text(json.dumps(report,indent=2));print(code,report.get('api_results'),len(report['images']),report.get('error',''))
