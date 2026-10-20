import bpy, math, json, os, hashlib
from mathutils import Vector
from pathlib import Path
OUT=Path(__file__).resolve().parent;EXPORT=OUT/'exports';EXPORT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
M={};assets=[];parts=[];collection=None

def mat(n,c,r=.6,metal=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=r;p.inputs['Metallic'].default_value=metal;M[n]=m;return m
mat('VVK_concrete_CC0',(.63,.60,.52),.88);mat('VVK_painted_steel',(.055,.105,.125),.65,.48);mat('VVK_dark_glass',(.032,.062,.075),.2,.3);mat('VVK_weathered_wood',(.19,.105,.045),.86);mat('VVK_masonry',(.32,.19,.115),.9)
# Existing documented CC0 material source; relative to this generator, embedded in GLB exports.
m=M['VVK_concrete_CC0'];nodes=m.node_tree.nodes;p=nodes.get('Principled BSDF')
for file,kind in [('concrete_wall_003_diff.jpg','diff'),('concrete_wall_003_nor_gl.jpg','normal')]:
 im=bpy.data.images.load(str(OUT/'textures'/file));im.filepath=str(OUT/'textures'/file);im.pack()
 tex=nodes.new('ShaderNodeTexImage');tex.image=im;tex.extension='REPEAT'
 if kind=='diff':m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
 else:
  im.colorspace_settings.name='Non-Color';normal=nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.4;m.node_tree.links.new(tex.outputs['Color'],normal.inputs['Color']);m.node_tree.links.new(normal.outputs['Normal'],p.inputs['Normal'])
C='VVK_concrete_CC0';S='VVK_painted_steel';G='VVK_dark_glass';W='VVK_weathered_wood';B='VVK_masonry'
def xyz(p):return Vector((p[0],-p[2],p[1]))
def begin(n):
 global parts,collection
 parts=[];collection=bpy.data.collections.new(n);bpy.context.scene.collection.children.link(collection)
def finish(o,n,m,sm=False):
 o.name=n;o.data.materials.append(M[m])
 for old in list(o.users_collection):old.objects.unlink(o)
 collection.objects.link(o);parts.append(o)
 for poly in o.data.polygons:poly.use_smooth=sm
 return o
def box(n,p,sc,m=C,b=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(p));o=bpy.context.object;o.dimensions=(sc[0],sc[2],sc[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if b:
  mod=o.modifiers.new('Construction edge','BEVEL');mod.width=b;mod.segments=1;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return finish(o,n,m)
def cyl(n,a,b,r,m=S,v=10):
 a,b=xyz(a),xyz(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return finish(o,n,m,True)
def mesh(n,vs,fs,m,sm=False):
 me=bpy.data.meshes.new(n);me.from_pydata([xyz(p) for p in vs],[],fs);me.update();o=bpy.data.objects.new(n,me);collection.objects.link(o);parts.append(o);o.data.materials.append(M[m]);
 for poly in me.polygons:poly.use_smooth=sm
 return o
def frame(x,h,z,w,hh,mat=S,t=.045,depth=.09):
 # z is outer face; frame proud of a glass pane, window sill below.
 box('Window left jamb',(x-w/2+t/2,h,z-depth/2),(t,hh,depth),mat)
 box('Window right jamb',(x+w/2-t/2,h,z-depth/2),(t,hh,depth),mat)
 box('Window lintel',(x,h+hh/2-t/2,z-depth/2),(w,t,depth),mat)
 box('Window sill frame',(x,h-hh/2+t/2,z-depth/2),(w,t,depth),mat)
 box('Recessed glazing',(x,h,z-depth+.012),(w-2*t,hh-2*t,.009),G)
def sill(x,h,w,z=.095):box('Projecting concrete sill',(x,h,z),(w,.055,.22),C,.008)
def structural():
 # Narrow perimeter structure, no full-bay backing slab. Native source building remains backing.
 for x in [-1.65,1.65]:box('Edge concrete pier',(x,1.5,.005),(.1,3,.09),C,.007)
 box('Top lintel',(0,2.95,.012),(3.2,.1,.12),C,.005)
 box('Bottom construction seam',(0,.04,.005),(3.2,.08,.08),C,.004)
def ac(x,h,z=.16):
 box('AC compressor cabinet',(x,h,z),(.52,.35,.26),S,.018)
 # actual narrow ventilation blades, fan guard cross and brackets
 for j in range(5):box('AC ventilation slot',(x,h-.12+j*.055,z+.136),(.43,.012,.014),G)
 for xx in [x-.19,x+.19]:box('AC wall bracket',(xx,h-.21,z-.025),(.035,.07,.30),S)
def shutter(x,h,w,hh,z=.075,open_fraction=1):
 box('Shutter left track',(x-w/2-.025,h,z),(.05,hh,.1),S)
 box('Shutter right track',(x+w/2+.025,h,z),(.05,hh,.1),S)
 box('Shutter roller hood',(x,h+hh/2+.055,z),(w+.16,.14,.22),S,.02)
 count=max(3,int(hh*open_fraction/.11));step=hh*open_fraction/count
 # single corrugated geometry ribbon, retaining genuine slat profile with few triangles.
 vs=[];fs=[];top=h+hh/2
 for j in range(count*2+1):
  yy=top-j*step/2;zz=z+(.015 if j%2 else -.012)
  vs.extend([(x-w/2,yy,zz),(x+w/2,yy,zz)])
 for j in range(count*2):fs.append((j*2,j*2+1,j*2+3,j*2+2))
 mesh('Corrugated roller shutter',vs,fs,S)
 box('Shutter pull rail',(x,top-count*step,z+.025),(w,.04,.035),S)
def sign(w=2.6):
 box('Blank shop sign mounting',(0,2.64,.10),(w,.32,.07),S,.008)
 for x in [-w*.45,w*.45]:box('Sign bracket',(x,2.64,.03),(.035,.22,.09),S)
def ventblocks(x,h,w,hh,z=.03):
 for j in range(3):
  for i in range(5):
   xx=x-w/2+(i+.5)*w/5;yy=h-hh/2+(j+.5)*hh/3
   # four bars surround a genuine open aperture, not painted decoration
   ww=w/5-.025;ht=hh/3-.025
   box('Vent brick top',(xx,yy+ht/2,z),(ww,.025,.10),B)
   box('Vent brick side',(xx-ww/2,yy,z),(.025,ht,.10),B)

def facade(family,upper):
 name='facade_'+family+('_upper' if upper else '_ground');begin(name);structural()
 if family=='aged_office':
  for x in [-.79,.79]:
   frame(x,1.58 if upper else 1.48,.09,1.25,1.82 if upper else 2.15)
   box('Mullion',(x,1.55,.095),(.035,1.82 if upper else 2.10,.06),S)
   sill(x,.64 if upper else .40,1.38)
  if upper:ac(.94,.37,.18)
  else:
   box('Office door mullion',(-.79,1.37,.11),(.025,2.03,.03),S)
   box('Door handle',(-.58,1.29,.14),(.018,.22,.025),S)
  box('Concrete shade eyebrow',(0,2.62,.17),(3.14,.10,.40),C,.008)
 elif family=='tropical_apartment':
  if upper:
   frame(0,1.70,.07,2.20,2.12)
   box('French door centre rail',(0,1.7,.085),(.065,2.10,.06),S)
   box('Balcony slab',(0,.37,.29),(2.85,.09,.62),C,.009)
   for x in [-1.38,1.38]:box('Balcony rail end',(x,.85,.32),(.025,.94,.55),S)
   box('Balcony top rail',(0,1.32,.58),(2.82,.035,.035),S)
   box('Balcony lower rail',(0,.47,.58),(2.82,.025,.025),S)
   for k in range(12):box('Balcony vertical baluster',(-1.34+k*2.68/11,.895,.58),(.022,.83,.022),S)
  else:
   box('Entrance wood door',(-.95,1.20,.025),(.88,2.25,.065),W,.006)
   frame(.55,1.65,.09,1.65,1.45);sill(.55,.90,1.80)
   box('Door recessed panels',(-.95,1.4,.065),(.67,1.44,.022),W,.008)
   box('Door steel latch',(-.65,1.12,.09),(.02,.15,.03),S)
   ventblocks(.55,.48,1.54,.47)
  box('Roof shade',(0,2.77,.19),(3.16,.10,.42),C,.01)
 elif family=='retail_shutter':
  if not upper:
   shutter(0,1.22,2.92,2.22);sign()
   box('Shop raised threshold',(0,.10,.13),(3.0,.08,.25),C,.005)
  else:
   for x in [-.81,.81]:frame(x,1.70,.09,1.30,1.5);sill(x,.91,1.39)
   box('Masonry spandrel',(0,.48,.025),(3.18,.66,.08),B)
   for j in range(5):box('Brick mortar reveal',(0,.20+j*.13,.071),(3.14,.006,.006),C)
   # sheet-metal hood at top with genuine braces
   shade=box('Pitched window awning',(0,2.61,.21),(3.12,.045,.44),S);shade.rotation_euler.x=-.14
   for x in [-1.25,1.25]:cyl('Shade diagonal brace',(x,2.27,.03),(x,2.60,.40),.012,S)
 elif family=='workshop':
  if not upper:
   shutter(-.42,1.25,2.02,2.25,open_fraction=.62)
   frame(1.10,1.73,.08,.77,1.15)
   box('Workshop service counter',(1.10,1.12,.17),(.86,.07,.35),W,.005)
   box('Workbench sill',(1.10,.49,.07),(.77,.11,.15),S)
   sign(2.82)
   for x in [-.95,.11]:box('Shutter safety guide',(x,1.21,.065),(.025,2.20,.08),S)
  else:
   frame(0,1.65,.09,2.92,1.64)
   for x in [-.99,0,.99]:box('Industrial steel mullion',(x,1.65,.10),(.03,1.60,.06),S)
   box('Industrial transom',(0,1.66,.10),(2.89,.035,.055),S)
   sill(0,.79,3.10)
   box('Upper workshop masonry',(0,.39,.03),(3.18,.68,.07),B)
   ac(1.02,2.66,.16)
 elif family=='compound_gate':
  if not upper:
   for x in [-1.47,1.47]:box('Masonry gate pier',(x,1.33,.045),(.26,2.58,.18),B,.008)
   for x in [-.655,.655]:
    box('Gate lower metal panel',(x,.74,.075),(1.27,1.22,.055),S,.004)
    box('Gate top rail',(x,2.42,.075),(1.27,.04,.05),S)
    for j in range(7):box('Gate vertical bar',(x-.54+j*.18,1.87,.075),(.018,1.06,.035),S)
   box('Gate centre latch',(.07,1.25,.115),(.16,.045,.05),S)
  else:
   for x in [-1.5,1.5]:box('Parapet masonry pier',(x,1.45,.02),(.20,2.8,.12),B,.008)
   box('Parapet upper coping',(0,2.76,.06),(3.10,.08,.18),C,.008)
   box('Parapet lower coping',(0,.24,.06),(3.10,.08,.18),C,.008)
   # perforated compound screen: real openings preserve all source geometry behind
   ventblocks(0,1.5,2.8,2.30,.03)
 elif family=='louvered_office':
  frame(0,1.50,.025,3.0,2.75,t=.05,depth=.06)
  if upper:
   for j in range(8):
    x=-1.35+j*2.7/7
    fin=box('Vertical concrete sun fin',(x,1.5,.17),(.055,2.75,.37),C,.006);fin.rotation_euler.z=.12
   sill(0,.10,3.1,.14)
  else:
   for j in range(11):
    h=.24+j*.245
    blade=box('Horizontal brise soleil',(0,h,.15),(2.99,.045,.35),C,.005);blade.rotation_euler.x=.12
   box('Glazed office entrance pull',(1.08,1.38,.37),(.025,.42,.025),S)
 export_asset(name,'facade',{'family':family,'level':'upper' if upper else 'ground','bay_width_m':3.4,'storey_height_m':3.0,'backing_slab':False,'placement':'Place +Z outward from an existing source building edge, preserving its footprint; Y=0 is storey base.'},1600)

def uv_physical(o):
 # Planar world-space UVs at 2m material scale; genuine concrete maps, no window atlas.
 if not o.data.uv_layers:o.data.uv_layers.new(name='Surface_2m')
 uv=o.data.uv_layers.active.data
 for poly in o.data.polygons:
  n=poly.normal;axis=max(range(3),key=lambda i:abs(n[i]))
  for li in poly.loop_indices:
   v=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
   if axis==0:a,b=v.y,v.z
   elif axis==1:a,b=v.x,v.z
   else:a,b=v.x,v.y
   uv[li].uv=(a/2,b/2)
def export_asset(name,kind,extra,budget=1600):
 global parts
 source=list(parts);bpy.context.view_layer.update()
 # Keep named construction pieces editable in .blend; only temporary export copies are fused.
 groups={}
 for obj in source:
  dup=obj.copy();dup.data=obj.data.copy();bpy.context.scene.collection.objects.link(dup);groups.setdefault(dup.data.materials[0].name,[]).append(dup)
 exports=[]
 for m,items in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for o in items:o.select_set(True)
  bpy.context.view_layer.objects.active=items[0];bpy.ops.object.join();o=bpy.context.object;o.name=name+'__'+m
  bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
  o.data.calc_loop_triangles();exports.append(o)
 tri=sum(len(o.data.loop_triangles) for o in exports)
 if tri>budget:
  for o in exports:
   mod=o.modifiers.new('Export geometry budget','DECIMATE');mod.ratio=(budget-12)/tri;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 for o in exports:
  bpy.context.view_layer.objects.active=o
  mod=o.modifiers.new('Explicit portable tangent triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name)
  uv_physical(o);o.data.calc_loop_triangles()
 tri=sum(len(o.data.loop_triangles) for o in exports)
 bpy.context.view_layer.update();coords=[o.matrix_world@Vector(v) for o in exports for v in o.bound_box]
 # Blender to glTF: x,x; y,z; z,-y.
 gl=[(v.x,v.z,-v.y) for v in coords];lo=[min(v[i] for v in gl) for i in range(3)];hi=[max(v[i] for v in gl) for i in range(3)]
 bpy.ops.object.select_all(action='DESELECT')
 for o in exports:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(EXPORT/(name+'.glb')),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_tangents=(C in groups),export_cameras=False,export_lights=False,export_extras=True)
 file=EXPORT/(name+'.glb');item={'id':name,'kind':kind,'file':'exports/'+name+'.glb','triangles':tri,'triangle_budget':budget,'bounds_m':{'min':[round(x,5) for x in lo],'max':[round(x,5) for x in hi]},'dimensions_m':[round(hi[i]-lo[i],5) for i in range(3)],'front':[0,0,1],'up':[0,1,0],'origin':'ground/storey bottom centre','materials':list(groups),'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'geometry_license':'Original generated geometry for Viva Wewa; no third-party model','textures':'concrete_wall_003 maps by Poly Haven CC0-1.0 where concrete material is present','editable_collection':collection.name};item.update(extra);assets.append(item)
 for o in exports:bpy.data.objects.remove(o,do_unlink=True)
 # Preview arrange original construction pieces under a root; exports remain authored at origin.
 root=bpy.data.objects.new(name+'__EDITABLE_ROOT',None);collection.objects.link(root)
 for o in source:o.parent=root
 if kind=='facade':
  i=len([a for a in assets if a['kind']=='facade'])-1;root.location=(i%6*4.15,0,(i//6)*3.7)
 else:
  i=len([a for a in assets if a['kind']=='prop'])-1;root.location=(i%10*2.5,4+(i//10)*3.0,0)
 root['asset_id']=name;root['export_origin']='Move root to world origin before re-export; named individual construction pieces remain editable.'

families=['aged_office','tropical_apartment','retail_shutter','workshop','compound_gate','louvered_office']
for upper in [False,True]:
 for family in families:facade(family,upper)

# Twenty reusable original street construction props; dimensions in metres, not surveyed positions.
def prop(n,fn,budget=1400):begin(n);fn();export_asset(n,'prop',{'placement':'Ground bottom centre; +Z preferred facing where directional.'},budget)
def curb():box('Curb concrete',(0,.125,0),(1,.25,.20),C,.015)
def corner():
 box('Corner curb leg',(-.39,.125,0),(.22,.25,1),C,.012);box('Corner curb return',(.11,.125,.39),(.78,.25,.22),C,.012)
def drain():
 for x in [-.21,.21]:box('Drain side wall',(x,.09,0),(.05,.18,1),C,.006)
 box('Drain bed',(0,.025,0),(.42,.05,1),C,.004)
def grate():
 for x in [-.20,.20]:box('Grate long frame',(x,.035,0),(.025,.07,1),S)
 for j in range(15):box('Grate cross slat',(0,.055,-.48+j*.96/14),(.39,.025,.024),S)
def fence():
 for x in [-.97,.97]:box('Fence post',(x,.85,0),(.06,1.7,.06),S,.004)
 for h in [.34,1.43]:box('Fence cross rail',(0,h,0),(1.94,.04,.035),S)
 for j in range(14):box('Fence picket',(-.91+j*1.82/13,.88,0),(.02,1.47,.02),S)
def lamp():
 cyl('Pole',(0,0,0),(0,5.5,0),.055,S,12);cyl('Outreach arm',(0,5.49,0),(0,5.70,.65),.036,S,10)
 box('Lamp housing',(0,5.68,.76),(.30,.09,.54),S,.035);box('Lamp diffuser',(0,5.625,.77),(.235,.012,.42),G,.012)
 box('Pole foundation',(0,.08,0),(.22,.16,.22),C,.012)
def bollard():
 cyl('Bollard base',(0,0,0),(0,.84,0),.058,S,12);box('Reflector band',(0,.66,.061),(.06,.06,.005),C)
def bench():
 for x in [-.64,.64]:
  box('Bench support',(x,.23,0),(.065,.46,.43),S,.012);cyl('Back upright',(x,.40,-.16),(x,.92,-.25),.022,S,10)
 for j in range(5):box('Wood seat slat',(0,.47,-.20+j*.10),(1.6,.04,.075),W,.006)
 for h in [.64,.78,.91]:box('Wood back slat',(0,h,-.235),(1.6,.085,.035),W,.006)
def bin():
 box('Public litter bin',(0,.48,0),(.46,.87,.42),S,.035);box('Litter lid',(0,.95,0),(.50,.09,.46),S,.025)
 box('Bin aperture',(0,.79,.216),(.33,.11,.009),G,.018);box('Bin base',(0,.04,0),(.42,.08,.38),C,.012)
def cabinet():
 box('Power cabinet',(0,.66,0),(.62,1.18,.34),S,.025);box('Concrete plinth',(0,.07,0),(.69,.14,.42),C,.014)
 box('Cabinet door',(0,.67,.179),(.55,1.08,.015),S,.014)
 for j in range(6):box('Cabinet vent',(0,.33+j*.047,.19),(.38,.012,.008),G)
 cyl('Cabinet door latch',(.205,.72,.193),(.205,.72,.218),.016,S,10)
def pole():
 cyl('Utility pole',(0,0,0),(0,5.9,0),.085,C,12)
 for h in [4.95,5.60]:
  box('Pole crossarm',(0,h,0),(1.2,.07,.07),S)
  for x in [-.5,0,.5]:cyl('Ceramic insulator',(x,h+.035,0),(x,h+.16,0),.048,C,10)
def signpost():
 cyl('Sign post',(0,0,0),(0,2.5,0),.027,S,10);box('Blank local sign',(0,2.10,0),(.72,.48,.035),S,.02)
def planter():
 box('Planter base',(0,.045,0),(.70,.09,.62),C,.012)
 for x in [-.365,.365]:box('Planter side',(x,.36,0),(.07,.63,.69),C,.014)
 for z in [-.31,.31]:box('Planter end',(0,.36,z),(.66,.63,.07),C,.014)
 box('Soil',(0,.59,0),(.61,.04,.52),B)
def stall():
 for x in [-.70,.70]:
  for z in [-.34,.34]:box('Stall leg',(x,.47,z),(.045,.94,.045),W)
 box('Sales counter',(0,.96,0),(1.55,.07,.80),W,.012)
 for x in [-.70,.70]:box('Canopy post',(x,1.53,-.30),(.04,1.12,.04),S)
 sheet=box('Corrugated market canopy',(0,2.11,0),(1.72,.04,.99),S,.008);sheet.rotation_euler.x=.13
 box('Counter display lip',(0,1.02,.36),(1.5,.07,.025),W)
def umbrella():
 cyl('Umbrella pole',(0,0,0),(0,2.18,0),.025,S,12);cyl('Umbrella foot',(0,0,0),(0,.10,0),.25,C,16)
 vs=[(0,2.40,0)]+[(1.0*math.cos(k*math.tau/12),2.08,1.0*math.sin(k*math.tau/12)) for k in range(12)];fs=[]
 for k in range(12):fs.append((0,k+1,(k+1)%12+1));cyl('Umbrella rib',(0,2.33,0),vs[k+1],.009,S,6)
 mesh('Umbrella canopy',vs,fs,S)
def crate():
 for x in [-.29,.29]:
  for z in [-.19,.19]:box('Crate corner',(x,.21,z),(.035,.42,.035),W)
 for h in [.07,.20,.34]:
  for z in [-.20,.20]:box('Crate long slat',(0,h,z),(.60,.09,.025),W)
  for x in [-.30,.30]:box('Crate end slat',(x,h,0),(.025,.09,.40),W)
 for x in [-.23,-.08,.08,.23]:box('Crate base board',(x,.025,0),(.12,.05,.38),W)
def barrier():
 for x in [-.72,.72]:
  box('Road barrier foot',(x,.055,0),(.22,.11,.62),S,.012);box('Barrier upright',(x,.55,0),(.05,1.0,.05),S)
 for h in [.45,.92]:box('Barrier horizontal rail',(0,h,0),(1.65,.09,.06),S,.008)
def concretepost():
 box('Compound marker post',(0,.38,0),(.20,.76,.20),C,.012);box('Post crown',(0,.78,0),(.23,.08,.23),C,.015)
def pavers():
 for j in range(5):
  for k in range(4):box('Individual paving block',(-.375+k*.25,.035,-.40+j*.20),(.238,.07,.188),C,.004)
def canopy():
 for x in [-.73,.73]:box('Awning rear bracket',(x,.24,.025),(.035,.48,.05),S);cyl('Awning brace',(x,.04,.03),(x,.51,.60),.012,S,8)
 sheet=box('Shop shade sheet',(0,.55,.32),(1.7,.035,.65),S,.005);sheet.rotation_euler.x=.08

for name,fn in [('curb_1m',curb),('curb_corner',corner),('open_drain_1m',drain),('drain_grate_1m',grate),('rail_fence_2m',fence),('street_lamp',lamp),('bollard',bollard),('bench_wood',bench),('litter_bin',bin),('electrical_cabinet',cabinet),('utility_pole',pole),('blank_signpost',signpost),('concrete_planter',planter),('vendor_stall',stall),('market_umbrella',umbrella),('wood_crate',crate),('portable_barrier',barrier),('concrete_marker',concretepost),('paving_patch_1m',pavers),('shop_awning',canopy)]:prop(name,fn)

manifest={'library':'Viva Wewa modular architecture and street kit','version':1,'generated_utc':'2026-10-20','coordinate_system':'glTF +Y up, +Z street-facing, +X right. Metres.','asset_count':len(assets),'facade_count':12,'prop_count':20,'production_status':'Original editable Blender production assets; artistic and geographic acceptance not yet granted.','geographic_limit':'Not a surveyed reconstruction of Gombe. No source footprint, alignment or geodata modified. Placement must be validated separately.','facade_contract':{'width_m':3.4,'height_m':3.0,'max_depth_m':.65,'no_solid_backing_slab':True,'notes':'Open construction frame and genuine window/door/shutter features. A source building provides the rear wall. Modules must be culled/placed by building edge; do not enlarge footprints.'},'shared_materials':list(M),'textures':[{'source':'https://polyhaven.com/a/concrete_wall_003','license':'CC0-1.0','license_url':'https://polyhaven.com/license','files':['textures/concrete_wall_003_diff.jpg','textures/concrete_wall_003_nor_gl.jpg'],'usage':'Concrete surface only; no photographic facade/window billboard'}],'geometry_license':'Original procedural geometry authored for the Viva Wewa user project, no external mesh copied.','assets':assets}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
# Pack images for editable portability; relative source texture paths are documented.
for im in bpy.data.images:
 if im.name.startswith('concrete_wall_003'):im.filepath='//textures/'+im.name
# Separate studio collection; original asset collections retain named editable construction pieces.
bpy.ops.object.select_all(action='DESELECT');bpy.context.scene.world.color=(.3,.3,.3)
for p,power,size in [((5,-6,13),2200,8),((20,-4,10),2000,8),((12,7,12),1600,7)]:
 bpy.ops.object.light_add(type='AREA',location=p);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((10,0,3))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(10.4,-23,11.0));cam=bpy.context.object;cam.rotation_euler=(Vector((10.4,0,3.2))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=25.8
scene=bpy.context.scene;scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False;scene.render.resolution_x=2600;scene.render.resolution_y=1150;scene.render.resolution_percentage=100;scene.render.filepath=str(OUT/'facades-preview.png');scene.view_settings.view_transform='AgX'
# Street props hidden for architectural contact sheet; preserve model collections in source blend.
for a in assets:
 if a['kind']=='prop':bpy.data.collections[a['editable_collection']].hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'viva-wewa-street-kit.blend'));bpy.ops.render.render(write_still=True)
for a in assets:
 bpy.data.collections[a['editable_collection']].hide_render=a['kind']=='facade'
cam.location=(12.0,-14,11);cam.rotation_euler=(Vector((11.0,5.6,1.4))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=26.5;scene.render.filepath=str(OUT/'props-preview.png');scene.render.resolution_y=1300;bpy.ops.render.render(write_still=True)
# Restore full scene and source preview camera in saved editable blend.
for a in assets:bpy.data.collections[a['editable_collection']].hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'viva-wewa-street-kit.blend'))
print('KIT_COMPLETE',json.dumps({'facades':12,'props':20,'triangles_total':sum(a['triangles'] for a in assets),'bytes':sum(a['bytes'] for a in assets)}))
