import pathlib,urllib.request,urllib.error,json,hashlib,re,sys
P=pathlib.Path('/workspace/wewa-assets/references/headlamp-bare-component-last-source-v1');D=pathlib.Path('/workspace/wewa/creative/research/headlamp-bare-component-last-source-v1')
def fetch(key,url,circuit):
 row={'key':key,'url':url,'circuit':circuit}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (documentary component research)'}),timeout=20)as r:
   b=r.read(20*1024*1024+1);row.update(http_status=r.status,final_url=r.url,content_type=r.headers.get('Content-Type'))
  if len(b)>20*1024*1024:raise ValueError('Response exceeds20MiB research cap; not retained')
  (P/key).write_bytes(b);row.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 except Exception as e:row['error']=str(e);row['http_status']=getattr(e,'code',None)
 log=D/'access.json';a=json.loads(log.read_text())if log.exists()else[];a.append(row);log.write_text(json.dumps(a,indent=2)+'\n');return row
if __name__=='__main__':
 row=fetch(*sys.argv[1:]);print(json.dumps(row))
 if 'error'not in row:
  b=(P/row['key']).read_bytes()
  if 'html'in(row.get('content_type')or''):
   s=b.decode('utf8','replace');links=re.findall(r'''(?:href|src)=["']([^"']+)''',s,re.I);print('\n'.join(x for x in links if re.search('lamp|light|catalog|product|after|pdf|shop|bajaj|two.?wheeler',x,re.I))[:12000])
