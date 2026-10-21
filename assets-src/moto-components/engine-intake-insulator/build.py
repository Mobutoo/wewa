"""One original conditional UG5 insulating spacer, photograph-led exterior.

No calibrated photo tracing, copied CAD, hidden groove or manufactured fit.
Authored round sections precede solid cuts; no global bevel on a thin result.
"""
from pathlib import Path
import bpy,bmesh,json,hashlib,math,sys
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-intake-insulator-v1'
P=json.loads((H/'parameters.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(R/P['head_source'])==P['head_sha256']
sys.path.insert(0,str(H.parent/'throttle-control'))
from control_geometry import material,mesh_object,csg,check_mesh,tree_world,export,studio
sys.path.insert(0,str(H.parent/'clutch-control'));from topology_cleanup_v2 import clean_evaluated
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
def collection(name):c=bpy.data.collections.new(name);s.collection.children.link(c);return c
parts=collection('WEWA_ENGINE_INTAKE_INSULATOR');construction=collection('INTAKE_INSULATOR_RETAINED_CONSTRUCTION')
guides=collection('INTAKE_INSULATOR_IMMUTABLE_HEAD_GUIDE');stage=collection('INTAKE_INSULATOR_STUDIO_NOT_EXPORTED')
paint=material('Original estimated dark insulating substrate - unmeasured',P['material_original']['linear_base_color'],0,P['material_original']['roughness'])
def outline():
    controls=[Vector(q)for q in P['outline_controls_uv_m']];out=[]
    for i,a in enumerate(controls):
        p0=controls[(i-1)%len(controls)];p1=a;p2=controls[(i+1)%len(controls)];p3=controls[(i+2)%len(controls)]
        for j in range(P['outline_samples_per_span']):
            t=j/P['outline_samples_per_span'];out.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
    assert sum(out[i].x*out[(i+1)%len(out)].y-out[(i+1)%len(out)].x*out[i].y for i in range(len(out)))>0
    return out
contour=outline();N=len(contour)
def inset(distance):
    result=[]
    for i,p in enumerate(contour):
        tangent=(contour[(i+1)%N]-contour[(i-1)%N]).normalized()
        result.append(p+Vector((-tangent.y,tangent.x))*distance)
    return result
thickness=P['estimated_body_thickness_m'];r=P['estimated_outer_edge_round_m']
sections=[]
for k in range(17):
    a=math.pi/2*k/16;sections.append((r*(1-math.cos(a)),r*(1-math.sin(a))))
sections.append((thickness-r,0.))
for k in range(1,17):
    a=math.pi/2*k/16;sections.append((thickness-r+r*math.sin(a),r*(1-math.cos(a))))
v=[];f=[]
for z,d in sections:v.extend((q.x,q.y,z)for q in inset(d))
for j in range(len(sections)-1):
    for i in range(N):f.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
f.append(tuple(reversed(range(N))));f.append(tuple((len(sections)-1)*N+i for i in range(N)))
body=mesh_object('Original asymmetric spacer outline with authored edge rounds',v,f,construction,paint)
def revolve(name,section,centre=(0,0),n=128):
    verts=[];faces=[];rings=[]
    for z,rad in section:
        if rad==0:rings.append([len(verts)]*n);verts.append((centre[0],centre[1],z))
        else:
            rings.append(list(range(len(verts),len(verts)+n)))
            verts.extend((centre[0]+rad*math.cos(math.tau*i/n),centre[1]+rad*math.sin(math.tau*i/n),z)for i in range(n))
    for j in range(len(section)):
        for i in range(n):
            face=list(dict.fromkeys([rings[j][i],rings[j][(i+1)%n],rings[(j+1)%len(section)][(i+1)%n],rings[(j+1)%len(section)][i]]))
            if len(face)>=3:faces.append(face)
    return mesh_object(name,verts,faces,construction)
def bore(name,radius,centre,n):
    edge=P['working_entry_round_m'];profile=[(-.005,0),(-.005,radius+edge),(0,radius+edge)]
    for k in range(1,17):
        a=math.pi/2*k/16;profile.append((edge*(1-math.cos(a)),radius+edge*(1-math.sin(a))))
    profile.append((thickness-edge,radius))
    for k in range(1,17):
        a=math.pi/2*k/16;profile.append((thickness-edge+edge*math.sin(a),radius+edge*(1-math.cos(a))))
    profile.extend([(thickness+.005,radius+edge),(thickness+.005,0)])
    return revolve(name,profile,centre,n)
half=P['working_bolt_pitch_m']/2
drills=[bore('Through gas mouth with estimated entry rounds',P['working_bore_radius_m'],(0,0),192)]
for sign in [-1,1]:drills.append(bore('True bolt opening '+str(sign),P['working_bolt_bore_radius_m'],(sign*half,0),128))
centre=P['working_visible_front_groove_centre_radius_m'];width=P['working_visible_front_groove_width_m'];lo=centre-width/2;hi=centre+width/2
bottom=thickness-P['working_visible_front_groove_depth_m'];rr=P['working_groove_bottom_round_m'];section=[(thickness+.002,lo),(bottom+rr,lo)]
for k in range(1,17):
    a=math.pi/2*k/16;section.append((bottom+rr-rr*math.sin(a),lo+rr*(1-math.cos(a))))
section.append((bottom,hi-rr))
for k in range(1,17):
    a=math.pi/2*k/16;section.append((bottom+rr*(1-math.cos(a)),hi-rr+rr*math.sin(a)))
section.append((thickness+.002,hi));drills.append(revolve('Visible annular face groove - rounded bottom only',section,n=256))
for i,xy in enumerate(P['working_shallow_front_witness_marks_uv_m']):
    depth=P['working_front_witness_depth_m'];radius=P['working_front_witness_radius_m'];rr=.00006;z=thickness-depth
    profile=[(z,0),(z,radius-rr)]
    for k in range(1,13):
        a=math.pi/2*k/12;profile.append((z+rr*(1-math.cos(a)),radius-rr+rr*math.sin(a)))
    profile.extend([(thickness+.002,radius),(thickness+.002,0)])
    drills.append(revolve('Closed shallow mould witness - function unknown '+str(i+1),profile,xy,96))
bpy.context.view_layer.update();body,ops=csg(body,[],drills,parts,paint,R,'Intake insulating spacer exterior - conditional UG5')
cleanup=clean_evaluated(body,construction);body.modifiers.clear()
bpy.context.view_layer.objects.active=body;body.hide_set(False);body.select_set(True)
bpy.ops.mesh.customdata_custom_splitnormals_clear();m=body.data;m.update()
flat_levels=[0,thickness,bottom,thickness-P['working_front_witness_depth_m']]
for face in m.polygons:
    zz=[m.vertices[i].co.z for i in face.vertices]
    plane=any(max(abs(z-level)for z in zz)<1e-8 for level in flat_levels)
    face.use_smooth=not plane
bm=bmesh.new();bm.from_mesh(m)
for edge in bm.edges:
    if len(edge.link_faces)==2 and edge.calc_face_angle()>math.radians(45):edge.smooth=False
bm.to_mesh(m);bm.free();m.update();pre=check_mesh(body)
assert not any(t.area==0 for t in (m.calc_loop_triangles()or m.loop_triangles))
with bpy.data.libraries.load(str(R/P['head_source']),link=True)as(a,l):l.objects=['Engine head base provisional datum','Engine UG5 head hollow exterior casting - editable candidate']
for obj in l.objects:guides.objects.link(obj)
head=next(obj for obj in l.objects if obj.type=='MESH');headroot=head.parent;guides.hide_viewport=False;bpy.context.view_layer.update()
u=Vector((.022,0,-.012)).normalized();w=Vector((0,1,0));vv=w.cross(u)
point=Vector(P['conditional_head_port_centre_local_m']);point.y=P['conditional_head_machined_face_y_m']+P['working_unfilled_rear_gap_m']
local=Matrix(((u.x,vv.x,w.x,point.x),(u.y,vv.y,w.y,point.y),(u.z,vv.z,w.z,point.z),(0,0,0,1)))
datum=bpy.data.objects.new('Intake insulator provisional rear seating datum',None);parts.objects.link(datum);datum.matrix_world=headroot.matrix_world@local;body.parent=datum;bpy.context.view_layer.update()
cross=len(tree_world(body).overlap(tree_world(head)));assert cross==0,('Conditional candidate/head surfaces cross',cross)
geometry=[check_mesh(body)];construction.hide_render=True;construction.hide_viewport=True;guides.hide_render=True;guides.hide_viewport=True
export(H/'engine-intake-insulator-inspection.glb',[datum,body]);target=body.matrix_world@Vector((0,0,thickness/2));studio(s,stage,target)
for obj in stage.objects:
    if obj.type=='MESH':obj.hide_render=True
    if obj.type=='LIGHT':obj.data.energy*=.02
s.camera.data.clip_start=.0005;file=H/'engine-intake-insulator-v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(file),compress=True)
for lib in bpy.data.libraries:
    if lib.parent is None:lib.filepath=bpy.path.relpath(bpy.path.abspath(lib.filepath),start=str(H))
bpy.ops.wm.save_as_mainfile(filepath=str(file),compress=True,relative_remap=False)
report={'component_id':P['component_id'],'revision':P['revision'],'source_sha256':sha(file),'export_sha256':sha(H/'engine-intake-insulator-inspection.glb'),
        'collection':parts.name,'root':datum.name,'geometry':geometry,'cleanup':cleanup,'CSG':{k:v for k,v in ops.items()if k not in ['vertices','triangles']},'contour_samples':N,'authored_round_sections':len(sections),
        'conditional_surface_crossings_with_head3':cross,'head_source_sha256':P['head_sha256'],'datum_world_matrix':[list(row)for row in datum.matrix_world],
        'flat_back_is_photographed':False,'back_groove_fabricated':False,'O_rings_fabricated':False,'material_measured':False,
        'witness_marks_are_through_ports':False,'all_dimensions_estimated':True,'art_accepted':False,'physical_iphone_tested':False}
(H/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');(O/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n')
assert sha(R/P['head_source'])==P['head_sha256'];print('INTAKE_INSULATOR',json.dumps(report))
