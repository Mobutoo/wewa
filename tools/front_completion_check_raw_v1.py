"""Read actual EXR sample metadata/channels and paired PNG dimensions; no calibration claim."""
from pathlib import Path
from PIL import Image
import struct,json,hashlib,sys
R=Path('/workspace/wewa');out=R/sys.argv[1];rows=[]
def z(f):
 b=bytearray()
 while True:
  c=f.read(1)
  if c==b'\0':return b.decode()
  if not c:raise EOFError('Truncated EXR header')
  b+=c
for folder in sys.argv[2:]:
 for p in sorted((R/folder/'raw').glob('*.exr')):
  with p.open('rb')as f:
   assert f.read(4)==b'\x76\x2f\x31\x01';version=struct.unpack('<I',f.read(4))[0];a={}
   while True:
    n=z(f)
    if not n:break
    t=z(f);s=struct.unpack('<I',f.read(4))[0];a[n]=(t,f.read(s))
  channels={};data=a['channels'][1];offset=0
  while data[offset]:
   end=data.index(0,offset);name=data[offset:end].decode();offset=end+1;channels[name]=struct.unpack_from('<i',data,offset)[0];offset+=16
  assert channels and all(t==2 for t in channels.values()),(p,channels)
  samples={k:v[1].decode()for k,v in a.items()if k.endswith('.samples')};assert samples and all(v=='96'for v in samples.values()),(p,samples)
  x0,y0,x1,y1=struct.unpack('<4i',a['dataWindow'][1]);size=(x1-x0+1,y1-y0+1);png=p.parent.parent/(p.stem+'.png');assert png.exists()and Image.open(png).size==size
  rows.append({'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'resolution_px':size,'actual_header_samples':samples,'all_channels_FLOAT32':True,'channels':channels,'paired_PNG':str(png.relative_to(R)),'PNG_sha256':hashlib.sha256(png.read_bytes()).hexdigest()})
assert rows;out.parent.mkdir(exist_ok=True,parents=True);out.write_text(json.dumps({'files':rows,'scope':'Actual saved EXR FLOAT32 channels, cycles sample metadata, dimensions, PNG pairing and hashes; no decoded-pixel radiometry or artistic/hardware acceptance'},indent=2));print(len(rows),'native96 EXR/PNG pairs verified')
