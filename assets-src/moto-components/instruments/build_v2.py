"""Targeted revision of the frozen instrument candidate; historical v1 untouched.
Source changes: observed USB assembly, bounded artwork footprints, warning/GEAR/
pump marks and exactly8degenerate FONT triangles. No angle or mount calibration.
"""
import bpy,bmesh,json,hashlib,math,sys,subprocess
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/instruments-v2';OUT.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(HERE));from v2_artwork_helpers import repair_zero_font,flat_polygon,filled_curve,flat_line
base=HERE/'instruments-v1.blend';base_sha=hashlib.sha256(base.read_bytes()).hexdigest();assert base_sha=='e3321cee34967f7749dbfa8650fe01c404137c55cfb5c42881363f098cb91ec0'
U=ROOT/'creative/reviews/instruments-usb-v2-material-study-r2';usb=json.loads((U/'source-geometry-check.json').read_text());read=json.loads((U/'preview-review.json').read_text());assert read['source_sha256']==usb['source_sha256']and read['passed_for_final_material_render'];usbsource=HERE/'instruments-usb-v2-material-study-r2.blend';assert hashlib.sha256(usbsource.read_bytes()).hexdigest()==usb['source_sha256'];P=json.loads((ROOT/'creative/research/instruments-v2/dial-artwork-plan.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(base));parts=bpy.data.collections['WEWA_INSTRUMENTS_SEPARATE_PARTS'];assembly=bpy.data.objects['INSTRUMENT_CLUSTER_MOUNT'];bpy.context.view_layer.update();original=list(parts.objects)
removed_names=[o.name for o in original if o.name.startswith('USB symbol ')or o.name=='USB rounded elastomer cap - closed'or o.name.startswith('Speed printed arc ')or o.name in ['Fuel pump outline','Fuel pump hose']or(o.name.startswith('Speed tick ')and int(o.name.rsplit(' ',1)[1])%20==0)]
changed=set(removed_names+['Charge warning 0','GEAR_DIGIT_4','Speed value 140','Speed value 40','Gear label'])
def signature(o):
 row={'type':o.type,'matrix':[list(r)for r in o.matrix_world],'parent':o.parent.name if o.parent else None}
 if o.type in['MESH','CURVE','FONT']:
  deps=bpy.context.evaluated_depsgraph_get();m=bpy.data.meshes.new_from_object(o.evaluated_get(deps),depsgraph=deps);row.update({'vertices':[list(v.co)for v in m.vertices],'polygons':[list(p.vertices)for p in m.polygons],'normals':[list(n.vector)for n in m.corner_normals],'UV':[[list(x.uv)for x in uv.data]for uv in m.uv_layers],'materials':[x.name for x in m.materials]});bpy.data.meshes.remove(m)
 return hashlib.sha256(json.dumps(row,separators=(',',':')).encode()).hexdigest()
protected={o.name:signature(o)for o in original if o.name not in changed};guides=bpy.data.collections.new('Instrument v2 editable artwork construction - hidden');bpy.context.scene.collection.children.link(guides);guides.hide_render=True
fonts=[repair_zero_font(n,parts,guides)for n in['Charge warning 0','GEAR_DIGIT_4','Speed value 140','Speed value 40']]
for name in removed_names:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
# Append the individually reviewed USB source, reparent its4visible objects into
# the original cluster without changing their local geometry/UV/normal buffers.
with bpy.data.libraries.load(str(usbsource),link=False)as(fr,to):to.collections=[usb['collection'],'USB original editable contour guides v2','USB original editable motif contours v2']
appended=[]
for collection in to.collections:
 bpy.context.scene.collection.children.link(collection)
 if collection.name==usb['collection']:
  oldroot=next(o for o in collection.objects if o.name.startswith('INSTRUMENT_USB_MATERIAL_STUDY_MOUNT'))
  for o in list(collection.objects):
   if o==oldroot:continue
   local=o.matrix_local.copy();collection.objects.unlink(o);parts.objects.link(o);o.parent=assembly;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=local;appended.append(o.name)
  bpy.data.objects.remove(oldroot,do_unlink=True);bpy.data.collections.remove(collection)
 else:collection.hide_render=True
white=bpy.data.materials['Dial white ink'];orange=bpy.data.materials['Dial amber orange ink'];red=bpy.data.materials['Pointer and red warning ink'];dark=bpy.data.materials['Charcoal printed dial'];new_art=[];cx=-.064;z=.02830

def polygon(name,points,material,height=z):
 area=sum(a[0]*b[1]-a[1]*b[0]for a,b in zip(points,points[1:]+points[:1]));o=flat_polygon(name,points if area>0 else list(reversed(points)),material,parts,assembly,height);new_art.append(o.name);return o

def annular(name,start,end,radius,width,material,height):
 steps=max(2,math.ceil(abs(end-start)*270/140));vertices=[]
 for i in range(steps+1):
  a=math.radians(225-(start+(end-start)*i/steps)*270/140)
  for r in[radius-width/2,radius+width/2]:vertices.append((cx+r*math.cos(a),r*math.sin(a),height))
 faces=[(2*i,2*i+2,2*i+3,2*i+1)for i in range(steps)];data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();o=bpy.data.objects.new(name,data);parts.objects.link(o);o.parent=assembly;data.materials.append(material);o['structural_closed_volume']=False;o['surface_role']='Original flat dial ink; angular layout remains working v1 convention';new_art.append(name)
for i in range(14):
 annular('Speed inner broken band v2 '+str(i),i*10+.65,(i+1)*10-.65,.0388,.00125,orange if i<11 else red,z)
for i in range(7):annular('Speed outer pale broken band v2 '+str(i),i*20+.70,(i+1)*20-.70,.0411,.00045,white,z+.000015)
for speed in range(0,141,20):
 a=math.radians(225-speed*270/140);radial=Vector((math.cos(a),math.sin(a)));tangent=Vector((-radial.y,radial.x));isred=speed>=120;outer=.0420;inner=.0350 if isred or speed==0 else .0344 if speed==20 else .0325;width=.0023 if isred else .0025;tip=.00025 if isred else .00035;shoulder=inner+.002;shape=[(outer,-width/2),(outer,width/2),(shoulder,tip*.70),(inner,tip/2),(inner,-tip/2),(shoulder,-tip*.70)];points=[]
 for r,t in shape:p=radial*r+tangent*t;points.append((cx+p.x,p.y))
 polygon('Speed major tapered ink v2 '+str(speed),points,red if isred else orange,z+.000035)
# Central exclamation: flat original stroke and dot inside the existing triangle.
def disk(name,centre,radius,material,height,segments=48):return polygon(name,[(centre[0]+radius*math.cos(i*math.tau/segments),centre[1]+radius*math.sin(i*math.tau/segments))for i in range(segments)],material,height)
polygon('Charge warning exclamation stem v2',[(-.00022,.00020),(.00022,.00020),(.00018,-.00180),(-.00018,-.00180)],red,.03220);disk('Charge warning exclamation dot v2',(0,-.00265),.00024,red,.03220)
# The native right dial reads GEAR vertically (bottom to top). Font and centre
# are retained; the orientation correction does not alter the ring/digit rig.
bpy.data.objects['Gear label'].rotation_euler.z+=math.pi/2
# Filled pump body with a true open window, a base and a separately observed hose.
cx=.064;px=cx-.023;py=0;outer=[(px-.0022,py-.0032),(px+.0020,py-.0032),(px+.0020,py+.0030),(px-.0022,py+.0030)];window=[(px-.00135,py+.0006),(px+.0011,py+.0006),(px+.0011,py+.0021),(px-.00135,py+.0021)];o=filled_curve('Fuel pump filled body with window v2',[outer,list(reversed(window))],white,parts,assembly,location=(0,0,.02828));new_art.append(o.name);polygon('Fuel pump foot v2',[(px-.0027,py-.0035),(px+.0025,py-.0035),(px+.0025,py-.0029),(px-.0027,py-.0029)],white,.02828);hose=flat_line('Fuel pump hose v2',[(px+.0020,py+.0023),(px+.0033,py+.0011),(px+.0033,py-.0018),(px+.0038,py-.0022),(px+.0043,py-.0017)],.00035,white,parts,assembly,.02828);new_art.append(hose.name)
# Keep original vector construction, evaluate the newly drawn pump only for a
# targeted exact-zero tessellation check; other historical ink stays untouched.
bpy.context.view_layer.update();new_surface_checks=[]
for name in new_art:
 o=bpy.data.objects[name];deps=bpy.context.evaluated_depsgraph_get();m=bpy.data.meshes.new_from_object(o.evaluated_get(deps),depsgraph=deps);m.calc_loop_triangles();areas=[]
 for tri in m.loop_triangles:
  a,b,c=[m.vertices[i].co for i in tri.vertices];areas.append((b-a).cross(c-a).length/2)
 assert min(areas)>0,(name,'New original ink has zero triangle; repair source tessellation before export');new_surface_checks.append({'object':name,'actual_triangles':len(areas),'min_area_m2':min(areas)});bpy.data.meshes.remove(m)
assert protected=={name:signature(bpy.data.objects[name])for name in protected},'Protected original objects changed'
# Evaluate original and added structural solids independently.
deps=bpy.context.evaluated_depsgraph_get();bodies=[]
for o in parts.objects:
 if not o.get('structural_closed_volume'):continue
 m=bpy.data.meshes.new_from_object(o.evaluated_get(deps),depsgraph=deps);bm=bmesh.new();bm.from_mesh(m);edges=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);left=set(bm.verts);connected=0
 while left:
  connected+=1;pending=[left.pop()]
  while pending:
   for edge in pending.pop().link_edges:
    for v in edge.verts:
     if v in left:left.remove(v);pending.append(v)
 bm.free();assert edges==0 and connected==1 and volume>0,(o.name,edges,connected,volume);bodies.append({'object':o.name,'non_manifold_edges':edges,'connected_components':connected,'signed_volume_m3':volume});bpy.data.meshes.remove(m)
bpy.ops.object.select_all(action='DESELECT')
for o in parts.objects:o.select_set(True)
bpy.context.view_layer.objects.active=assembly;glb=HERE/'instruments-v2-inspection.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True,export_tangents=True);subprocess.run(['node',str(HERE/'finalize_export_v2.mjs')],cwd=ROOT,check=True);path=HERE/'instruments-v2.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);assert hashlib.sha256(base.read_bytes()).hexdigest()==base_sha
report={'schema':1,'revision':'instruments-v2','source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(glb.read_bytes()).hexdigest(),'baseline_source_sha256':base_sha,'baseline_export_sha256':'26f411564cc903308ce529b0100efe8d68f95a22a0a2e7e17dd4cf4e3f7364ba','collection':parts.name,'root':assembly.name,'removed_original_objects':removed_names,'protected_source_objects_sha256':protected,'protected_source_objects_bit_identical':True,'font_source_repairs':fonts,'structural_bodies':bodies,'new_original_ink':new_surface_checks,'appended_USB_objects':appended,'USB_source_sha256':usb['source_sha256'],'USB_export_sha256':usb['export_sha256'],'numeric_angles_and_needle_pivots_unchanged':True,'global_camera_or_metric_calibration_recovered':False,'pod_centres_mounts_and_lenses_unchanged':True,'all_part_dimensions_estimated':True,'odometer_still_static':True,'art_accepted':False};(HERE/'build-report-v2.json').write_text(json.dumps(report,indent=2)+'\n');(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');print('INSTRUMENTS_V2_SOURCE',report['source_sha256'],report['export_sha256'])
