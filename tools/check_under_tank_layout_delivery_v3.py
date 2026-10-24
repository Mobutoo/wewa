"""Verify immutable input, fitted export/source bounds, declared changes and captured pixels."""
import argparse,copy,hashlib,json,struct
from pathlib import Path
from derive_handlebar_registration_v2 import decode
ROOT=Path(__file__).resolve().parents[1];REV=ROOT/'creative/reviews/under-tank-layout-v3';OUT=ROOT/'assets-src/moto-components/under-tank-layout-v3'
def read(p):return json.loads(p.read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
files=[]
for folder in [REV,OUT,ROOT/'creative/research/under-tank-layout-v3',ROOT/'tools/under-tank-layout-review-v3']:
 files.extend(p for p in folder.rglob('*') if p.is_file() and p.name!='manifest.json')
files.extend((ROOT/'tools').glob('*under_tank_layout*v3.*'));files.append(ROOT/'creative/workflow/records/moto-under-tank-layout-003.json')
if args.write:(REV/'manifest.json').write_text(json.dumps({'files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(set(files))]},indent=2)+'\n')
manifest=read(REV/'manifest.json');assert {r['path'] for r in manifest['files']}=={str(p.relative_to(ROOT)) for p in files}
for r in manifest['files']:
 p=ROOT/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],r['path']
plan=read(ROOT/'creative/research/under-tank-layout-v3/plan.json');report=read(REV/'composition-check.json');native=read(REV/'native-check.json')
base,bb=decode((ROOT/plan['source_glb']).read_bytes());new,nb=decode((OUT/'motorcycle-layout.glb').read_bytes())
assert nb[:len(bb)]==bb
assert sha(ROOT/plan['source_glb'])==report['source_sha256'] and sha(OUT/'motorcycle-layout.glb')==report['output_sha256']
assert len(report['wrappers'])==len(plan['changes'])==len(native['changes'])==10
assert len(report['fitted_connections'])==len(native['deformations'])==11
for table in ['meshes','materials','accessors','bufferViews','images','textures','samplers']:
 assert new[table][:len(base[table])]==base[table],table
nodes=copy.deepcopy(new['nodes'][:len(base['nodes'])])
for row in report['fitted_connections']:
 assert nodes[row['node']]['mesh']==row['new_mesh'] and row['minimum_jacobian']>.05
 nodes[row['node']]['mesh']=row['original_mesh']
assert nodes==base['nodes']
roots=base['scenes'][0]['nodes'].copy()
def mul(a,b):return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]
C=[[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]];Ci=list(map(list,zip(*C)))
for row,source in zip(report['wrappers'],native['changes']):
 wrapper=new['nodes'][row['wrapper']];assert wrapper['children']==[row['original_node']]
 expected=mul(mul(C,source['delta_blender']),Ci)
 assert max(abs(wrapper['matrix'][j*4+i]-expected[i][j]) for i in range(4) for j in range(4))<1e-6
 assert max(abs(mul(source['delta_blender'],source['before_blender'])[i][j]-source['after_blender'][i][j]) for i in range(4) for j in range(4))<1e-6
 roots[roots.index(row['original_node'])]=row['wrapper']
assert new['scenes'][0]['nodes']==roots
# Only recorded inherited zero-area index triples may be removed.
def indices(doc,binary,i):
 a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']];fmt={5121:'B',5123:'H',5125:'I'}[a['componentType']]
 assert not v.get('byteStride')
 return struct.unpack_from('<'+fmt*a['count'],binary,v.get('byteOffset',0)+a.get('byteOffset',0))
assert sum(len(r['removed_triangles']) for r in report['inherited_zero_area_cleanup'])==2
for row in report['inherited_zero_area_cleanup']:
 old=indices(base,bb,row['old_indices']);removed=set(row['removed_triangles'])
 assert tuple(v for i,v in enumerate(old) if i//3 not in removed)==indices(new,nb,row['new_indices'])
measured=read(REV/'measured-check.json');assert measured['unaffected_groups_unchanged']
a,b=measured['measurements'];assert a['fixed']==b['fixed']
assert abs(b['tank_sidecover_profile_overlap_m']-a['tank_sidecover_profile_overlap_m']-.075)<1e-6
assert abs(b['float_bowl_to_upper_casting_vertical_envelope_gap_m']-a['float_bowl_to_upper_casting_vertical_envelope_gap_m']+.035)<1e-6
export=read(REV/'export-check.json');assert export['errors']==0 and export['no_new_warnings'] and export['sha256']==sha(OUT/'motorcycle-layout.glb')
for row in export['fitted_parts']:
 bounds=measured['fitted_source_bounds'][row['name']]
 assert max(abs(bounds[k][i]-row['blender_world_bounds'][k][i]) for k in ['min','max'] for i in range(3))<1e-6,row['name']
browser=read(REV/'browser-check.json');assert not browser['page_errors'] and not browser['http_failures'] and len(browser['captures'])==7
for row in browser['captures']:
 data=(REV/row['file']).read_bytes();expected=(3840,2880) if row['file'].startswith(('front','rear')) else (2560,1920)
 assert data[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',data[16:24])==expected and hashlib.sha256(data).hexdigest()==row['sha256']
 assert row['runtime']['textures_ready'] and set(row['runtime']['text_meshes'])=={'Plate text Art.','Plate text 015'}
print(json.dumps({'valid':True,'pinned_files':len(manifest['files']),'assembly_translations':10,'fitted_connections':11,'captures':7,'art_accepted':False},indent=2))
