"""Separate original LH magneto casting candidate. Current RDC small/occluded relief unresolved.
Explicitly not a mirrored RH cover, nor a recovered inner magneto housing.
"""
from pathlib import Path
import bpy,bmesh,json,sys,math,hashlib
from mathutils import Vector,Matrix
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/engine-cover-left-v1';P=json.loads((HERE/'parameters.json').read_text());sys.path.insert(0,str(HERE));from hollow_profile_loft import closed_loft
sys.path.insert(0,str(HERE.parent/'throttle-control'));from control_geometry import material,mesh_object,cylinder,csg,check_mesh,export,studio
sys.path.insert(0,str(HERE.parent/'clutch-control'));from topology_cleanup_v2 import clean_evaluated
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
source=bpy.data.collections.new('WEWA_ENGINE_COVER_LEFT');s.collection.children.link(source)
construction=bpy.data.collections.new('ENGINE_COVER_LEFT_RETAINED_CONSTRUCTION');s.collection.children.link(construction)
stage=bpy.data.collections.new('ENGINE_COVER_LEFT_STUDIO_NOT_EXPORTED');s.collection.children.link(stage)
paint=material('LH engine silver coated casting - estimated PBR',(.43,.45,.47),.20,.40);scale=P['pixel_scale_working_m'];cx,cy=P['mapping_origin_uv_px'];outline_uv=[((x-cx)*scale,(cy-y)*scale) for x,y in P['outline_uv_px']];main=Vector(((P['main_boss_uv_px'][0]-cx)*scale,(cy-P['main_boss_uv_px'][1])*scale))
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def height(p,t):
 base=.005+.015*smooth((1-t)/.15);d=(p-main).length
 # One wide forward circular boss, smoothly joined to its own upper perimeter.
 return base+.023*smooth((.072-d)/.016)
verts,faces,outline=closed_loft(outline_uv,height,wall=P['wall_working_m']);base=mesh_object('LH original asymmetric hollow loft construction',verts,faces,construction,paint)
features=[];drills=[]
for k,(x,y) in enumerate(P['visible_fixation_candidate_uv_px']):
 p=Vector(((x-cx)*scale,(cy-y)*scale));a=math.atan2(p.y,p.x);near=min(outline,key=lambda q:abs(math.atan2(math.sin(math.atan2(q.y,q.x)-a),math.cos(math.atan2(q.y,q.x)-a))));depth=height(p,p.length/near.length)+.001
 features.append(cylinder('LH visible fixation collar candidate '+str(k+1),(p.x,p.y,depth/2),.0057,depth,construction,paint,axis=(0,0,1),n=80));drills.append(cylinder('LH provisional fixation bore '+str(k+1),(p.x,p.y,.025),P['fastener_bore_working_m'],.12,construction,axis=(0,0,1),n=80))
bpy.context.view_layer.update();body,operations=csg(base,features,drills,source,paint,ROOT,'LH magneto cover hollow casting - editable candidate');cleanup=clean_evaluated(body,construction)
body.modifiers.clear();bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body;bpy.ops.mesh.customdata_custom_splitnormals_clear();body.data.update()
for p in body.data.polygons:p.use_smooth=True
x,y,z=P['datum_world_m'];datum=bpy.data.objects.new('Engine LH cover provisional datum',None);source.objects.link(datum);datum.matrix_world=Matrix(((0,0,1,x),(1,0,0,y),(0,1,0,z),(0,0,0,1)));body.parent=datum;assert abs(datum.matrix_world.to_3x3().determinant()-1)<1e-6
body['all_dimensions_estimated']=True;body['exact_RDC_part_certified']=False;body['related_three_relief_sectors_copied']=False;body['art_accepted']=False
construction.hide_render=True;construction.hide_viewport=True;bpy.context.view_layer.update();checks=check_mesh(body)
from mathutils.bvhtree import BVHTree
m=body.to_mesh();tree=BVHTree.FromPolygons([v.co for v in m.vertices],[tuple(f.vertices) for f in m.polygons]);body.to_mesh_clear();roof=tree.ray_cast(Vector((0,0,-.04)),Vector((0,0,1)),.14);assert roof[0] is not None and roof[0].z>.02,('Rear cavity absent',roof)
export(HERE/'engine-cover-left-inspection.glb',[datum,body]);points=[body.matrix_world@Vector(p) for p in body.bound_box];target=sum(points,Vector())/len(points);studio(s,stage,target)
for o in stage.objects:
 if o.type=='MESH':o.location.z=min(p.z for p in points)-.002
 if o.type=='LIGHT':o.data.energy*=.08
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'engine-cover-left-v1.blend'),compress=True)
report={'id':P['id'],'source_sha256':hashlib.sha256((HERE/'engine-cover-left-v1.blend').read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((HERE/'engine-cover-left-inspection.glb').read_bytes()).hexdigest(),'collection':source.name,'geometry':[checks],'topology_cleanup':cleanup,'custom_normals_present':body.data.has_custom_normals,'normal_policy':'No inherited custom normals; dense smooth curved skin with real sharp openings','rear_cavity_roof_local_w_m':roof[0].z,'basis_local_u_v_w_world':[[0,1,0],[0,0,1],[1,0,0]],'datum_world_m_estimated':P['datum_world_m'],'world_basis_determinant':datum.matrix_world.to_3x3().determinant(),'bounds_world_m':{'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)]},'gasket_plane_and_hidden_interfaces_certified':False,'related_three_relief_sectors_copied':False,'current_RDC_face_relief_unresolved':True,'complete_fixation_count_known':False,'all_dimensions_estimated':True,'art_accepted':False,'physical_iphone_tested':False}
(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps({'preflight':report,'CSG':{k:v for k,v in operations.items() if k not in ['vertices','triangles']}},indent=2)+'\n');print('WEWA_LH_COVER_PREFLIGHT',json.dumps(report))
