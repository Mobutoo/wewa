"""Exact supplier reference queries; attributed metadata public, documentary originals private."""
import urllib.request,urllib.parse,json,hashlib,concurrent.futures,sys
from pathlib import Path
key=sys.argv[1];codes=sys.argv[2:];O=Path('/workspace/wewa/creative/research')/key;P=Path('/workspace/wewa-assets/references')/key;O.mkdir(exist_ok=False);P.mkdir(exist_ok=False)
def fetch(code):
 u='https://www.croslandrepuestos.pe/api/catalog_system/pub/products/search?'+urllib.parse.urlencode({'fq':'alternateIds_RefId:'+code});row={'code':code,'query':u,'images':[],'actually_viewed':False}
 try:
  with urllib.request.urlopen(u,timeout=25)as f:d=json.load(f)
  row['results']=len(d)
  for product in d:
   for item in product.get('items',[]):
    refs=[x.get('Value')for x in item.get('referenceId',[])]
    if code not in refs:continue
    for im in item.get('images',[]):
     with urllib.request.urlopen(im['imageUrl'],timeout=25)as f:b=f.read()
     p=P/(code+'-'+str(len(row['images']))+'.jpg');p.write_bytes(b);row['images'].append({'product':product.get('productName'),'description':product.get('description'),'references':refs,'url':im['imageUrl'],'private_path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'rights':'Private documentary only; no photo redistribution'})
 except Exception as e:row['error']=str(e)
 return row
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:d=list(pool.map(fetch,codes))
(O/'source-register.json').write_text(json.dumps({'protocol':'tools/front_completion_exact_sources_front12_v1.py','sources':d,'all_dimensions_still_unmeasured':True},indent=2))
for x in d:print(x['code'],x.get('results'),len(x['images']),x.get('error',''))
