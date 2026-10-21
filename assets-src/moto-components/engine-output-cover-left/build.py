"""One separately formed LH rear shell from related PF541287 photo, not a chaincase.
CurrentRDC variant, invisible thickness and gear legend remain unconfirmed.
"""
from pathlib import Path
import bpy,bmesh,numpy as np,json,math,sys,hashlib
from mathutils import Vector,Matrix
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/engine-output-cover-left-v1';OUT.mkdir(exist_ok=True);P=json.loads((HERE/'parameters.json').read_text());sys.path.insert(0,str(HERE));from formed_shell import smooth_curve,inside,edge_distance,cdt_slab
sys.path.insert(0,str(HERE.parent/'throttle-control'));from control_geometry import material,mesh_object,cylinder,csg,check_mesh,tree_world,studio
sys.path.insert(0,str(HERE.parent/'clutch-control'));from topology_cleanup_v2 import clean_evaluated
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
source=bpy.data.collections.new('WEWA_ENGINE_OUTPUT_COVER_LEFT');s.collection.children.link(source)
construction=bpy.data.collections.new('ENGINE_OUTPUT_COVER_RETAINED_CONSTRUCTION');s.collection.children.link(construction)
guides=bpy.data.collections.new('ENGINE_OUTPUT_COVER_IMMUTABLE_INTERFACE_GUIDES');s.collection.children.link(guides)
stage=bpy.data.collections.new('ENGINE_OUTPUT_COVER_STUDIO_NOT_EXPORTED');s.collection.children.link(stage)
paint=material('LH rear shell silver coating - estimated PBR',(.43,.45,.47),.20,.40)
a=math.radians(P['photo_inplane_rotation_degrees_working']);cx,cy=P['photo_origin_uv_px'];scale=P['pixel_scale_working_m']
def project(px):
 x,y=px[0]-cx,px[1]-cy;return Vector(((x*math.cos(a)-y*math.sin(a))*scale,-(x*math.sin(a)+y*math.cos(a))*scale))
outline=smooth_curve([project(p) for p in P['outline_uv_px']],7);panel=smooth_curve([project(p) for p in P['panel_outline_uv_px']],7)
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def height(p):
 bow=.010+P['face_bow_depth_working_m']*math.exp(-((p.x+.015)/.060)**2-((p.y+.010)/.080)**2)
 distance=edge_distance(p,panel);signed=distance if inside(p,panel) else -distance
 formed=P['panel_raise_working_m']*smooth(.5+signed/P['panel_transition_width_working_m'])
 lip=.0025*math.exp(-(edge_distance(p,outline)/.0035)**2)
 return bow+formed+lip
verts,faces,cdtcheck=cdt_slab(outline,P['wall_working_m'],pitch=.0011);base=mesh_object('Original flat concave thin-wall construction before forming',verts,faces,construction,paint)
# Build edge radius while the plate is flat; reject a bad thin-body result here.
bevel=base.modifiers.new('Pre-form small perimeter lip radius estimate','BEVEL');bevel.width=P['edge_radius_working_m'];bevel.segments=3;bevel.limit_method='ANGLE';bevel.angle_limit=.8
bpy.context.view_layer.update();flat_cleanup=clean_evaluated(base,construction);base.modifiers.clear();bpy.ops.object.select_all(action='DESELECT');base.select_set(True);bpy.context.view_layer.objects.active=base;bpy.ops.mesh.customdata_custom_splitnormals_clear()
for v in base.data.vertices:v.co.z+=height(Vector((v.co.x,v.co.y)))
base.data.update();bpy.context.view_layer.update();formed_check=check_mesh(base)
p=project(P['visible_lower_boss_uv_px']);h=height(p)
# A moulded rounded mounting shoulder is integral, not a separate bolt or a block.
section=[(h-.0035,0),(h-.0035,.0058),(h-.001,.0067),(h+.001,.0064),(h+.0027,.0050),(h+.0032,.0042),(h+.0032,0)]
def revolve(name,section,n=128):
 vv=[];rings=[];ff=[]
 for w,r in section:
  if r==0:rings.append([len(vv)]*n);vv.append((p.x,p.y,w))
  else:rings.append(list(range(len(vv),len(vv)+n)));vv.extend((p.x+r*math.cos(math.tau*i/n),p.y+r*math.sin(math.tau*i/n),w) for i in range(n))
 for k in range(len(section)):
  if section[k][1]==0 and section[(k+1)%len(section)][1]==0:continue
  for i in range(n):
   j=(i+1)%n;f=list(dict.fromkeys([rings[k][i],rings[(k+1)%len(section)][i],rings[(k+1)%len(section)][j],rings[k][j]]))
   if len(f)>=3:ff.append(tuple(f))
 return mesh_object(name,vv,ff,construction,paint)
shoulder=revolve('Visible rounded mounting shoulder construction',section)
bore=cylinder('Visible mounting through bore candidate',(p.x,p.y,h),P['visible_bore_radius_working_m'],.10,construction,axis=(0,0,1),n=128)
bpy.context.view_layer.update();body,operations=csg(base,[shoulder],[bore],source,paint,ROOT,'LH rear output cover formed hollow wall - editable candidate');cleanup=clean_evaluated(body,construction);body.modifiers.clear();bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body;bpy.ops.mesh.customdata_custom_splitnormals_clear();body.data.update()
for polygon in body.data.polygons:polygon.use_smooth=True
# All faces receive a nondegenerate physical projection, including perimeter/bore walls.
uv=body.data.uv_layers.new(name='Estimated silver coating 6mm projection')
for f in body.data.polygons:
 axis=max(range(3),key=lambda k:abs(f.normal[k]));components={0:(1,2),1:(0,2),2:(0,1)}[axis]
 for li in f.loop_indices:
  co=body.data.vertices[body.data.loops[li].vertex_index].co;uv.data[li].uv=(co[components[0]]/P['original_grain_tile_working_m'],co[components[1]]/P['original_grain_tile_working_m'])
# Probe actual evaluated openings; closed solid topology alone cannot prove them.
from mathutils.bvhtree import BVHTree
m=body.to_mesh();probe_tree=BVHTree.FromPolygons([v.co for v in m.vertices],[tuple(f.vertices) for f in m.polygons]);body.to_mesh_clear();opening_probes={}
for label,photo_point in [('visible_bore',P['visible_lower_boss_uv_px']),('front_clearance',[120,800]),('rear_clearance',[810,375])]:
 point=project(photo_point);hit=probe_tree.ray_cast(Vector((point.x,point.y,-.04)),Vector((0,0,1)),.14);opening_probes[label]=hit[0] is None;assert opening_probes[label],('Blocked expected open area',label,hit)
grain=None;tangent_check=None
if P.get('use_original_grain_normal_map',False):
 from coating_texture import apply_original_grain
 grain=apply_original_grain(paint,HERE/'textures',uv.name,tile_m=P['original_grain_tile_working_m'],height_rms_m=P['original_grain_height_RMS_working_m'])
 body.data.calc_tangents(uvmap=uv.name);unit=max(abs(loop.tangent.length-1) for loop in body.data.loops);orth=max(abs(body.data.corner_normals[loop.index].vector.dot(loop.tangent)) for loop in body.data.loops);bad_sign=sum(abs(abs(loop.bitangent_sign)-1)>1e-6 for loop in body.data.loops)
 tangent_check={'max_unit_length_error':unit,'max_abs_dot_normal':orth,'invalid_handedness':bad_sign,'repaired':False};assert unit<1e-4 and orth<1e-4 and bad_sign==0,tangent_check
x,y,z=P['datum_world_m'];datum=bpy.data.objects.new('LH rear output cover provisional datum',None);source.objects.link(datum);datum.matrix_world=Matrix(((0,0,1,x),(1,0,0,y),(0,1,0,z),(0,0,0,1)));body.parent=datum
body['all_dimensions_estimated']=True;body['exact_RDC_part_certified']=False;body['gear_legend_reproduced']=False;body['art_accepted']=False
parent=HERE.parent/'engine-cover-left/engine-cover-left-v1.blend';parent_sha=hashlib.sha256(parent.read_bytes()).hexdigest();assert parent_sha=='7e27606ef19b7a49e932ac13841b1da15c6d0d4936f1cef8f095bb233c3ce1d4'
with bpy.data.libraries.load(str(parent),link=True) as (available,loaded):loaded.objects=['Engine LH cover provisional datum','LH magneto cover hollow casting - editable candidate']
for o in loaded.objects:guides.objects.link(o)
bpy.context.view_layer.update();crossings=len(tree_world(bpy.data.objects['LH magneto cover hollow casting - editable candidate']).overlap(tree_world(body)))
checks=check_mesh(body);construction.hide_render=True;construction.hide_viewport=True;guides.hide_render=True;guides.hide_viewport=True
# The gray geometry pass is archived privately; grain adds source images/UV tangents only.
bpy.ops.object.select_all(action='DESELECT');datum.select_set(True);body.select_set(True);bpy.context.view_layer.objects.active=body;bpy.ops.export_scene.gltf(filepath=str(HERE/'engine-output-cover-left-inspection.glb'),export_format='GLB',use_selection=True,export_apply=True,export_tangents=bool(grain))
points=[body.matrix_world@Vector(p) for p in body.bound_box];target=sum(points,Vector())/len(points);studio(s,stage,target)
for o in stage.objects:
 if o.type=='MESH':o.location.z=min(p.z for p in points)-.002
 if o.type=='LIGHT':o.data.energy*=.08
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'engine-output-cover-left-v1.blend'),compress=True)
report={'component_id':P['component_id'],'source_sha256':hashlib.sha256((HERE/'engine-output-cover-left-v1.blend').read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((HERE/'engine-output-cover-left-inspection.glb').read_bytes()).hexdigest(),'collection':source.name,'geometry':[checks],'CDT':cdtcheck,'flat_preform_cleanup':flat_cleanup,'formed_before_union_geometry':formed_check,'final_cleanup':cleanup,'custom_normals_present':body.data.has_custom_normals,'related_parent_source_sha256':parent_sha,'surface_crossings_parent_LH_cover':crossings,'mounting_interface_certified':False,'complete_fastening_layout_known':False,'gear_legend_reproduced':False,'original_grain_maps_created':bool(grain),'original_grain':grain,'source_tangents':tangent_check,'actual_openings_probes':opening_probes,'datum_world_m_estimated':P['datum_world_m'],'basis_local_u_v_w_world':[[0,1,0],[0,0,1],[1,0,0]],'bounds_world_m':{'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)]},'all_dimensions_estimated':True,'art_accepted':False,'physical_iphone_tested':False}
(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps({'preflight':report,'CSG':{k:v for k,v in operations.items() if k not in ['vertices','triangles']}},indent=2)+'\n');print('WEWA_REAR_COVER_PREFLIGHT',json.dumps(report))
