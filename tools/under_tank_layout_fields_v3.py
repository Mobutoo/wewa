"""Continuous fitting fields in Blender world metres; analytic normal Jacobians."""
import numpy as np

def field(points, spec):
    points=np.asarray(points,dtype=float)
    axis=spec.get('axis',1);start,end=spec.get('interval',[0,1])
    if spec['kind']=='translation':
        return points+np.array(spec['delta']),np.broadcast_to(np.eye(3),(len(points),3,3)).copy()
    t=np.clip((points[:,axis]-start)/(end-start),0,1)
    weight=t*t*(3-2*t);gradient=6*t*(1-t)/(end-start)
    d0=np.array(spec.get('from',[0,0,0]));d1=np.array(spec['to']);delta=d1-d0
    result=points+d0+weight[:,None]*delta
    jac=np.broadcast_to(np.eye(3),(len(points),3,3)).copy();jac[:,:,axis]+=gradient[:,None]*delta
    assert np.min(np.linalg.det(jac))>.05,'Fitting field folded a surface'
    return result,jac
