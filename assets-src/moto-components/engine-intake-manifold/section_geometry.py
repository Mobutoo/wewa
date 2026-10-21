"""Original section helpers for a cast, hollow manifold; no source asset imports."""
import math
from mathutils import Vector
from control_geometry import mesh_object
def curve(controls,steps=12):
    controls=[Vector(p)for p in controls];result=[]
    for i,p1 in enumerate(controls):
        p0=controls[(i-1)%len(controls)];p2=controls[(i+1)%len(controls)];p3=controls[(i+2)%len(controls)]
        for j in range(steps):
            t=j/steps;result.append(.5*(2*p1+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
    return result
def rounded_plate(name,contour,thickness,radius,collection,material):
    count=len(contour);sections=[]
    for i in range(17):
        a=math.pi/2*i/16;sections.append((radius*(1-math.cos(a)),radius*(1-math.sin(a))))
    sections.append((thickness-radius,0.))
    for i in range(1,17):
        a=math.pi/2*i/16;sections.append((thickness-radius+radius*math.sin(a),radius*(1-math.cos(a))))
    vertices=[];faces=[]
    for z,inset in sections:
        for i,p in enumerate(contour):
            t=(contour[(i+1)%count]-contour[(i-1)%count]).normalized();q=p+Vector((-t.y,t.x))*inset;vertices.append((q.x,q.y,z))
    for j in range(len(sections)-1):
        for i in range(count):faces.append((j*count+i,j*count+(i+1)%count,(j+1)*count+(i+1)%count,(j+1)*count+i))
    faces.append(tuple(reversed(range(count))));faces.append(tuple((len(sections)-1)*count+i for i in range(count)))
    return mesh_object(name,vertices,faces,collection,material)
def revolve_z(name,section,collection,material=None,centre=(0,0),segments=192):
    vertices=[];faces=[];rings=[]
    for z,r in section:
        if r==0:rings.append([len(vertices)]*segments);vertices.append((*centre,z))
        else:
            rings.append(list(range(len(vertices),len(vertices)+segments)))
            vertices.extend((centre[0]+r*math.cos(math.tau*i/segments),centre[1]+r*math.sin(math.tau*i/segments),z)for i in range(segments))
    for j in range(len(section)):
        for i in range(segments):
            f=list(dict.fromkeys([rings[j][i],rings[j][(i+1)%segments],rings[(j+1)%len(section)][(i+1)%segments],rings[(j+1)%len(section)][i]]))
            if len(f)>=3:faces.append(f)
    return mesh_object(name,vertices,faces,collection,material)
def through_bore(name,radius,thickness,edge,centre,collection,segments=128):
    section=[(-.005,0),(-.005,radius+edge),(0,radius+edge)]
    for i in range(1,17):
        a=math.pi/2*i/16;section.append((edge*(1-math.cos(a)),radius+edge*(1-math.sin(a))))
    section.append((thickness-edge,radius))
    for i in range(1,17):
        a=math.pi/2*i/16;section.append((thickness-edge+edge*math.sin(a),radius+edge*(1-math.cos(a))))
    section.extend([(thickness+.005,radius+edge),(thickness+.005,0)])
    return revolve_z(name,section,collection,centre=centre,segments=segments)
def hollow_neck(P,collection,material):
    t=P['working_base_thickness_m'];root=P['working_root_outer_radius_m'];r=P['working_root_round_radius_m'];outer=P['working_neck_outer_radius_m']
    top=P['working_neck_top_z_m'];inner=P['working_inner_radius_m']
    # True tangent root quarter-circle, from(root,t) to(root-r,t+r).
    profile=[(t-.001,root),(t,root)]+[(t+r*(1-math.cos(math.pi/2*i/32)),root-r*math.sin(math.pi/2*i/32))for i in range(1,33)]
    for centre in P['working_rib_centres_z_m']:
        half=P['working_rib_half_height_m'];profile.append((centre-half,outer))
        for j in range(1,33):
            u=j/32;profile.append((centre-half+2*half*u,outer+P['working_rib_relief_m']*math.sin(math.pi*u)**2))
    # Rounded mouth bead then flat annular top and an explicit bore entry round.
    lip=P['working_mouth_lip_outer_radius_m'];profile +=[(top-.003,outer),(top-.0018,lip),(top-.00035,lip)]
    rr=.00035
    for i in range(1,17):
        a=math.pi/2*i/16;profile.append((top-rr+rr*math.sin(a),lip-rr+rr*math.cos(a)))
    profile.append((top,inner+rr))
    for i in range(1,17):
        a=math.pi/2*i/16;profile.append((top-rr+rr*math.cos(a),inner+rr-rr*math.sin(a)))
    profile +=[(t-.001,inner)]
    return revolve_z('Authored annular cast neck three bands and rounded root',profile,collection,material,segments=256),profile

def cast_side_feature(P,collection,material):
    """Rounded tapered integral lug; hidden cross-section explicitly estimated."""
    sections=P['working_side_boss_sections_x_z_ry_rz_m'];N=96;vertices=[];rings=[];faces=[]
    for x,z,ry,rz in sections:
        if ry==0:rings.append([len(vertices)]*N);vertices.append((x,0,z))
        else:
            rings.append(list(range(len(vertices),len(vertices)+N)))
            vertices.extend((x,ry*math.cos(math.tau*i/N),z+rz*math.sin(math.tau*i/N))for i in range(N))
    faces.append(tuple(reversed(rings[0])))
    for j in range(len(rings)-1):
        for i in range(N):
            f=list(dict.fromkeys([rings[j][i],rings[j][(i+1)%N],rings[j+1][(i+1)%N],rings[j+1][i]]))
            if len(f)>2:faces.append(f)
    return mesh_object('Rounded tapered closed lateral cast feature - function unresolved',vertices,faces,collection,material)
