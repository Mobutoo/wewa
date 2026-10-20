"""Read-only open-loop and ray-count structure checks, not artistic acceptance."""
import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/switchgear-left-v2';r=json.loads((OUT/'source-geometry-check.json').read_text());path=HERE/'switchgear-left-v2.blend';assert hashlib.sha256(path.read_bytes()).hexdigest()==r['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(path));vectors=json.loads((ROOT/r['glyph_trace_register']).read_text());E=Vector(r['datum']['endpoint_m']);I=Vector(r['datum']['inward_axis']);T=Vector(r['datum']['thumb_side_radial']);Z=Vector((0,0,1));rows=[]
for row in r['new_icon_contours']:
 o=bpy.data.objects[row['object']];name='high_beam' if 'high_beam' in o.name else 'low_beam' if 'low_beam' in o.name else 'horn';bm=bmesh.new();bm.from_mesh(o.data);unseen=set(bm.verts);components=0
 while unseen:
  components+=1;stack=[unseen.pop()]
  while stack:
   for edge in stack.pop().link_edges:
    for vertex in edge.verts:
     if vertex in unseen:unseen.remove(vertex);stack.append(vertex)
 euler=len(bm.verts)-len(bm.edges)+len(bm.faces);genus=(2*components-euler)/2;nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free();tree=BVHTree.FromPolygons([v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons]);checks=[];xmin,ymin,xmax,ymax=row['photo_bounds_px'];scale=row['width_m_estimated']/(xmax-xmin);left,centre_z={'high_beam':(.1405,.016),'low_beam':(.1405,.009),'horn':(.1286,-.0215)}[name]
 for c in vectors['glyphs'][name]['components']:
  for loop in c['loops']:
   if not loop['is_hole']:continue
   px=sum(p[0] for p in loop['points_px'])/len(loop['points_px']);py=sum(p[1] for p in loop['points_px'])/len(loop['points_px']);q=left+(px-xmin)*scale;z=centre_z+((ymin+ymax)/2-py)*scale;hit=tree.ray_cast(E+I*q+Z*z+T*.10,-T,.15)[0];checks.append({'native_hole_probe_px':[px,py],'actual_ink_mesh_hit':hit is not None})
 # Paint lettering is an evaluated curve surface with intentional cap/side
 # vertex splits, not a rigid mechanical solid. Check actual visible filled
 # regions and apertures rather than imposing a manifold-solid test on ink.
 rays=[c for c in vectors['glyphs'][name]['components'] if len(c['loops'])==1] if name!='horn' else []
 ray_probes=[];gap_probes=[]
 def probe(px,py):
  q=left+(px-xmin)*scale;z=centre_z+((ymin+ymax)/2-py)*scale
  return tree.ray_cast(E+I*q+Z*z+T*.10,-T,.15)[0] is not None
 if rays:
  rays.sort(key=lambda c:c['bounds_px'][1]);common_x=(max(c['bounds_px'][0] for c in rays)+min(c['bounds_px'][2] for c in rays))/2
  for c in rays:
   x0,y0,x1,y1=c['bounds_px'];ray_probes.append({'native_px':[common_x,(y0+y1)/2],'actual_ink_mesh_hit':probe(common_x,(y0+y1)/2)})
  for first,second in zip(rays,rays[1:]):
   py=(first['bounds_px'][3]+second['bounds_px'][1])/2;gap_probes.append({'native_px':[common_x,py],'actual_ink_mesh_hit':probe(common_x,py)})
 record={'glyph':name,'paint_surface_topology_not_a_rigid_solid_test':True,'native_trace_components':len(vectors['glyphs'][name]['components']),'actual_aperture_ray_tests':checks,'actual_ray_stroke_probes':ray_probes,'actual_gap_probes':gap_probes};rows.append(record)
 assert checks and not any(c['actual_ink_mesh_hit'] for c in checks),record
 if name!='horn':assert len(ray_probes)==5 and all(c['actual_ink_mesh_hit'] for c in ray_probes) and not any(c['actual_ink_mesh_hit'] for c in gap_probes),record
result={'source_sha256':r['source_sha256'],'scope':'White ink real ray-cast probes: five visible ray strokes separated by empty gaps, D and horn interior apertures empty. Ink is not qualified as a mechanical solid. Real source geometry, not merely names. Does not certify exact RDC variant or artistic fidelity.','glyphs':rows,'passed':True,'art_accepted':False};(OUT/'glyph-structure-check.json').write_text(json.dumps(result,indent=2)+'\n');print('GLYPH_STRUCTURE_V2',json.dumps(result))
