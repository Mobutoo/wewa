"""Apply documented world transforms with new parents, retaining all original GLB bytes."""
import copy,json,hashlib
import numpy as np
from under_tank_layout_fields_v3 import field
from pathlib import Path
from derive_handlebar_registration_v2 import decode,encode
ROOT=Path(__file__).resolve().parents[1];REV=ROOT/'creative/reviews/under-tank-layout-v3';OUT=ROOT/'assets-src/moto-components/under-tank-layout-v3'
plan=json.loads((ROOT/'creative/research/under-tank-layout-v3/plan.json').read_text());base,binary=decode((ROOT/plan['source_glb']).read_bytes());doc=copy.deepcopy(base)
def mul(a,b):return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]
C=[[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]];Ci=list(map(list,zip(*C)));rows=[]
for c in plan['changes']:
 idx=next(i for i,n in enumerate(doc['nodes']) if n.get('name')==c['name']);assert idx in doc['scenes'][0]['nodes'],c['name']
 D=[[0.0]*4 for i in range(4)];D[3][3]=1
 for i in range(3):D[i][i]=c['scale'][i];D[i][3]=c['translation_blender_m'][i]+c['pivot_blender_m'][i]*(1-c['scale'][i])
 M=mul(mul(C,D),Ci);wrapper=len(doc['nodes']);doc['nodes'].append({'name':'LAYOUT ['+c['name']+']','matrix':[M[i][j] for j in range(4) for i in range(4)],'children':[idx]})
 doc['scenes'][0]['nodes'][doc['scenes'][0]['nodes'].index(idx)]=wrapper;rows.append({'original_node':idx,'wrapper':wrapper,'name':c['name']})
# Append float attributes for fitted connections; leave every original buffer byte intact.
def matrix(n):
 if 'matrix' in n:return np.array(n['matrix']).reshape(4,4).T
 x,y,z,w=n.get('rotation',[0,0,0,1]);m=np.eye(4)
 m[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0]);return m
world={}
def walk(i,parent):
 world[i]=parent@matrix(doc['nodes'][i])
 for child in doc['nodes'][i].get('children',[]):walk(child,world[i])
for i in doc['scenes'][0]['nodes']:walk(i,np.eye(4))
def descendants(i):
 yield i
 for child in doc['nodes'][i].get('children',[]):yield from descendants(child)
def values(index):
 a=base['accessors'][index];v=base['bufferViews'][a['bufferView']];dtype=np.dtype({5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4',5120:'i1',5121:'u1'}[a['componentType']]);n={'VEC3':3,'VEC4':4,'VEC2':2,'SCALAR':1}[a['type']]
 out=np.ndarray((a['count'],n),dtype=dtype,buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',dtype.itemsize*n),dtype.itemsize)).astype(float)
 if a.get('normalized'):out=np.maximum(out/np.iinfo(dtype).max,-1)
 return out
blob=bytearray(binary)
def attribute(array,position=False):
 while len(blob)%4:blob.append(0)
 start=len(blob);raw=np.asarray(array,dtype='<f4').tobytes();blob.extend(raw);view=len(doc['bufferViews']);doc['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':len(raw),'target':34962});a={'bufferView':view,'componentType':5126,'count':len(array),'type':'VEC'+str(array.shape[1])}
 if position:a.update(min=array.min(axis=0).tolist(),max=array.max(axis=0).tolist())
 index=len(doc['accessors']);doc['accessors'].append(a);return index
fitted=[];cleaned=[];Cnp=np.array(C);Cinv=np.array(Ci)
for spec in plan['deformations']:
 if 'mesh' in spec:ids=[i for i,n in enumerate(doc['nodes']) if n.get('name')==spec['mesh'] and i in world]
 else:
  root=next(i for i,n in enumerate(doc['nodes']) if n.get('name')==spec['root']);ids=[i for i in descendants(root) if 'mesh' in doc['nodes'][i]]
 assert ids,spec
 for i in ids:
  node=doc['nodes'][i];oldmesh=node['mesh'];mesh=copy.deepcopy(doc['meshes'][oldmesh]);mesh['name']=mesh.get('name',node['name'])+' — layout v3';M=Cinv@world[i];inv=np.linalg.inv(M);maxdisp=0;minjac=1
  for prim in mesh['primitives']:
   attrs=prim['attributes'];p=values(attrs['POSITION']);wp=p@M[:3,:3].T+M[:3,3];adjusted,J=field(wp,spec);local=(adjusted-M[:3,3])@inv[:3,:3].T
   attrs['POSITION']=attribute(local,True);localJ=np.einsum('ij,njk,kl->nil',inv[:3,:3],J,M[:3,:3])
   normal=values(attrs['NORMAL']);normal=np.einsum('nij,nj->ni',np.linalg.inv(localJ).transpose(0,2,1),normal);normal/=np.linalg.norm(normal,axis=1)[:,None];attrs['NORMAL']=attribute(normal)
   if 'TANGENT' in attrs:
    tangent=values(attrs['TANGENT']);t=np.einsum('nij,nj->ni',localJ,tangent[:,:3]);t-=normal*np.sum(t*normal,axis=1)[:,None];t/=np.linalg.norm(t,axis=1)[:,None];attrs['TANGENT']=attribute(np.column_stack((t,tangent[:,3])))
   # Inherited quantized zero-area triangles are omitted from the fitted primitive only.
   index=values(prim['indices']).astype(int).reshape(-1,3)
   def areas(vertices):
    a,b,c=vertices[index[:,0]],vertices[index[:,1]],vertices[index[:,2]]
    return .5*np.linalg.norm(np.cross(b-a,c-a),axis=1)
   area=areas(local);keep=area>1e-15
   if not keep.all():
    assert np.all(areas(p)[~keep]<=1e-15),'Fitting collapsed a previously valid triangle'
    while len(blob)%4:blob.append(0)
    filtered=index[keep].reshape(-1).astype('<u4');start=len(blob);blob.extend(filtered.tobytes());view=len(doc['bufferViews']);doc['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':filtered.nbytes,'target':34963});accessor=len(doc['accessors']);doc['accessors'].append({'bufferView':view,'componentType':5125,'count':len(filtered),'type':'SCALAR','min':[int(filtered.min())],'max':[int(filtered.max())]});oldindex=prim['indices'];prim['indices']=accessor
    cleaned.append({'name':node['name'],'old_indices':oldindex,'new_indices':accessor,'removed_triangles':np.flatnonzero(~keep).tolist(),'all_already_zero_area_in_input':True})
   maxdisp=max(maxdisp,float(np.linalg.norm(adjusted-wp,axis=1).max()));minjac=min(minjac,float(np.linalg.det(J).min()))
  node['mesh']=len(doc['meshes']);doc['meshes'].append(mesh);fitted.append({'node':i,'name':node['name'],'original_mesh':oldmesh,'new_mesh':node['mesh'],'max_displacement_m':maxdisp,'minimum_jacobian':minjac})
doc['buffers']=[{'byteLength':len(blob)}]
path=OUT/'motorcycle-layout.glb';path.write_bytes(encode(doc,bytes(blob)))
(REV/'composition-check.json').write_text(json.dumps({'source_sha256':hashlib.sha256((ROOT/plan['source_glb']).read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'wrappers':rows,'fitted_connections':fitted,'inherited_zero_area_cleanup':cleaned,'original_binary_preserved':True,'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n');print('LAYOUT_COMPOSED',len(rows))
