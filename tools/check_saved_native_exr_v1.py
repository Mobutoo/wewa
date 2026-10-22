"""Read actual recursively saved EXR header, channels, FLOAT32 and dimensions; no artistic assertion."""
import argparse,json,hashlib,struct
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('folder');p.add_argument('--output',required=True);a=p.parse_args();R=Path(__file__).resolve().parents[1];rows=[]
def z(f):
 b=bytearray()
 while True:
  c=f.read(1);assert c,'Truncated EXR'
  if c==b'\0':return b.decode()
  b.extend(c)
for path in sorted((R/a.folder).rglob('*.exr')):
 with path.open('rb')as f:
  assert f.read(4)==b'\x76\x2f\x31\x01';version=struct.unpack('<I',f.read(4))[0];attrs={}
  while True:
   name=z(f)
   if not name:break
   kind=z(f);size=struct.unpack('<I',f.read(4))[0];attrs[name]=(kind,f.read(size))
  data=attrs['channels'][1];i=0;ch={}
  while data[i]:
   j=data.index(0,i);name=data[i:j].decode();i=j+1;ch[name]=struct.unpack_from('<i',data,i)[0];i+=16
  assert ch and all(v==2 for v in ch.values()),(path,ch)
  for c in 'RGB':assert any(n==c or n.endswith('.'+c)for n in ch),(path,c)
  x0,y0,x1,y1=struct.unpack('<4i',attrs['dataWindow'][1]);assert x1>=x0 and y1>=y0
 rows.append(dict(path=str(path.relative_to(R)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size,channels=ch,FLOAT32=True,resolution=[x1-x0+1,y1-y0+1]))
assert rows;dest=R/a.output;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(dict(files=rows,scope='Actual saved EXR header/hash checks; no pixel/art reception'),indent=2)+'\n');print('CHECKED_FLOAT32_EXR',len(rows))
