import json,hashlib,struct,datetime
from pathlib import Path
O=Path(__file__).resolve().parent;R=Path('/workspace/wewa');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def cstring(f):
 b=bytearray()
 while True:
  c=f.read(1)
  if c==b'\0':return b.decode()
  if not c:raise ValueError('truncated EXR')
  b.extend(c)
raw=[]
for view in ['left','right','quarter']:
 p=O/('native-'+view+'.exr')
 with p.open('rb') as f:
  assert struct.unpack('<I',f.read(4))[0]==20000630;version=f.read(4);attrs={}
  while True:
   name=cstring(f)
   if not name:break
   typ=cstring(f);size=struct.unpack('<I',f.read(4))[0];attrs[name]=(typ,f.read(size))
  channels=[];buf=attrs['channels'][1];i=0
  while buf[i]:
   j=buf.index(0,i);name=buf[i:j].decode();ptype=struct.unpack_from('<i',buf,j+1)[0];channels.append(dict(name=name,pixel_type=ptype,bits=32 if ptype==2 else 16));i=j+17
  assert channels and all(c['pixel_type']==2 for c in channels)
  dw=struct.unpack('<iiii',attrs['dataWindow'][1]);assert [dw[2]-dw[0]+1,dw[3]-dw[1]+1]==[540,480]
  raw.append(dict(path=p.name,sha256=sha(p),channels=channels,resolution=[540,480],raw32=True))
render=json.loads((O/'native-render-report.json').read_text());assert len(render)==3 and all(r['samples']==96 and r['threads']==2 and r['device']=='CPU' for r in render)
parents=json.loads((O/'poses-and-sources.json').read_text())['parents'];assert all(sha(R/r['source'])==r['sha256'] for r in parents)
parity=json.loads((O/'parity.json').read_text());assert parity['triangle_position_multiset_equal'] and parity['missing_triangles']==parity['added_triangles']==0
assert json.loads((O/'gltf-validation.json').read_text())['issues']['numErrors']==0
(O/'raw32-check.json').write_text(json.dumps(dict(raw=raw,native_96_three_views=True),indent=2))
files=[]
for p in sorted(O.rglob('*')):
 if not p.is_file() or p.name=='frozen-outputs.json' or '__pycache__' in p.parts:continue
 assert p.stat().st_size<100*1024**2,str(p)
 files.append(dict(path=str(p.relative_to(O)),bytes=p.stat().st_size,sha256=sha(p)))
manifest=dict(schema=1,frozen_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Engine-only conditional donor comparison; main handles whole assembly and repetitions',status='FROZEN_CANDIDATE_REWORK_NOT_COMPLETE_OEM',art_accepted=False,G8=False,main_entry='engine-exterior-completion-v1-linked.blend',main_collection='WEWA_ENGINE_EXTERIOR_COMPLETION_V1_CONDITIONAL',main_fragment='main-integration-fragment.json',inputs_unchanged=True,public_file_limit_bytes=100*1024**2,total_bytes=sum(x['bytes'] for x in files),outputs=files,remaining=['Donor identity/pairing/OEM fit unresolved','Estimated axial depth/profile registration, visible bottom silhouette mismatch','LH external boss and crown morphology not completed in inherited source','Upper lands/output-panel alternate source frames not installed','Whole-context visibility and frame contacts left to main'])
(O/'frozen-outputs.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(dict(files=len(files),bytes=manifest['total_bytes'],sha256=sha(O/'frozen-outputs.json'),status=manifest['status'])))
