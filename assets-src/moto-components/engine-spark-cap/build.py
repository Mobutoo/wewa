"""Original two-exposure DD111048-related cap exterior, bounded dimensions."""
from pathlib import Path
import bpy,bmesh,json,hashlib,math,sys
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/engine-spark-cap-v1';P=json.loads((H/'parameters.json').read_text());sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import material,mesh_object,csg,check_mesh,tree_world,export,studio
sys.path.insert(0,str(H.parent/'clutch-control'));from topology_cleanup_v2 import clean_evaluated
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for k in ['plug','head']:assert sha(R/P[k+'_source'])==P[k+'_sha256']
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
source=bpy.data.collections.new('WEWA_ENGINE_SPARK_CAP');s.collection.children.link(source);construction=bpy.data.collections.new('SPARK_CAP_RETAINED_CONSTRUCTION');s.collection.children.link(construction);guides=bpy.data.collections.new('SPARK_CAP_IMMUTABLE_GUIDES');s.collection.children.link(guides);stage=bpy.data.collections.new('SPARK_CAP_STUDIO_NOT_EXPORTED');s.collection.children.link(stage)
paint=material('Original estimated dark molded cap substrate',P['material']['base_color_linear'],0,.5);metal=material('Original estimated visible contact metal',(.45,.44,.40),1,.27)
def sectionmesh(name,profile,mat=None,n=192,seam=False,helix=False):
 vv=[];ff=[];rings=[]
 for x,r in profile:
  if r==0:rings.append([len(vv)]*n);vv.append((x,0,0));continue
  indices=[]
  for j in range(n):
   phi=math.tau*j/n;radius=r
   if seam and .0258<x<.054:
    axial=min(1,(x-.0258)/.002,(.054-x)/.002);peak=sum(math.exp(-.5*(math.atan2(math.sin(phi-angle),math.cos(phi-angle))/P['parting_seam_angular_sigma_rad'])**2)for angle in [0,math.pi]);radius+=P['parting_seam_height_m']*max(0,axial)*peak
   if helix and x>=0 and x<=.003 and r>.0008:
    phase=(x/P['contact_pitch_estimate_m']-phi/math.tau)%1;radius+=.00015*(.5+.5*math.cos(math.tau*phase))**3
   indices.append(len(vv));vv.append((x,radius*math.cos(phi),radius*math.sin(phi)))
  rings.append(indices)
 for i in range(len(rings)):
  q=(i+1)%len(rings)
  for j in range(n):
   k=(j+1)%n;face=list(dict.fromkeys([rings[i][j],rings[i][k],rings[q][k],rings[q][j]]))
   if len(face)>=3:ff.append(face)
 return mesh_object(name,vv,ff,construction,mat)
# Main photographed broad sleeve, mouth lip, tapered neck and rounded elbow end.
profile=[(.024,0),(.024,.0093)]
for j in range(1,13):a=math.pi/2*j/12;profile.append((.0243-.0003*math.cos(a),.0093+.0003*math.sin(a)))
profile +=[(.0252,.0096),(.0255,.0094),(.0258,.009),(.051,.009),(.053,.0089),(.054,.0085)]
for j in range(1,25):
 t=j/24;blend=t*t*(3-2*t);profile.append((.054+.004*t,.0085+(.0052-.0085)*blend))
profile +=[(.075,.0052)]
for j in range(1,17):a=math.pi/2*j/16;profile.append((.075+.0052*math.sin(a),0 if j==16 else .0052*math.cos(a)))
main=sectionmesh('Original cap sleeve lip taper and neck',profile,paint,n=384,seam=True)
# Short transverse port with rounded annular lip. Its absolute angle is estimated.
portprofile=[(0,0),(0,.0069),(.0004,.0073),(.001,.0075),(.015,.0075),(.0154,.0078),(.0158,.008),(.0175,.008),(.0178,.0078),(.018,.0076),(.018,0)]
port=sectionmesh('Original short transverse molded port',portprofile,paint);port.rotation_euler.z=math.pi/2;port.location=(P['transverse_port_centre_x_m'],-.006,0)
# Visible socket cavity: wider entry narrows behind the lip; hidden back simplified.
socket=[(.022,0),(.022,.0071),(.025,.0071),(.027,.0065),(.029,.0056),(.051,.0056),(.052,.0052),(.053,.0043),(.053,0)];longcut=sectionmesh('Estimated blind main plug socket',socket)
shortcut=sectionmesh('Estimated short-port blind socket',[(-.001,0),(-.001,.0038),(-.0005,.0045),(.015,.0045),(.015,0)]);shortcut.rotation_euler.z=math.pi/2;shortcut.location=(.075,0,0)
bpy.context.view_layer.update();cap,ops=csg(main,[port],[longcut,shortcut],source,paint,R,'Molded spark cap hollow exterior - editable conditional candidate');cleanup=clean_evaluated(cap,construction);cap.modifiers.clear();bpy.ops.object.select_all(action='DESELECT');cap.select_set(True);bpy.context.view_layer.objects.active=cap;bpy.ops.mesh.customdata_custom_splitnormals_clear();cap.data.update()
cap.name='Molded spark cap body - conditional candidate';cap.data.name=cap.name
for f in cap.data.polygons:f.use_smooth=True
# The contact is the tiny observed metallic feature only. Its mounting rear is
# truncated with a working50micrometre gap, not an invented resistor assembly.
contactprofile=[(-.00095,0),(-.00095,.0010)]
for j in range(1,73):contactprofile.append((-.00095+.003*j/72,.00105))
contactprofile +=[(.00205,.0009),(.00205,.00035),(.0013,.00035),(.0013,0)]
contact=sectionmesh('Visible short-port metallic contact - section estimated',contactprofile,metal,n=96,helix=True)
for c in list(contact.users_collection):c.objects.unlink(contact)
source.objects.link(contact);contact.rotation_euler.z=math.pi/2;contact.location=(.075,0,0)
with bpy.data.libraries.load(str(R/P['plug_source']),link=True)as(a,l):l.objects=['Spark plug inherited estimated seat datum']+[r['name']for r in json.loads((H.parent/'engine-spark-plug/build-report.json').read_text())['geometry']]
for o in l.objects:guides.objects.link(o)
plugroot=next(o for o in l.objects if o.type=='EMPTY');plugobjects=[o for o in l.objects if o.type=='MESH']
with bpy.data.libraries.load(str(R/P['head_source']),link=True)as(a,l):l.objects=['Engine head base provisional datum','Engine UG5 head hollow exterior casting - editable candidate']
for o in l.objects:guides.objects.link(o)
head=next(o for o in l.objects if o.type=='MESH');guides.hide_viewport=False;bpy.context.view_layer.update();datum=bpy.data.objects.new('Spark cap inherited unchanged provisional plug datum',None);source.objects.link(datum);datum.matrix_world=plugroot.matrix_world.copy();cap.parent=datum;contact.parent=datum;bpy.context.view_layer.update();objects=[cap,contact];geometry=[check_mesh(o)for o in objects]
for o in objects:
 o.data.calc_loop_triangles();assert all(t.area>0 for t in o.data.loop_triangles);o['all_dimensions_estimated']=True;o['art_accepted']=False
interfaces=[]
for a in objects:
 for b in plugobjects+[head]:interfaces.append({'a':a.name,'b':b.name,'pairs':len(tree_world(a).overlap(tree_world(b)))})
interfaces.append({'a':cap.name,'b':contact.name,'pairs':len(tree_world(cap).overlap(tree_world(contact)))})
assert not any(x['pairs']for x in interfaces),interfaces
construction.hide_render=True;construction.hide_viewport=True;guides.hide_render=True;guides.hide_viewport=True;export(H/'engine-spark-cap-inspection.glb',[datum]+objects);points=[o.matrix_world@Vector(v)for o in objects for v in o.bound_box];target=sum(points,Vector())/len(points);studio(s,stage,target)
for o in stage.objects:
 if o.type=='MESH':o.hide_render=True
 if o.type=='LIGHT':o.data.energy*=.02
s.camera.data.clip_start=.0005;file=H/'engine-spark-cap-v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(file),compress=True)
for k in ['plug','head']:assert sha(R/P[k+'_source'])==P[k+'_sha256']
report={'component_id':P['component_id'],'revision':P['revision'],'source_sha256':sha(file),'export_sha256':sha(H/'engine-spark-cap-inspection.glb'),'geometry':geometry,'cleanup':cleanup,'surface_interfaces':interfaces,'datum_world_matrix':[list(r)for r in datum.matrix_world],'plug_source_sha256':P['plug_sha256'],'head_source_sha256':P['head_sha256'],'scope':'Observed cap body and short-port metallic contact only. All dimensions/sections/pose estimated, blind backs simplified; no HTlead/resistor/internal electrical mechanism.','all_dimensions_estimated':True,'art_accepted':False,'physical_iphone_tested':False};(H/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');(O/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');print('SPARK_CAP_PREFLIGHT',json.dumps(report))
