"""Preserve original GLB buffers; apply planned group matrices and append mounts."""
import copy,hashlib,json
from pathlib import Path
import numpy as np
from derive_handlebar_registration_v2 import decode,encode
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets-src/moto-components/visual-proportions-v2';REVIEW=ROOT/'creative/reviews/visual-proportions-v2'
plan=json.loads((ROOT/'creative/research/visual-proportions-v2/plan.json').read_text())
native=json.loads((REVIEW/'native-check.json').read_text())
base,bb=decode((ROOT/plan['source_glb']).read_bytes());add,ab=decode((OUT/'proportion-additions.glb').read_bytes());result=copy.deepcopy(base)
def matrix(n):
 if 'matrix'in n:return np.array(n['matrix']).reshape(4,4).T
 x,y,z,w=n.get('rotation',[0,0,0,1]);m=np.eye(4)
 m[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0]);return m
changed=[]
for c in native['changes']:
 ids=[i for i,n in enumerate(result['nodes']) if n.get('name')==c['name']];assert len(ids)==1,(c['name'],ids)
 i=ids[0]
 # Non-root battery children have an identity parent, explicitly verified.
 if i not in result['scenes'][0]['nodes']:
  parents=[n for n in base['nodes'] if i in n.get('children',[])];assert len(parents)==1 and np.allclose(matrix(parents[0]),np.eye(4)),c['name']
 n=result['nodes'][i];m=np.array(c['delta_gltf'])@matrix(n)
 for k in ['translation','rotation','scale','matrix']:n.pop(k,None)
 n['matrix']=m.T.flatten().tolist();changed.append(i)
assert not any(add.get(k) for k in ['textures','images','animations','skins'])
tables=['nodes','meshes','materials','accessors','bufferViews'];offsets={t:len(base[t]) for t in tables}
for n in add['nodes']:
 if 'mesh'in n:n['mesh']+=offsets['meshes']
 if 'children'in n:n['children']=[i+offsets['nodes'] for i in n['children']]
for m in add['meshes']:
 for p in m['primitives']:
  p['attributes']={k:v+offsets['accessors'] for k,v in p['attributes'].items()};p['indices']+=offsets['accessors'];p['material']+=offsets['materials']
for a in add['accessors']:a['bufferView']+=offsets['bufferViews']
for v in add['bufferViews']:v['byteOffset']=v.get('byteOffset',0)+len(bb)
for t in tables:result[t].extend(add[t])
result['buffers']=[{'byteLength':len(bb)+len(ab)}]
removed=[i for i,n in enumerate(result['nodes']) if n.get('name') in plan['deactivated_roots']]
assert len(removed)==len(plan['deactivated_roots'])
result['scenes'][0]['nodes']=[i for i in result['scenes'][0]['nodes'] if i not in removed]
result['scenes'][0]['nodes'] += [i+offsets['nodes'] for i in add['scenes'][0]['nodes']]
path=OUT/'motorcycle-proportions.glb';path.write_bytes(encode(result,bb+ab))
a,b=decode(path.read_bytes());assert b==bb+ab
for t in tables+['images','textures','samplers']:
 old=copy.deepcopy(a[t][:len(base[t])])
 if t=='nodes':
  for i in changed:old[i]=base[t][i]
 assert old==base[t],t
report={'source':plan['source_glb'],'source_sha256':hashlib.sha256((ROOT/plan['source_glb']).read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'original_binary_preserved':True,'original_geometry_textures_preserved':True,'changed_parent_nodes':changed,'deactivated_roots':plan['deactivated_roots'],'new_meshes':len(add['meshes']),'new_roots':len(add['scenes'][0]['nodes']),'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(REVIEW/'composition-check.json').write_text(json.dumps(report,indent=2)+'\n');print('PROPORTIONS_COMPOSED',len(changed),path.stat().st_size)
