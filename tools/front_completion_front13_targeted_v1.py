"""New independent search routes; never repeat the prior supplier/media negatives."""
from pathlib import Path
import urllib.request,urllib.parse,xml.etree.ElementTree as ET,json,hashlib,concurrent.futures
R=Path('/workspace/wewa');O=R/'creative/research/front-completion-front13-targeted-v1';P=Path('/workspace/wewa-assets/references/front-completion-front13-targeted-v1');O.mkdir(exist_ok=False);P.mkdir(exist_ok=False)
queries=[('P06','Bajaj Boxer BM150 headlight lens reflector disassembly'),('P06','"PF401003" headlight lens'),('P24','Bajaj Boxer BM150 speedometer drive front wheel valve parts'),('P28','"DS181009"'),('P28','"DS181010"'),('P23','"DH151029"')]
def run(t):
 pkg,q=t;u='https://www.bing.com/search?'+urllib.parse.urlencode({'format':'rss','q':q});row={'package':pkg,'query':q,'url':u,'links':[],'geometry_unlocked':False}
 try:
  b=urllib.request.urlopen(u,timeout=20).read();p=P/(pkg+'-'+hashlib.sha256(q.encode()).hexdigest()[:8]+'.xml');p.write_bytes(b);row['private_response_sha256']=hashlib.sha256(b).hexdigest();row['links']=[i.findtext('link') for i in ET.fromstring(b).findall('./channel/item')]
 except Exception as e:row['error']=str(e)
 return row
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:rows=list(pool.map(run,queries))
(O/'search-register.json').write_text(json.dumps({'method':'New Bing RSS discovery only; links are not photographic evidence or acceptance','queries':rows,'private_originals':True},indent=2))
for row in rows:print(row['package'],row['query'],*row['links'][:5],row.get('error',''),sep='\n')
