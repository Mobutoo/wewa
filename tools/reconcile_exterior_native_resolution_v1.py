"""Add observed PNG/EXR dimensions without modifying frozen author reports or pixels."""
import json,struct,hashlib,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'creative/reviews'/sys.argv[1];p=O/'render-report.json';d=json.loads(p.read_text());rows=[]
def zstr(f):
 b=bytearray()
 while True:
  c=f.read(1)
  if not c:raise ValueError('Truncated EXR')
  if c==b'\0':return b.decode()
  b.extend(c)
for v in d['views']:
 png=O/(v['name']+'.png');exr=O/'raw'/(v['name']+'.exr')
 with png.open('rb')as f:
  h=f.read(24);assert h[:8]==b'\x89PNG\r\n\x1a\n';size=struct.unpack('>II',h[16:24])
 with exr.open('rb')as f:
  assert f.read(4)==b'\x76\x2f\x31\x01';f.read(4);attrs={}
  while True:
   n=zstr(f)
   if not n:break
   typ=zstr(f);length=struct.unpack('<I',f.read(4))[0];attrs[n]=(typ,f.read(length))
  a,b,c,e=struct.unpack('<4i',attrs['dataWindow'][1]);assert(c-a+1,e-b+1)==size
 original=v.get('source_author_view',{});declared=original.get('resolution_px',original.get('resolution'));rows.append({'view':v['name'],'source_author_declared_px':declared,'actual_PNG_and_EXR_px':list(size),'declaration_mismatch':declared is not None and list(declared)!=list(size),'PNG_sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'EXR_sha256':hashlib.sha256(exr.read_bytes()).hexdigest()});v['resolution_px']=list(size);v['resolution_provenance']='native-resolution-reconciliation-v1.json; independent actual PNG and EXR headers. Original author declaration retained unchanged under source_author_view.'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');(O/'native-resolution-reconciliation-v1.json').write_text(json.dumps({'scope':'Observed saved native dimensions; no resizing/rerender. Frozen author declarations and files retained. No art or calibration acceptance.','protocol':'tools/reconcile_exterior_native_resolution_v1.py','protocol_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'views':rows},ensure_ascii=False,indent=2)+'\n');print('NATIVE_DIMENSIONS_RECONCILED',sys.argv[1],sum(r['declaration_mismatch']for r in rows))
