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
V=O.parent/'engine-exterior-completion-v1';v1=json.loads((V/'frozen-outputs.json').read_text());assert sha(V/'frozen-outputs.json')=='466b977f356c51148744335c98b0b639326a69bd52138d7d691dca4b6fd78295'
assert all(sha(V/r['path'])==r['sha256'] for r in v1['outputs'])
parity=json.loads((O/'child-parity.json').read_text());assert parity['triangle_position_multiset_equal'] and parity['maximum_vertex_delta_m']==0
validation=json.loads((O/'child-gltf-validation.json').read_text());assert validation['issues']['numErrors']==validation['issues']['numWarnings']==0
runtime=json.loads((O/'runtime-check.json').read_text());assert runtime['triangles']==1462720 and len(runtime['removed_once'])==2 and not runtime['page_errors']
meta=json.loads((O/'new-child-data-report.json').read_text());assert sha(R/meta['glb'])==meta['glb_sha256'] and sha(R/meta['source'])==meta['source_sha256']
(O/'raw32-check.json').write_text(json.dumps(dict(raw=raw,native_96_three_views=True),indent=2))
files=[]
for p in sorted(O.rglob('*')):
 if not p.is_file() or p.name=='frozen-outputs.json' or '__pycache__' in p.parts:continue
 assert p.stat().st_size<100*1024**2,str(p)
 files.append(dict(path=str(p.relative_to(O)),bytes=p.stat().st_size,sha256=sha(p)))
manifest=dict(schema=1,frozen_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='FROZEN_LOWER_APRON_FIX_EXECUTED_CONDITIONAL_DONOR',scope='Observed same-donor LH lower apron; small LH rigid translation; main owns whole assembly and repetitions',art_accepted=False,G8=False,v1_preserved=dict(manifest_sha256=sha(V/'frozen-outputs.json'),all_55_outputs_unchanged=True),main_fragment='main-integration-fragment.json',main_entry='engine-exterior-completion-v2-linked.blend',main_collection='WEWA_ENGINE_EXTERIOR_COMPLETION_V2_CONDITIONAL',new_child='lh-donor-lower-apron-v2.blend',new_buffers='lh-donor-lower-apron-v2.glb',new_child_data='new-child-data-report.json',total_bytes=sum(r['bytes'] for r in files),max_public_file_bytes=max(r['bytes'] for r in files),outputs=files,limits=['Conditional JE541038 BM150 donor, not paired/OEM RDC125','Source metric depth and registration remain estimated','No full assembled engine reception or physical iPhone qualification'])
(O/'frozen-outputs.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(dict(files=len(files),bytes=manifest['total_bytes'],max_file_bytes=manifest['max_public_file_bytes'],manifest_sha256=sha(O/'frozen-outputs.json'),new_child_sha256=meta['source_sha256'],glb_sha256=meta['glb_sha256'],v1_unchanged=True)))
