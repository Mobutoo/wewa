"""Actual single-layer FLOAT32 EXR headers; separate denoised presentation."""
from pathlib import Path
import json,struct,hashlib
R=Path('/workspace/wewa');O=R/'creative/reviews/headlamp-front-photo-reconstruction-v1'
def z(f):
 b=bytearray()
 while True:
  c=f.read(1)
  if c==b'\0':return b.decode()
  if not c:raise ValueError('Truncated EXR')
  b.extend(c)
for folder in [O/'denoised-96']:
 report=json.loads((folder/'render-report.json').read_text());rows=[]
 for p in sorted((folder/'raw').glob('*.exr')):
  with p.open('rb') as f:
   assert f.read(4)==b'\x76\x2f\x31\x01';f.read(4);attrs={}
   while True:
    n=z(f)
    if not n:break
    t=z(f);size=struct.unpack('<I',f.read(4))[0];attrs[n]=(t,f.read(size))
  data=attrs['channels'][1];i=0;channels={}
  while data[i]:
   e=data.index(0,i);n=data[i:e].decode();i=e+1;channels[n]=struct.unpack_from('<i',data,i)[0];i+=16
  assert all(c in channels for c in ['R','G','B']) and all(t==2 for t in channels.values())
  a,b,c,d=struct.unpack('<4i',attrs['dataWindow'][1]);assert [c-a+1,d-b+1]==[640,480]
  png=folder/(p.stem+'.png');head=png.read_bytes()[:24];assert struct.unpack('>II',head[16:24])==(640,480)
  view=next(v for v in report['views'] if v['view']==p.stem);assert view['samples']==96
  samples={k:v[1].decode() for k,v in attrs.items() if k.endswith('.samples')}
  assert not samples or all(v=='96' for v in samples.values())
  rows.append({'EXR':str(p.relative_to(R)),'EXR_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'PNG':str(png.relative_to(R)),'PNG_sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'channels':channels,'all_channels_FLOAT32':True,'resolution':[640,480],'samples_from_source_protocol':96,'samples_in_actual_EXR_header':samples,'denoising':report['denoising']})
 assert len(rows)==2
 (folder/'raw-render-check.json').write_text(json.dumps({'files':rows,'scope':'Actual single-layer EXR channel/dimension/hash and PNG header checks; sample metadata distinguished from source protocol. Not measured optical or radiometric qualification.'},indent=2))
 print(len(rows),'actual EXR/PNG pairs verified; denoising',report['denoising'])
