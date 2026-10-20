"""Read-only casting/interface checks; filename avoids shadowing Python inspect."""
import hashlib,json,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
REV=sys.argv[sys.argv.index('--revision')+1] if '--revision' in sys.argv else 'v2'
OUT=ROOT/('creative/reviews/front-brake-plate-'+REV)
bpy.ops.wm.open_mainfile(filepath=str(HERE/('front-brake-plate-'+REV+'.blend')))
deps=bpy.context.evaluated_depsgraph_get();obj=bpy.data.objects['Front brake panel - editable casting'];evaluated=obj.evaluated_get(deps);mesh=evaluated.to_mesh();bm=bmesh.new();bm.from_mesh(mesh)
unseen=set(bm.verts);shells=0
while unseen:
 shells+=1;pending=[unseen.pop()]
 while pending:
  v=pending.pop()
  for edge in v.link_edges:
   other=edge.other_vert(v)
   if other in unseen:unseen.remove(other);pending.append(other)
tree=BVHTree.FromPolygons([v.co for v in mesh.vertices],[tuple(p.vertices) for p in mesh.polygons])
probes={}
for name,y,z in [('axle',0,.29),('cam',-.030,.25),('socket',-.043,.318)]:
 hit=tree.ray_cast(Vector((.1,y,z)),Vector((-1,0,0)),.2);probes[name]={'surface_hit':hit[0] is not None,'first_hit_x_m':hit[0].x if hit[0] is not None else None}
for name,x,y,z,length in [('upper_cross',.041,-.004,.319,.021),('outer_cross',.0435,.036,.299,.032)]:
 hit=tree.ray_cast(Vector((x,y,z)),Vector((0,1,0)),length);probes[name]={'surface_hit':hit[0] is not None,'first_hit_y_m':hit[0].y if hit[0] is not None else None}
# The existing rim inspection has a documented sparse source deviation <50um.
# Its local hub region suffices to detect surface crossings against this candidate.
rim=bpy.data.objects['FIT Front cast rim - inspection export'];rim_mesh=rim.data
selected=[];used=set()
for poly in rim_mesh.polygons:
 points=[rim_mesh.vertices[i].co for i in poly.vertices]
 if max(p.x for p in points)>.017 and all((p.y*p.y+(p.z-.29)**2)<.09**2 for p in points):selected.append(tuple(poly.vertices));used.update(poly.vertices)
ids=sorted(used);mapping={old:i for i,old in enumerate(ids)}
rim_tree=BVHTree.FromPolygons([rim_mesh.vertices[i].co for i in ids],[tuple(mapping[i] for i in p) for p in selected]);crossings=tree.overlap(rim_tree)
reduced=bpy.data.objects['Front brake panel - inspection export'];reduced_tree=BVHTree.FromObject(reduced,deps);distances=[]
for i in range(0,len(mesh.vertices),max(1,len(mesh.vertices)//10000)):
 nearest=reduced_tree.find_nearest(mesh.vertices[i].co)
 if nearest[0] is not None:distances.append(nearest[3])
distances.sort();bounds={'min':[min(v.co[i] for v in mesh.vertices) for i in range(3)],'max':[max(v.co[i] for v in mesh.vertices) for i in range(3)]}
report={'scope':'Actual saved casting and estimated hub interface. Surface-crossing check is not a seal, tolerance or installed-brake certification. Wheel inspection source deviation documented separately.','source_sha256':hashlib.sha256((HERE/('front-brake-plate-'+REV+'.blend')).read_bytes()).hexdigest(),'vertices':len(bm.verts),'faces':len(bm.faces),'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'connected_casting_shells':shells,'signed_volume_m3':bm.calc_volume(signed=True),'bounds_blender_xyz_m':bounds,'material_faces':{m.name:sum(p.material_index==i for p in mesh.polygons) for i,m in enumerate(mesh.materials)},'bore_and_socket_probes':probes,'candidate_interface':{'rim_region_vertices':len(ids),'rim_region_faces':len(selected),'surface_triangle_crossings':len(crossings),'nominal_spigot_radial_clearance_m':.0008,'nominal_flange_axial_gap_m':.001,'nominal_central_counterbore_axial_gap_m':.0015,'all_dimensions_estimated':True,'installation_clocking_verified':False},'reduction':{'samples':len(distances),'directional_source_vertex_to_reduced_surface_max_m':max(distances),'p95_m':distances[int(.95*(len(distances)-1))],'full_hausdorff':False},'art_accepted':False}
report['loose_vertices']=sum(not v.link_faces for v in bm.verts)
report['crossing_examples']=[]
for ia,ib in crossings[:20]:
 if ia<len(mesh.polygons) and ib<len(selected):
  pc=mesh.polygons[ia].center;rc=sum((rim_mesh.vertices[i].co for i in selected[ib]),Vector())/len(selected[ib])
  report['crossing_examples'].append({'panel_face_centre':list(pc),'rim_face_centre':list(rc)})
(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n')
assert report['non_manifold_edges']==0 and shells==1 and report['signed_volume_m3']>0,report
assert not probes['axle']['surface_hit'] and not probes['cam']['surface_hit'],report
assert probes['socket']['surface_hit'] and abs(probes['socket']['first_hit_x_m']-.042)<.001,report
assert not probes['upper_cross']['surface_hit'] and not probes['outer_cross']['surface_hit'],report
assert not crossings,report
assert max(distances)<.0004,report
bm.free();evaluated.to_mesh_clear();print('WEWA_PANEL_SOURCE',json.dumps(report))
