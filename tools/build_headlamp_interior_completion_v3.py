"""Visible DJ201051 glazing morphology and observed annular lips only.
No bowl, optical facets, hidden neck, welding or photographed texture.
"""
from pathlib import Path
import bpy, math, json, hashlib, runpy
R=Path('/workspace/wewa');K='headlamp-interior-completion-v3'
H=R/'assets-src/moto-components'/K; O=R/'creative/reviews'/K
H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version=0
u=runpy.run_path(str(R/'tools/front_completion_front10_mesh_helpers_v1.py'))
collection=bpy.data.collections.new('WEWA_HEADLAMP_VISIBLE_OPTICS_V3');bpy.context.scene.collection.children.link(collection)
def mesh(name,v,f):
 o=u['mesh_object'](name,v,f)
 for c in list(o.users_collection):c.objects.unlink(o)
 collection.objects.link(o)
 for p in o.data.polygons:p.use_smooth=True
 return o
def material(name,color,metal,rough,trans=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF']
 for k,v in [('Base Color',color),('Metallic',metal),('Roughness',rough),('Transmission Weight',trans),('IOR',1.46)]:p.inputs[k].default_value=v
 return m
glass=material('Clear glazing visible-surface hypothesis v3',(.99,.995,1,1),0,.025,1)
silver=material('Observed silver annular lips v3',(.80,.82,.84,1),1,.12)
radius=.085;sag=.0035;N=1280;nr=112;lines=[.30,.015,-.29,-.43]
def zvalue(x,y):
 r=math.hypot(x,y);z=sag*(1-(r/radius)**2)
 # Foreground lines are observed through all three exact-code photos.
 # Their molded side and amplitude are authoring estimates, not measured facts.
 z+=sum(.00012*math.exp(-((y-radius*q)/.00020)**2) for q in lines)
 if .0805<r<.0845:
  fade=math.sin(math.pi*(r-.0805)/.004)**2
  z+=.000055*fade*(.5+.5*math.cos(640*math.atan2(y,x)))
 return z
v=[(0,0,zvalue(0,0))];f=[]
for i in range(1,nr+1):
 r=radius*i/nr
 for j in range(N):
  a=2*math.pi*j/N;x=r*math.cos(a);y=r*math.sin(a);v.append((x,y,zvalue(x,y)))
for j in range(N):f.append((0,1+j,1+(j+1)%N))
for i in range(nr-1):
 for j in range(N):a=1+i*N+j;b=1+i*N+(j+1)%N;f.append((a,a+N,b+N,b))
objects=[mesh('DJ201051_VISIBLE_GLAZING_FOUR_TRANSVERSE_LINES_AND_FINE_BORDER_V3',v,f)];objects[0].data.materials.append(glass)
def annulus(name,ri,ro,y,z,x=0):
 v=[];f=[]
 for r in [ri,ro]:
  for j in range(512):a=2*math.pi*j/512;v.append((x+r*math.cos(a),y+r*math.sin(a),z))
 for j in range(512):k=(j+1)%512;f.append((j,512+j,512+k,k))
 ob=mesh(name,v,f);ob.data.materials.append(silver);objects.append(ob)
annulus('DJ201051_VISIBLE_PERIPHERAL_SILVER_LIP_ONLY_V3',.0828,.085,0,-.00045)
annulus('DJ201051_VISIBLE_MAIN_OPENING_FRONT_LIP_ONLY_V3',.0175,.019,.0008,-.00045,.0045)
annulus('DJ201051_VISIBLE_PILOT_OPENING_FRONT_LIP_ONLY_V3',.0063,.0072,-.037,-.00045,.003)
# Appearance candidate: planar visible silver field traced by its front outline
# and two observed aperture projections. It is deliberately NOT a bowl, and
# neither polygon edges nor triangulation are asserted to be optical facets.
# The flat recession is an explicit depth simplification for exterior review.
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
vv=[];ee=[]
for cx,cy,rr,nn in [(0,0,.0828,512),(.0045,.0008,.019,192),(.003,-.037,.0072,128)]:
 base=len(vv)
 for k in range(nn):a=2*math.pi*k/nn;vv.append(Vector((cx+rr*math.cos(a),cy+rr*math.sin(a))))
 for k in range(nn):ee.append((base+k,base+(k+1)%nn))
for i in range(-38,39):
 for j in range(-38,39):
  x=i*.002;y=j*.002
  if math.hypot(x,y)<.080 and math.hypot(x-.0045,y-.0008)>.020 and math.hypot(x-.003,y+.037)>.0082:vv.append(Vector((x,y)))
verts,edges,faces,*_=delaunay_2d_cdt(vv,ee,[],0,1e-9)
retained=[]
for face in faces:
 x=sum(verts[i].x for i in face)/len(face);y=sum(verts[i].y for i in face)/len(face)
 if math.hypot(x,y)<.0828 and math.hypot(x-.0045,y-.0008)>.019 and math.hypot(x-.003,y+.037)>.0072:retained.append(face)
skin=mesh('DJ201051_VISIBLE_SILVER_FIELD_FRONT_PROJECTION_DEPTH_SIMPLIFIED_V3',[(p.x,p.y,-.00045) for p in verts],retained)
skin.data.materials.append(silver);objects.append(skin)
bpy.context.scene.unit_settings.system='METRIC'
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
blend=H/'visible-optics-v3.blend';glb=H/'visible-optics-v3.glb'
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_animations=False,export_tangents=False)
audit=[]
for ob in objects:
 ob.data.calc_loop_triangles();audit.append({'object':ob.name,'vertices':len(ob.data.vertices),'triangles':len(ob.data.loop_triangles),'minimum_triangle_area_m2':min(p.area for p in ob.data.polygons),'material':ob.data.materials[0].name})
assert len(objects)==5 and all(a['minimum_triangle_area_m2']>0 for a in audit)
(O/'native-construction-check.json').write_text(json.dumps({'source':str(blend.relative_to(R)),'sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'objects':audit,'no_bowl':True,'no_facets':True,'no_neck_or_hidden_rear':True,'source_pixels_as_texture':False,'art_accepted':False},indent=2))
(H/'parameters.json').write_text(json.dumps({'scope':'Only visible glazing relief and silver frontal lips; hidden and ambiguous reflector regions absent','reference_normalized_transverse_y_over_R':lines,'line_placement_uncertainty_over_R':.03,'R_m':radius,'R_uncertainty_m':[.075,.100],'sag_m':sag,'sag_hypothesis_range_m':[0,.0085],'ridge_height_m':.00012,'ridge_height_authoring_range_m':[.00004,.00020],'ridge_width_m':.0004,'border_striae_count_estimated':640,'border_striae_count_range':[480,800],'border_amplitude_m':.000055,'border_amplitude_authoring_range_m':[.00002,.00010],'main_aperture_center_xy_m':[.0045,.0008],'pilot_aperture_center_xy_m':[.003,-.037],'aperture_center_authoring_uncertainty_m':.004,'visible_silver_field':'Planar front-projection approximation at z=-.00045m with source-observed outline/two holes; no bowl or optical facets.','lip_recesses_m':[.00045,.00045,.00045],'lip_recess_authoring_range_m':[0,.003],'depth_status':'Explicit appearance proposal, not recovered measurements. Profiles and glass-side ownership unconfirmed. No generic bowl is created.','material_status':'Clear, non-emissive glass IOR1.46 transmission1 roughness.025; silver lip metal1 roughness.12, estimated clean appearance','mounted_fit':False,'art_accepted':False},indent=2))
