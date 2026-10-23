"""Verify pinned delivery, preserved geometry, native/export registrations and real captures."""
import argparse,copy,hashlib,json,struct
from pathlib import Path
from derive_handlebar_registration_v2 import decode
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'creative/reviews/assembly-alignment-v1'
def read(p):return json.loads(p.read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
paths=[]
for folder in ['assets-src/moto-components/assembly-alignment-v1','creative/reviews/assembly-alignment-v1','creative/research/assembly-alignment-v1','tools/assembly-alignment-review-v1']:
 paths.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and p.name!='manifest.json')
paths.extend((ROOT/'tools').glob('*assembly_alignment*v1.*'));paths.append(ROOT/'creative/workflow/records/moto-assembly-alignment-001.json')
if args.write:(OUT/'manifest.json').write_text(json.dumps({'files':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(set(paths))]},indent=2)+'\n')
manifest=read(OUT/'manifest.json')
for r in manifest['files']:
 p=ROOT/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],r['path']
plan=read(ROOT/'creative/research/assembly-alignment-v1/plan.json');report=read(OUT/'composition-check.json');native=read(OUT/'native-check.json')
base,bb=decode((ROOT/plan['source_glb']).read_bytes());new,nb=decode((ROOT/'assets-src/moto-components/assembly-alignment-v1/motorcycle-aligned.glb').read_bytes());add,ab=decode((ROOT/'assets-src/moto-components/assembly-alignment-v1/alignment-mounts.glb').read_bytes())
assert nb==bb+ab
assert len(native['changes'])==len(plan['changes'])==len(report['changed_parent_nodes'])==47
assert sha(ROOT/plan['source_glb'])==report['source_sha256']
assert sha(ROOT/'assets-src/moto-components/assembly-alignment-v1/motorcycle-aligned.glb')==report['output_sha256']
for table in ['nodes','meshes','materials','accessors','bufferViews','images','textures','samplers']:
 old=copy.deepcopy(new[table][:len(base[table])])
 if table=='nodes':
  for i in report['changed_parent_nodes']:old[i]=base[table][i]
 if table=='materials':old[report['changed_original_material']]=base[table][report['changed_original_material']]
 assert old==base[table],table
# Independently compare saved Blender world matrices against glTF transforms.
def mul(a,b):return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]
C=[[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]];Ci=list(map(list,zip(*C)))
for c in native['changes']:
 n=next(n for n in new['nodes'] if n.get('name')==c['name'])
 expected=mul(mul(C,c['after_blender']),Ci)
 assert max(abs(n['matrix'][j*4+i]-expected[i][j]) for i in range(4) for j in range(4))<1e-6,c['name']
material=new['materials'][report['changed_original_material']];assert not material.get('extensions') and material['pbrMetallicRoughness']['baseColorFactor']==plan['material_change']['base_color']
export=read(OUT/'export-check.json');assert all(r['issues']['numErrors']==0 for r in export['validations']);assert len(export['parts'])==29 and export['triangles']==8428
surface=read(OUT/'native-surface-check.json');assert len(surface['new_meshes'])==29 and all(r['non_manifold_edges']==0 and r['volume_m3']>0 for r in surface['new_meshes'])
browser=read(OUT/'browser-check.json');assert not browser['page_errors'] and not browser['http_failures'];assert len(browser['captures'])==8
for r in browser['captures']:
 data=(OUT/r['file']).read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n'
 expected=(3840,2880) if r['file'].startswith(('front','rear')) else (2560,1920)
 assert struct.unpack('>II',data[16:24])==expected and hashlib.sha256(data).hexdigest()==r['sha256']
 assert r['runtime']['textures_ready'] and set(r['runtime']['text_meshes'])=={'Plate text Art.','Plate text 015'}
print(json.dumps({'valid':True,'pinned_files':len(manifest['files']),'registrations':47,'new_meshes':29,'captures':8,'art_accepted':False},indent=2))
