"""Bake evaluated congés, weld their collapsed float32 points, verify the retained surface.
Never fix tangents to hide duplicate-position triangles. Geometry displacement is bounded.
"""
import math,bpy,bmesh
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
def clean_evaluated(obj,retained_collection,require_closed=True):
 deps=bpy.context.evaluated_depsgraph_get();before=bpy.data.meshes.new_from_object(obj.evaluated_get(deps),depsgraph=deps);before.calc_loop_triangles()
 oldverts=[v.co.copy() for v in before.vertices];oldfaces=[tuple(t.vertices) for t in before.loop_triangles];oldtree=BVHTree.FromPolygons(oldverts,oldfaces,all_triangles=True)
 bm=bmesh.new();bm.from_mesh(before);oldvolume=bm.calc_volume(signed=True);oldarea=sum(f.calc_area() for f in bm.faces);oldcount=(len(bm.verts),len(bm.faces))
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
 bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-9)
 bmesh.ops.triangulate(bm,faces=list(bm.faces))
 bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-9)
 if not require_closed:
  # Ink can contain collinear FONT tessellation triangles. They carry no
  # printed area; remove them explicitly without closing glyph counters.
  bmesh.ops.triangulate(bm,faces=list(bm.faces))
  empty=[]
  for face in bm.faces:
   if len(face.verts)!=3:continue
   a,b,c=[tuple(v.co) for v in face.verts];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
   if math.hypot(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])==0:empty.append(face)
  bmesh.ops.delete(bm,geom=empty,context='FACES')
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 for e in bm.edges:e.smooth=e.is_manifold and e.calc_face_angle(0)<.70
 nonmanifold=sum(not e.is_manifold for e in bm.edges);newvolume=bm.calc_volume(signed=True);newarea=sum(f.calc_area() for f in bm.faces)
 if require_closed:assert nonmanifold==0 and newvolume>0,(obj.name,nonmanifold,newvolume)
 clean=bpy.data.meshes.new(obj.name+' cleaned evaluated topology');bm.to_mesh(clean);bm.free();clean.update();clean.calc_loop_triangles()
 def area(tri):
  a,b,c=[tuple(clean.vertices[i].co) for i in tri.vertices];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)];return .5*math.hypot(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
 zeros=sum(area(t)==0 for t in clean.loop_triangles);assert zeros==0,(obj.name,zeros)
 newverts=[v.co.copy() for v in clean.vertices];newfaces=[tuple(t.vertices) for t in clean.loop_triangles];newtree=BVHTree.FromPolygons(newverts,newfaces,all_triangles=True)
 oldkd=KDTree(len(oldverts))
 for i,v in enumerate(oldverts):oldkd.insert(v,i)
 oldkd.balance();retained_drift=max(oldkd.find(v)[2] for v in newverts)
 forward=max(newtree.find_nearest(v)[3] for v in oldverts);reverse=max(oldtree.find_nearest(v)[3] for v in newverts)
 volume_relative=abs(newvolume-oldvolume)/abs(oldvolume) if oldvolume else None;area_relative=abs(newarea-oldarea)/oldarea
 assert retained_drift<=3e-7 and max(forward,reverse)<=3e-7,(obj.name,retained_drift,forward,reverse)
 if require_closed:assert volume_relative<1e-6 and area_relative<1e-5,(obj.name,volume_relative,area_relative)
 retained=bpy.data.objects.new(obj.name+' - rejected degenerate evaluated mesh retained',before);retained_collection.objects.link(retained);retained.matrix_world=obj.matrix_world.copy();retained.hide_render=True;retained.hide_set(True)
 for mat in obj.data.materials:clean.materials.append(mat)
 obj.modifiers.clear();obj.data=clean
 normal=obj.modifiers.new('Planar faces and real sharp edges after weld','WEIGHTED_NORMAL');normal.keep_sharp=True;normal.weight=50;normal.mode='FACE_AREA_WITH_ANGLE'
 for p in clean.polygons:p.use_smooth=True
 return {'name':obj.name,'before_vertices_faces':oldcount,'after_vertices_faces':[len(clean.vertices),len(clean.polygons)],'weld_distance_m':1e-7,'degenerate_distance_m':1e-9,'retained_vertex_to_original_vertex_max_m':retained_drift,'old_vertices_to_clean_surface_max_m':forward,'clean_vertices_to_old_surface_max_m':reverse,'volume_before_m3':oldvolume,'volume_after_m3':newvolume,'volume_relative_delta':volume_relative,'area_relative_delta':area_relative,'non_manifold_edges_after':nonmanifold,'zero_area_triangles_after':zeros,'tangents_repaired':False}
