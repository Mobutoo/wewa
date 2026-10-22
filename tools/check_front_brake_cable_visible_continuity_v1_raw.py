from pathlib import Path
import struct,json,hashlib
R=Path('/workspace/wewa');O=R/'creative/reviews/front-brake-cable-visible-continuity-v1'
def z(f):
 b=bytearray()
 while True:
  c=f.read(1)
  if c==b'\0':return b.decode()
  if not c:raise ValueError('Truncated EXR')
  b.extend(c)
rows=[]
for p in sorted((O/'raw').glob('*.exr')):
 with p.open('rb') as f:
  assert f.read(4)==b'\x76\x2f\x31\x01';f.read(4);attrs={}
  while True:
   n=z(f)
   if not n:break
   t=z(f);size=struct.unpack('<I',f.read(4))[0];attrs[n]=(t,f.read(size))
 channels={};data=attrs['channels'][1];i=0
 while data[i]:
  e=data.index(0,i);n=data[i:e].decode();i=e+1;channels[n]=struct.unpack_from('<i',data,i)[0];i+=16
 assert all(n in channels for n in ['R','G','B']) and all(v==2 for v in channels.values())
 x,y,a,b=struct.unpack('<4i',attrs['dataWindow'][1]);assert [a-x+1,b-y+1]==[800,600]
 png=O/(p.stem+'.png');assert struct.unpack('>II',png.read_bytes()[16:24])==(800,600)
 samples={k:v[1].decode() for k,v in attrs.items() if k.endswith('.samples')};assert not samples or all(v=='96' for v in samples.values())
 rows.append({'EXR':str(p.relative_to(R)),'EXR_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'PNG':str(png.relative_to(R)),'PNG_sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'resolution':[800,600],'all_channels_FLOAT32':True,'channels':channels,'samples_in_EXR_header':samples,'source_protocol_samples':96,'denoising':True})
assert len(rows)==2
(O/'raw-render-check.json').write_text(json.dumps({'files':rows,'scope':'Actual EXR/PNG headers/hashes; not measured materials or optical qualification'},indent=2))
