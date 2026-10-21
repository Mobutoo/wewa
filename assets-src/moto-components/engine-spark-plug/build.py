"""Original installed plug exterior, conditional representative Champion family.
Nominal hidden insertion is plain: no unsupported electrode or thread mechanism.
"""
from pathlib import Path
import bpy,bmesh,json,hashlib,math,sys
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-spark-plug-v1';P=json.loads((H/'parameters.json').read_text());sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import material,mesh_object,check_mesh,tree_world,export,studio
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(R/P['head_source'])==P['head_sha256'];bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
coll=bpy.data.collections.new('WEWA_ENGINE_SPARK_PLUG_EXTERIOR');s.collection.children.link(coll);guides=bpy.data.collections.new('SPARK_PLUG_IMMUTABLE_HEAD_GUIDE');s.collection.children.link(guides);stage=bpy.data.collections.new('SPARK_PLUG_STUDIO_NOT_EXPORTED');s.collection.children.link(stage)
with bpy.data.libraries.load(str(R/P['head_source']),link=True)as(a,l):l.objects=['Engine head base provisional datum','Engine UG5 head hollow exterior casting - editable candidate']
for o in l.objects:guides.objects.link(o)
head=next(o for o in l.objects if o.type=='MESH');headroot=next(o for o in l.objects if o.type=='EMPTY');bpy.context.view_layer.update();axis=Vector(P['outward_head_axis']).normalized();U=Vector((0,1,0));V=axis.cross(U).normalized();centre=Vector(P['head_seat_m'])+axis*P['seat_candidate_axial_offset_m'];datum=bpy.data.objects.new('Spark plug inherited estimated seat datum',None);coll.objects.link(datum);datum.matrix_world=headroot.matrix_world@Matrix(((axis.x,U.x,V.x,centre.x),(axis.y,U.y,V.y,centre.y),(axis.z,U.z,V.z,centre.z),(0,0,0,1)))
metal=material('Original estimated plug metal plating',(.52,.49,.42),1,.25);ceramic=material('Original unmarked white glazed ceramic',(.82,.80,.74),0,.19);washermat=material('Original estimated seat washer metal',(.34,.35,.36),1,.30)
def revolve(name,profile,mat,hexshape=False):
 if hexshape:
  # True rounded regular hex with16mm across flats, corner radius estimated.
  a=P['hex_across_flats_m']/2;r=P['hex_corner_radius_m'];core=(a-r)/math.cos(math.pi/6);contour=[]
  for k in range(6):
   angle=math.pi/6+k*math.pi/3;C=Vector((core*math.cos(angle),core*math.sin(angle)))
   for j in range(13):
    t=angle-math.pi/6+math.pi/3*j/12;contour.append(C+Vector((r*math.cos(t),r*math.sin(t))))
  # Densify long flats too: paired circular inner rings must not bridge
  # a large angular gap as chords and intrude into the ceramic.
  dense=[]
  for start,end in zip(contour,contour[1:]+contour[:1]):
   count=max(1,math.ceil((end-start).length/.00035))
   for j in range(count):dense.append(start+(end-start)*(j/count))
  contour=dense;angles=[math.atan2(p.y,p.x)for p in contour]
 else:angles=[math.tau*j/P['angular_segments']for j in range(P['angular_segments'])];contour=None
 vv=[];ff=[];rings=[];N=len(angles)
 for x,radius,mix in profile:
  if radius==0:rings.append([len(vv)]*N);vv.append((x,0,0));continue
  ring=[]
  for j,angle in enumerate(angles):
   base=Vector((radius*math.cos(angle),radius*math.sin(angle)));p=base.normalized()*min(radius,contour[j].length) if contour and mix else base;ring.append(len(vv));vv.append((x,p.x,p.y))
  rings.append(ring)
 for k in range(len(rings)):
  q=(k+1)%len(rings)
  for j in range(N):
   m=(j+1)%N;face=list(dict.fromkeys([rings[k][j],rings[k][m],rings[q][m],rings[q][j]]))
   if len(face)>=3:ff.append(face)
 o=mesh_object(name,vv,ff,coll,mat);o.parent=datum
 for face in o.data.polygons:
  if abs(abs(face.normal.x)-1)<1e-7:face.use_smooth=False
  if hexshape and .00819<face.center.x<.01261 and abs(face.normal.x)<1e-6:
   # A full machined flat keeps its actual plane normal. Rounded corners smooth.
   radial=Vector((face.center.y,face.center.z));normal=Vector((face.normal.y,face.normal.z))
   if any(abs(radial.dot(Vector((math.cos(k*math.pi/3),math.sin(k*math.pi/3))))-P['hex_across_flats_m']/2)<1e-7 for k in range(6)):face.use_smooth=False
 return o
# Metal shell, rounded hex and rolled shoulders, concealed plain insertion.
outer=[(-.0125,.00485,0),(-.01235,.005,0),(.0009,.005,0),(.00105,.005,0),(.00125,.0078,0),(.00145,.008,0),(.0047,.008,0),(.0049,.00775,0),(.0051,.0076,0),(.0054,.0076,0),(.0056,.00785,0),(.0063,.00785,0),(.0066,.0078,0),(.0070,.0078,0)]
# A conical chamfer cuts only the corners near the16mmAF flats;
# the top ends at a planar annulus, rather than collapsing all six corners
# toward the ceramic neck as a pinched loft.
outer +=[(.0070+.0012*j/24,.0078+.0016*j/24,1)for j in range(1,25)]
outer +=[(.0126,.0094,1)]
outer +=[(.0126+.0012*j/24,.0094-.0014*j/24,1)for j in range(1,25)]
outer +=[(.0138,.0062,0),(.0140,.0061,0),(.0144,.00585,0),(.0144,.00505,0),(.0017,.00505,0),(.0014,.003,0),(-.0125,.003,0)]
body=revolve('Plug metal body rounded hex - hidden insertion plain',outer,metal,True)
# Preserve real C0 machined boundaries. No custom normal or tangent repair.
bm=bmesh.new();bm.from_mesh(body.data)
for edge in bm.edges:
 if len(edge.link_faces)==2 and edge.calc_face_angle(0)>.30:edge.smooth=False
bm.to_mesh(body.data);bm.free();body.data.update()
# Washer ring, four actual rounded section corners.
prof=[];x0=0;x1=P['washer_thickness_m'];ri=P['washer_inner_radius_m'];ro=P['washer_outer_radius_m'];rr=.0001
for cx,cr,start,end in [(x0+rr,ro-rr,math.pi,math.pi/2),(x1-rr,ro-rr,math.pi/2,0),(x1-rr,ri+rr,0,-math.pi/2),(x0+rr,ri+rr,-math.pi/2,-math.pi)]:
 for j in range(9):a=start+(end-start)*j/8;prof.append((cx+rr*math.cos(a),cr+rr*math.sin(a),0))
washer=revolve('Plug separate estimated uncompressed seat washer',prof,washermat)
# Five lower ribs follow the primary representative6995, not image62 mixed in.
profile=[(.0138,0,0),(.0138,.0048,0),(.0140,.00495,0),(.0155,.00495,0),(.0160,.0047,0),(.0172,.0047,0)]
for k in range(P['ceramic_rib_count_working']):
 for j in range(1,25):
  t=j/24;x=P['ceramic_rib_start_x_m']+(k+t)*P['ceramic_rib_pitch_m'];profile.append((x,P['ceramic_stem_radius_m']+(P['ceramic_rib_radius_m']-P['ceramic_stem_radius_m'])*math.sin(math.pi*t)**2,0))
profile +=[(.0348,.0047,0),(.0351,.0048,0),(.0358,.0048,0),(.0362,.0046,0),(.0378,.0042,0),(.0382,.0039,0),(.0386,.0038,0),(.0386,0,0)]
insulator=revolve('Plug exposed ceramic five estimated lower ribs - unmarked',profile,ceramic)
terminalprofile=[(.0387,0,0),(.0387,.0026,0),(.0390,.0028,0),(.0405,.0028,0),(.0408,.00245,0),(.0416,.00245,0),(.0419,.0027,0),(.0423,.0027,0),(.0426,.00245,0),(.0433,.00245,0),(.0437,.0029,0),(.0444,.0031,0),(.0473,.0031,0),(.0480,.0029,0),(.0490,.0026,0),(.0495,.0021,0),(.0495,0,0)]
terminal=revolve('Plug separate exposed SAE-like terminal - conditional option',terminalprofile,metal);objects=[body,washer,insulator,terminal];bpy.context.view_layer.update();geometry=[check_mesh(o)for o in objects]
for o in objects:
 o.data.calc_loop_triangles();assert all(t.area>0 for t in o.data.loop_triangles);o['art_accepted']=False;o['exact_RDC_variant_confirmed']=False
cross=[{'object':o.name,'pairs':len(tree_world(o).overlap(tree_world(head)))}for o in objects];internal=[]
for i,a in enumerate(objects):
 for b in objects[i+1:]:internal.append({'a':a.name,'b':b.name,'pairs':len(tree_world(a).overlap(tree_world(b)))})
assert not any(x['pairs']for x in cross+internal),{'head':cross,'internal':internal}
guides.hide_render=True;guides.hide_viewport=True;export(H/'engine-spark-plug-inspection.glb',[datum]+objects);points=[o.matrix_world@Vector(v)for o in objects for v in o.bound_box];target=sum(points,Vector())/len(points);studio(s,stage,target)
for o in stage.objects:
 if o.type=='MESH':o.hide_render=True
 if o.type=='LIGHT':o.data.energy*=.02
s.camera.data.clip_start=.0005;file=H/'engine-spark-plug-v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(file),compress=True);assert sha(R/P['head_source'])==P['head_sha256'];report={'component_id':P['component_id'],'revision':P['revision'],'source_sha256':sha(file),'export_sha256':sha(H/'engine-spark-plug-inspection.glb'),'geometry':geometry,'head_surface_pairs':cross,'internal_surface_pairs':internal,'datum_world_matrix':[list(r)for r in datum.matrix_world],'scope':'Installed observable exterior. Plain hidden insertion envelope at nominal linked dimensions, no helical thread or concealed electrode/electrical internals. No exact RDC claim.','dimensions_attributed_to_manufacturer_linked_image_mm':{'nominal_diameter':10,'hex_across_flats':16,'threaded_length':12.5},'rest_dimensions_estimated':True,'unresolved_retailer_reach_mm':12.7,'art_accepted':False,'physical_iphone_tested':False};(H/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');(O/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');print('SPARK_PLUG_PREFLIGHT',json.dumps(report))
