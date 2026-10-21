"""Actual GLB buffer/transform rays vs separately extracted native inspections.

No exported buffer repair, no source mutation, no broad fidelity/fit claim.
Requires numpy only. Uncompressed float32 meshes are intentionally the scope.
"""
from pathlib import Path
import hashlib,json,struct,math,time
import numpy as np
D=Path(__file__).resolve().parent;R=D.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
TYPES={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
DT={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'}

def readglb(p):
    data=p.read_bytes();assert data[:4]==b'glTF' and struct.unpack_from('<I',data,4)[0]==2
    offset=12;doc=None;binary=None
    while offset<len(data):
        n,kind=struct.unpack_from('<II',data,offset);chunk=data[offset+8:offset+8+n];offset+=8+n
        if kind==0x4e4f534a:doc=json.loads(chunk)
        elif kind==0x004e4942:binary=chunk
    assert doc and binary is not None
    def accessor(i):
        a=doc['accessors'][i];assert 'sparse'not in a and not a.get('normalized',False)
        b=doc['bufferViews'][a['bufferView']];assert b.get('buffer',0)==0
        dtype=np.dtype(DT[a['componentType']]);width=TYPES[a['type']]
        stride=b.get('byteStride',dtype.itemsize*width)
        return np.ndarray((a['count'],width),dtype=dtype,buffer=binary,
          offset=b.get('byteOffset',0)+a.get('byteOffset',0),strides=(stride,dtype.itemsize)).copy()
    def local(n):
        if 'matrix'in n:return np.array(n['matrix'],dtype=np.float64).reshape(4,4).T
        x,y,z,w=n.get('rotation',[0,0,0,1]);rotation=np.array([
         [1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
         [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
         [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
        m=np.eye(4);m[:3,:3]=rotation@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0]);return m
    positions=[];triangles=[];primitives=[];count=0
    def visit(i,parent):
        nonlocal count
        node=doc['nodes'][i];matrix=parent@local(node)
        if 'mesh'in node:
            for primitive in doc['meshes'][node['mesh']]['primitives']:
                assert primitive.get('mode',4)==4 and not primitive.get('extensions',{})
                v=accessor(primitive['attributes']['POSITION']).astype(np.float64)
                v=v@matrix[:3,:3].T+matrix[:3,3]
                # glTF world +Yup/-Zfront -> native Blender +Zup/+Yrear.
                v=v[:,[0,2,1]]*np.array([1.,-1.,1.])
                ix=accessor(primitive['indices']).ravel().reshape(-1,3).astype(np.int64)
                positions.append(v);triangles.append(ix+count)
                primitives.append({'node':node.get('name',str(i)),'vertices':len(v),'triangles':len(ix),'material':primitive.get('material')})
                count+=len(v)
        for j in node.get('children',[]):visit(j,matrix)
    for i in doc['scenes'][doc.get('scene',0)]['nodes']:visit(i,np.eye(4))
    return np.vstack(positions),np.vstack(triangles),primitives

def stations(v,tri,y,z):
    a=v[tri[:,0]];e1=v[tri[:,1]]-a;e2=v[tri[:,2]]-a
    direction=np.array([1.,0.,0.]);origin=np.array([-.20,y,z]);h=np.cross(np.broadcast_to(direction,e2.shape),e2)
    det=np.einsum('ij,ij->i',e1,h);good=np.abs(det)>1e-16;inv=np.divide(1.,det,out=np.zeros_like(det),where=good)
    s=origin-a;u=inv*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1);w=inv*q[:,0];t=inv*np.einsum('ij,ij->i',e2,q)
    hits=np.sort(t[good&(u>=-1e-8)&(w>=-1e-8)&(u+w<=1+1e-8)&(t>=0)&(t<=.4)]-.20)
    unique=[]
    for x in hits:
        if not unique or x-unique[-1]>1e-6:unique.append(float(x))
    return unique

source=D/'source-inspection-surface-read-v1.json';native=json.loads(source.read_text())
out={'schema':1,'time_UTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'script_sha256':sha(Path(__file__)),
 'native_extraction_report_sha256':sha(source),'scope':'Sparse actual GLB surface-ray comparison to source inspection copies; full detailed master/reduced GLB Hausdorff, material equality and installed contacts NOT tested.',
 'comparison_tolerance_m':1e-6,'tolerance_scope':'Diagnostic ray station/float encoding comparison chosen before execution, not an OEM fabrication tolerance.',
 'rows':[],'source_or_GLB_modified':False,'installed_pose_verified':False,'art_accepted':False}
for row in native['rows']:
    p=R/row['GLB'];assert sha(p)==row['export_sha256']
    v,t,prims=readglb(p)
    # The rim GLB includes its three distinct valve components; source extract
    # intentionally reads the casting only. At central sampled radii no valve
    # is intersected; whole-object bounds are not a casting parity claim.
    details=[]
    for q in row['axial_rays']:
        hits=stations(v,t,q['y_m'],q['z_m']);a=q['x_surface_stations_m']
        same=len(hits)==len(a);delta=max([abs(x-y)for x,y in zip(a,hits)],default=0)if same else None
        details.append({'y_m':q['y_m'],'z_m':q['z_m'],'native_x_stations_m':a,'GLB_x_stations_m':hits,'same_station_count':same,'max_station_error_m':delta})
    areas=np.linalg.norm(np.cross(v[t[:,1]]-v[t[:,0]],v[t[:,2]]-v[t[:,0]]),axis=1)*.5
    z={'key':row['key'],'GLB':row['GLB'],'export_sha256':sha(p),'primitives':prims,'actual_vertices':len(v),'actual_triangles':len(t),
     'bounds_native_Blender_m':{'min':v.min(axis=0).tolist(),'max':v.max(axis=0).tolist()},'rays':details,
     'all_sampled_station_counts_match':all(q['same_station_count']for q in details),
     'all_sampled_station_errors_within_1um':all(q['same_station_count']and q['max_station_error_m']<=1e-6 for q in details),
     'min_triangle_area_m2':float(areas.min()),'triangles_area_at_or_below_1e18_m2':int((areas<=1e-18).sum()),
     'all_buffers_unchanged':sha(p)==row['export_sha256']}
    out['rows'].append(z)
    print(row['key'],len(t),z['all_sampled_station_counts_match'],z['all_sampled_station_errors_within_1um'],z['triangles_area_at_or_below_1e18_m2'])
(D/'actual-GLB-ray-comparison-v1.json').write_text(json.dumps(out,indent=2)+'\n')
