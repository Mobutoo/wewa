"""Original bounded RH stalk and seat contact-skin surfaces; no imported meshes."""
import math
from collections import Counter
import numpy as np
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt


def smooth(t):
    return 6 * t**5 - 15 * t**4 + 10 * t**3


def dsmooth(t):
    return 30 * t*t * (t - 1)**2


def right_stalk(p):
    def blend(x, a, b, ra, rb):
        t = min(1., max(0., (x-a)/(b-a)))
        return ra+(rb-ra)*smooth(t), (rb-ra)*dsmooth(t)/(b-a)

    def radius(x):
        body, shoulder, neck, end = [p[k] for k in ('main_body', 'shoulder', 'neck', 'head_stub')]
        if x <= body['end_m']:
            return blend(x, body['start_m'], body['end_m'], body['radius_start_m'], body['radius_end_m'])
        if x <= shoulder['end_m']:
            return blend(x, shoulder['start_m'], shoulder['end_m'], body['radius_end_m'], shoulder['end_radius_m'])
        if x >= end['start_m']:
            return blend(x, end['start_m'], end['end_m'], neck['radius_m'], end['end_radius_m'])
        r, derivative = neck['radius_m'], 0.
        for g in p['grooves']:
            delta = x-g['center_m']; a = abs(delta)
            lo, hi = g['flat_half_width_m'], g['half_width_m']
            if a <= lo:
                r -= g['depth_m']
            elif a < hi:
                t = (a-lo)/(hi-lo)
                r -= g['depth_m']*(1-smooth(t))
                derivative += g['depth_m']*dsmooth(t)/(hi-lo)*(1 if delta > 0 else -1)
        return r, derivative

    rings = []
    flare = p['root_flare']
    for k in range(flare['quarter_segments']+1):
        a = math.pi*k/(2*flare['quarter_segments'])
        x = flare['length_m']*(1-math.cos(a))
        r = flare['start_radius_m']+(flare['end_radius_m']-flare['start_radius_m'])*math.sin(a)
        tx = flare['length_m']*math.sin(a)
        tr = (flare['end_radius_m']-flare['start_radius_m'])*math.cos(a)
        rings.append((x, r, tx, tr))
    for key in ('main_body', 'shoulder', 'neck', 'head_stub'):
        section = p[key]; a, b = section['start_m'], section['end_m']
        count = section.get('samples', math.ceil((b-a)/section.get('axial_sample_m', .0001)))
        xs = {a+(b-a)*i/count for i in range(count+1)}
        if key == 'neck':
            for g in p['grooves']:
                for d in (-g['half_width_m'], -g['flat_half_width_m'], 0,
                          g['flat_half_width_m'], g['half_width_m']):
                    xs.add(g['center_m']+d)
        for x in sorted(xs):
            if abs(x-rings[-1][0]) < 1e-12:
                continue
            assert x > rings[-1][0]
            r, derivative = radius(x)
            rings.append((x, r, 1., derivative))
    n = p['radial_segments']; vertices, normals, faces, uv = [], [], [], []
    for x, r, tx, tr in rings:
        assert r > 0
        for k in range(n):
            a = 2*math.pi*k/n
            vertices.append((x, r*math.cos(a), r*math.sin(a)))
            normals.append(tuple(Vector((-tr, tx*math.cos(a), tx*math.sin(a))).normalized()))
    for i in range(len(rings)-1):
        for k in range(n):
            a, b = i*n+k, i*n+(k+1)%n
            c, d = (i+1)*n+(k+1)%n, (i+1)*n+k
            u0, u1, v0, v1 = k/n, (k+1)/n, rings[i][0]/rings[-1][0], rings[i+1][0]/rings[-1][0]
            faces.extend([(a, b, c), (a, c, d)])
            uv.extend([[(u0,v0),(u1,v0),(u1,v1)], [(u0,v0),(u1,v1),(u0,v1)]])
    return vertices, normals, faces, uv, {'expected_boundary_loops': [n,n],
        'scope': 'Independent PF401002-referenced exterior stalk skin; two covered interface cuts, no peg/bore.',
        'guard': 'Strictly increasing axis and positive radius; one revolution skin, no reflected source mesh.',
        'profile': rings}


def seat_damper(p):
    hx, hy = p['half_face_size_XY_m']; lip = p['outer_lip_radius_m']
    rcorner = p['outer_corner_radius_m']-lip
    outer, outer_normals = [], []
    for cx, cy, start in [(hx-lip-rcorner,hy-lip-rcorner,0),
                           (-hx+lip+rcorner,hy-lip-rcorner,90),
                           (-hx+lip+rcorner,-hy+lip+rcorner,180),
                           (hx-lip-rcorner,-hy+lip+rcorner,270)]:
        for k in range(p['outer_quarter_segments']+1):
            a = math.radians(start+90*k/p['outer_quarter_segments'])
            outer.append((cx+rcorner*math.cos(a),cy+rcorner*math.sin(a)))
            outer_normals.append((math.cos(a),math.sin(a)))
    # Straight top/bottom edges also cross all five grooves. Corner-only
    # contour samples would bridge their valleys with a long flat triangle.
    dense_outer, dense_normals = [], []
    for i,q in enumerate(outer):
        following=outer[(i+1)%len(outer)];normal=outer_normals[i]
        count=max(1,math.ceil(math.dist(q,following)/.000075))
        for k in range(count):
            t=k/count
            dense_outer.append(tuple((1-t)*q[j]+t*following[j]for j in range(2)))
            n=Vector(tuple((1-t)*normal[j]+t*outer_normals[(i+1)%len(outer)][j]for j in range(2))).normalized()
            dense_normals.append(tuple(n))
    outer,outer_normals=dense_outer,dense_normals
    hole_face_r = p['hole_radius_m']+p['hole_lip_radius_m']
    hole = [(hole_face_r*math.cos(2*math.pi*k/p['circular_segments']),
             hole_face_r*math.sin(2*math.pi*k/p['circular_segments']))
            for k in range(p['circular_segments'])]

    def height(x):
        z, derivative = 0., 0.
        for c in p['groove_centers_X_m']:
            delta = x-c; a = abs(delta)
            lo, hi = p['groove_flat_half_width_m'],p['groove_half_width_m']
            if a <= lo:
                z -= p['groove_depth_m']
            elif a < hi:
                t=(a-lo)/(hi-lo)
                z -= p['groove_depth_m']*(1-smooth(t))
                derivative += p['groove_depth_m']*dsmooth(t)/(hi-lo)*(1 if delta>0 else -1)
        return z, derivative

    def inside(q):
        x,y=q; dx=max(abs(x)-(hx-lip-rcorner),0);dy=max(abs(y)-(hy-lip-rcorner),0)
        return (abs(x)<hx-lip and abs(y)<hy-lip and dx*dx+dy*dy<rcorner*rcorner
                and x*x+y*y>hole_face_r*hole_face_r)

    points=list(outer)+hole; edges=[]
    for offset, loop in [(0,outer),(len(outer),hole)]:
        edges.extend((offset+i,offset+(i+1)%len(loop)) for i in range(len(loop)))
    ys=np.arange(-hy+lip+.00013,hy-lip,p['face_grid_step_m'])
    xs=set(np.arange(-hx+lip+.00017,hx-lip,p['face_grid_step_m']))
    for c in p['groove_centers_X_m']:
        for i in range(p['groove_profile_samples']+1):
            xs.add(c-p['groove_half_width_m']+2*p['groove_half_width_m']*i/p['groove_profile_samples'])
        for delta in (-p['groove_flat_half_width_m'],0,p['groove_flat_half_width_m']):xs.add(c+delta)
    used={tuple(round(float(x),10) for x in q) for q in points}
    for x in sorted(xs):
        for y in ys:
            q=(float(x),float(y));key=tuple(round(v,10)for v in q)
            if inside(q) and math.hypot(*q)>hole_face_r+.00007 and key not in used:
                points.append(q);used.add(key)
    step=p.get('face_hole_refinement_step_m',.0001)
    local=np.arange(-hole_face_r-.0012,hole_face_r+.0012,step)
    for x in local:
        for y in local:
            q=(float(x),float(y));radius=math.hypot(*q)
            key=tuple(round(v,10)for v in q)
            if hole_face_r+.000015<radius<hole_face_r+.0012 and inside(q) and key not in used:
                points.append(q);used.add(key)
    coords,_,triangles,*_=delaunay_2d_cdt([Vector(q)for q in points],edges,
                                        [list(range(len(outer)))],1,p['CDT_epsilon_m'],False)
    xy=[tuple(q)for q in coords]; top=[]
    for triangle in triangles:
        assert len(triangle)==3
        center=tuple(sum(xy[i][j]for i in triangle)/3 for j in range(2))
        if inside(center):top.append(tuple(triangle))
    active=sorted({i for t in top for i in t});remap={k:i for i,k in enumerate(active)}
    xy=[xy[k]for k in active];top=[tuple(remap[i]for i in t)for t in top]
    vertices=[(x,y,height(x)[0])for x,y in xy]
    normals=[tuple(Vector((-height(x)[1],0,1)).normalized())for x,y in xy]
    faces=[];uv=[]

    def triangle(ids, tex):
        ids=list(ids);tex=list(tex)
        a,b,c=[Vector(vertices[i])for i in ids]
        if (b-a).cross(c-a).dot(Vector(normals[ids[0]]))<0:
            ids[1],ids[2]=ids[2],ids[1];tex[1],tex[2]=tex[2],tex[1]
        faces.append(tuple(ids));uv.append(tex)
    for t in top:triangle(t,[(xy[i][0]/.01,xy[i][1]/.01)for i in t])
    lookup={tuple(round(v,8)for v in q):i for i,q in enumerate(xy)}
    def find(q):
        key=tuple(round(v,8)for v in q)
        if key in lookup:return lookup[key]
        i=min(range(len(xy)),key=lambda j:(xy[j][0]-q[0])**2+(xy[j][1]-q[1])**2)
        assert math.dist(q,xy[i])<2e-7,(q,xy[i])
        return i

    for loop,radials,b,inward in [(outer,outer_normals,lip,False),
            (hole,[(math.cos(2*math.pi*k/len(hole)),math.sin(2*math.pi*k/len(hole)))for k in range(len(hole))],p['hole_lip_radius_m'],True)]:
        count=len(loop);previous=[find(q)for q in loop];profile_v=0.
        for j in range(1,p['lip_quarter_segments']+5):
            is_arc=j<=p['lip_quarter_segments']
            phi=min(j,p['lip_quarter_segments'])*math.pi/(2*p['lip_quarter_segments'])
            sign=-1 if inward else 1
            positions=[]; derivatives=[]
            for (x,y),(nx,ny) in zip(loop,radials):
                xx=x+sign*b*math.sin(phi)*nx;yy=y+sign*b*math.sin(phi)*ny
                z,dz=height(xx);z+=b*(math.cos(phi)-1)
                if is_arc:
                    derivative=Vector((sign*b*math.cos(phi)*nx,sign*b*math.cos(phi)*ny,
                                       dz*sign*b*math.cos(phi)*nx-b*math.sin(phi)))
                else:
                    t=(j-p['lip_quarter_segments'])/4
                    z=(1-t)*z-t*p['inspection_side_depth_m'];derivative=Vector((0,0,-1))
                positions.append(Vector((xx,yy,z)));derivatives.append(derivative)
            ids=[]
            for k,pos in enumerate(positions):
                tangent=positions[(k+1)%count]-positions[k-1]
                normal=(tangent.cross(derivatives[k])if inward else derivatives[k].cross(tangent)).normalized()
                assert normal.length>.99
                ids.append(len(vertices));vertices.append(tuple(pos));normals.append(tuple(normal))
            new_v=(b*phi if is_arc else b*math.pi/2+(j-p['lip_quarter_segments'])*p['inspection_side_depth_m']/4)
            for k in range(count):
                nxt=(k+1)%count;u0,u1=k/count,(k+1)/count
                triangle((previous[k],previous[nxt],ids[nxt]),[(u0,profile_v/.01),(u1,profile_v/.01),(u1,new_v/.01)])
                triangle((previous[k],ids[nxt],ids[k]),[(u0,profile_v/.01),(u1,new_v/.01),(u0,new_v/.01)])
            previous=ids;profile_v=new_v
    counts=Counter(tuple(sorted((a,b)))for f in faces for a,b in zip(f,f[1:]+f[:1]))
    assert all(n in(1,2)for n in counts.values())
    assert sum(n==1 for n in counts.values())==len(outer)+len(hole)
    return vertices,normals,faces,uv,{'expected_boundary_loops':[len(outer),len(hole)],
        'scope':'One contact face with five C2 valleys, rounded outside lip and mouth, two truncated review walls; no hidden back/peg/cavity bottom.',
        'guard':'Constrained face domain with explicit hole, single-valued authored height, original rounded lip continuations. No global self-intersection certification.',
        'face_domain_triangles':len(top),'face_area_xy_m2':sum(abs((xy[t[1]][0]-xy[t[0]][0])*(xy[t[2]][1]-xy[t[0]][1])-(xy[t[1]][1]-xy[t[0]][1])*(xy[t[2]][0]-xy[t[0]][0]))/2 for t in top)}
