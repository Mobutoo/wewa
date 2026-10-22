import json,re,hashlib
from pathlib import Path
R=Path('/workspace/wewa');O=Path(__file__).resolve().parent;hits={}
def walk(d,origin):
 if isinstance(d,list):
  for x in d:walk(x,origin)
 elif isinstance(d,dict):
  if isinstance(d.get('source'),str) and d.get('source_objects'):
   if re.search(r'front-completion-p2[1234]-|fuel-tap-stepped-hex|chaincase-front-ear|brake-actuation',d['source']):
    s=d['source'];s=s if s.startswith('assets-src/')else'assets-src/moto-components/'+s
    if s not in hits:hits[s]=dict(**d,evidence_files=[])
    hits[s]['evidence_files'].append(origin)
  for v in d.values():
   if isinstance(v,(dict,list)):walk(v,origin)
for p in sorted((R/'creative/reviews').glob('front-completion-*/**/*catalog*fragment*.json')):
 try:walk(json.loads(p.read_text()),str(p.relative_to(R)))
 except (ValueError,TypeError):pass
(O/'catalog-candidates.json').write_text(json.dumps(list(hits.values()),indent=2))
for s,v in hits.items():print(s,'OBJECTS',v['source_objects'])
