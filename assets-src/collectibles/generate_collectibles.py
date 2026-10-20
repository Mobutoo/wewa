import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
M={};parts=[];manifest=[];coll=None
def mat(n,c,r=.6,m=0,em=0):
 a=bpy.data.materials.new(n);a.diffuse_color=(*c,1);a.use_nodes=True;p=a.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=r;p.inputs['Metallic'].default_value=m
 if em:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=em
 M[n]=a
mat('Original corrugated cardboard',(.33,.185,.078),.94);mat('Packing tape and kraft label',(.58,.43,.235),.54);mat('Black print and polymer',(.014,.018,.020),.71);mat('Energy yellow enamel',(.86,.57,.014),.36,.35,.16);mat('Steel contacts',(.31,.34,.35),.3,.83)
C='Original corrugated cardboard';T='Packing tape and kraft label';K='Black print and polymer';Y='Energy yellow enamel';S='Steel contacts'
def xyz(p):return Vector((p[0],-p[2],p[1]))
def begin(name):
 global coll,parts
 coll=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(coll);parts=[]
def fin(o,n,m):
 o.name=n;o.data.materials.append(M[m]);parts.append(o)
 for c in list(o.users_collection):c.objects.unlink(o)
 coll.objects.link(o);return o
def box(n,p,sc,m,b=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(p));o=bpy.context.object;o.dimensions=(sc[0],sc[2],sc[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if b:
  mod=o.modifiers.new('Small manufactured edge','BEVEL');mod.width=b;mod.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return fin(o,n,m)
def quad(n,vs,m):
 me=bpy.data.meshes.new(n);me.from_pydata([xyz(p) for p in vs],[],[(0,1,2,3)]);me.update();o=bpy.data.objects.new(n,me);coll.objects.link(o);parts.append(o);o.data.materials.append(M[m]);return o
def cyl(n,p,r,depth,m,v=16):
 bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=depth,location=xyz(p));o=bpy.context.object
 for f in o.data.polygons:f.use_smooth=len(f.vertices)==4
 return fin(o,n,m)
def export(name,meaning):
 originals=list(parts);group={}
 for o in originals:group.setdefault(o.data.materials[0].name,[]).append(o)
 out=[]
 for material,items in group.items():
  copies=[]
  for o in items:
   d=o.copy();d.data=o.data.copy();bpy.context.scene.collection.objects.link(d);copies.append(d)
  bpy.ops.object.select_all(action='DESELECT')
  for d in copies:d.select_set(True)
  bpy.context.view_layer.objects.active=copies[0]
  if len(copies)>1:bpy.ops.object.join()
  o=bpy.context.object;o.name=name+'__'+material.replace(' ','_');bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);o.data.calc_loop_triangles();out.append(o)
 count=sum(len(o.data.loop_triangles) for o in out);assert count<=1000,(name,count)
 bpy.context.view_layer.update();v=[o.matrix_world@Vector(p) for o in out for p in o.bound_box];g=[(p.x,p.z,-p.y) for p in v];lo=[min(p[i] for p in g) for i in range(3)];hi=[max(p[i] for p in g) for i in range(3)]
 bpy.ops.object.select_all(action='DESELECT')
 for o in out:o.select_set(True)
 file=OUT/(name+'.glb');bpy.ops.export_scene.gltf(filepath=str(file),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_cameras=False,export_lights=False)
 manifest.append({'id':name,'file':file.name,'triangles':count,'materials':list(group),'dimensions_m':[round(hi[i]-lo[i],5) for i in range(3)],'bounds_m':{'min':[round(p,5) for p in lo],'max':[round(p,5) for p in hi]},'coordinate_system':'GLB Xright,Yup,+Zfront; origin ground bottom centre','purpose':meaning,'provenance':'Original procedural Blender geometry and PBR materials, no photo, external mesh, logo or paid asset.','license':'Original generated work authored for user Viva Wewa project.','sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'bytes':file.stat().st_size})
 for o in out:bpy.data.objects.remove(o,do_unlink=True)
 root=bpy.data.objects.new(name+'__EDITABLE',None);coll.objects.link(root)
 for o in originals:o.parent=root
 root.location.x=-.42 if name=='pickup_parcel' else .42
# A real brown delivery carton, with packing strips, flap seam, kraft label and printed barcode.
begin('pickup_parcel')
box('Cardboard carton',(0,.15,0),(.45,.30,.32),C,.004)
# Kraft flap seam on top; all additions stay extremely close to the original packaging envelope.
quad('Central top flap line',[(-.0015,.3002,-.158),(.0015,.3002,-.158),(.0015,.3002,.158),(-.0015,.3002,.158)],K)
quad('Top packing tape',[(-.033,.3005,-.158),(.033,.3005,-.158),(.033,.3005,.158),(-.033,.3005,.158)],T)
for front in [-1,1]:
 z=front*.1603
 quad('Tape end wrap',[(-.033,.17,z),(.033,.17,z),(.033,.297,z),(-.033,.297,z)],T)
quad('Shipping kraft label',[(.061,.075,.1607),(.196,.075,.1607),(.196,.168,.1607),(.061,.168,.1607)],T)
# Original abstract barcode, not an identifiable tracking code.
widths=[1,1,2,1,3,1,2,2,1,1,3,2,1,2];x=.070
for i,w in enumerate(widths):
 ww=.0014*w
 quad('Barcode ink',[(x,.087,.161),(x+ww,.087,.161),(x+ww,.139,.161),(x,.139,.161)],K);x+=ww+.0025
for y,w in [(.152,.092),(.146,.061)]:quad('Address placeholder ink',[(.071,y,.161),(.071+w,y,.161),(.071+w,y+.002,.161),(.071,y+.002,.161)],K)
# Two side handling marks made of simple dark strokes; no text/logo needed.
for x in [-.125,-.094]:
 quad('Keep upright mark',[(x,.09,.1607),(x+.007,.09,.1607),(x+.007,.137,.1607),(x,.137,.1607)],K)
 # triangle arrowhead
 me=bpy.data.meshes.new('Arrow head');me.from_pydata([xyz((x-.005,.137,.1607)),xyz((x+.012,.137,.1607)),xyz((x+.0035,.151,.1607))],[],[(0,1,2)]);me.update();o=bpy.data.objects.new('Handling arrow',me);coll.objects.link(o);parts.append(o);o.data.materials.append(M[K])
export('pickup_parcel','Brown corrugated delivery parcel, replaces generic gameplay cube; footprint0.45×0.32m,height0.30m')
# Fictional readable energy cartridge, black upper/lower collars and yellow metal body.
begin('nitro_token')
cyl('Yellow energy shell',(0,.226,0),.120,.346,Y,16)
cyl('Lower protective collar',(0,.030,0),.125,.060,K,16)
cyl('Upper protective collar',(0,.410,0),.125,.040,K,16)
cyl('Top steel contact',(0,.44,0),.055,.020,S,12)
# yellow side ribs and two restrained yellow band faces against black shell ends
for x in [-.083,.083]:box('Front vertical grip rib',(x,.226,.085),(.022,.26,.035),K,.004)
# Raised yellow lightning bolt silhouette on black front badge.
box('Black energy badge',(0,.23,.117),(.085,.205,.012),K,.008)
vs=[(-.004,.315,.126),(.030,.315,.126),(.008,.252,.126),(.034,.252,.126),(-.025,.149,.126),(-.006,.224,.126),(-.032,.224,.126)]
me=bpy.data.meshes.new('Original lightning glyph');me.from_pydata([xyz(p) for p in vs],[],[(0,1,2),(0,2,6),(2,3,5),(3,4,5),(2,5,6)]);me.update();o=bpy.data.objects.new('Energy glyph',me);coll.objects.link(o);parts.append(o);o.data.materials.append(M[Y])
export('nitro_token','Fictional yellow/black energy cartridge, arcade collectable; diameter0.25m,height0.45m')
report={'library':'Viva Wewa original gameplay collectibles','created_utc':'2026-10-20','assets':manifest,'max_triangles_each':1000,'max_materials_each':3,'geometry_license':'Original generated work authored for the user project; no third-party assets or copied labels.','limits':['Fictional energy cartridge is an arcade cue, not real product placement.','No photographic acceptance asserted.','Blender preview contains both items; exported GLBs contain one item each at local ground origin.']}
(OUT/'provenance.json').write_text(json.dumps(report,indent=2))
# Editable scene and actual Blender render.
for p,power,size in [((1.5,-2,3),400,3),((-2,-1,2),300,2),((0,2,2.8),450,2)]:
 bpy.ops.object.light_add(type='AREA',location=p);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,0,.18))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(1.1,-2.7,1.25));c=bpy.context.object;c.rotation_euler=(Vector((0,0,.18))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=1.65
s=bpy.context.scene;s.camera=c;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False;s.render.resolution_x=1500;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.filepath=str(OUT/'collectibles-preview.png');s.world.color=(.3,.3,.3);s.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'viva-wewa-collectibles.blend'));bpy.ops.render.render(write_still=True)
print('COLLECTIBLES_READY',json.dumps(manifest))
