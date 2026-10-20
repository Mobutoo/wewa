"""Edit only documented icon contours from an immutable checked v1 source."""
import bpy,bmesh,json,hashlib,subprocess,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/switchgear-left-v2';OUT.mkdir(parents=True,exist_ok=True)
base=HERE/'switchgear-left-v1.blend';base_report=json.loads((HERE/'build-report.json').read_text());assert hashlib.sha256(base.read_bytes()).hexdigest()==base_report['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(base));source=bpy.data.collections['WEWA_SWITCHGEAR_LEFT'];rigid_names=[x['object'] for x in base_report['checks']]
def signature(o):
 m=o.data;row={'vertices':[list(v.co) for v in m.vertices],'polygons':[list(f.vertices) for f in m.polygons],'normals':[list(n.vector) for n in m.corner_normals],'UV':[[list(x.uv) for x in l.data] for l in m.uv_layers],'matrix':[list(r) for r in o.matrix_world],'materials':[m.name for m in o.data.materials],'parent':o.parent.name if o.parent else None};return hashlib.sha256(json.dumps(row,separators=(',',':')).encode()).hexdigest()
before={name:signature(bpy.data.objects[name]) for name in rigid_names};removed=[]
for o in list(source.objects):
 if o.name.startswith('LH print beam ') or o.name.startswith('LH print horn'):
  removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
assert len(removed)==10,removed
editable=bpy.data.collections.new('LH editable photo-traced symbol curves v2');bpy.context.scene.collection.children.link(editable)
E=Vector(base_report['datum']['endpoint_m']);I=Vector(base_report['datum']['inward_axis']);T=Vector(base_report['datum']['thumb_side_radial']);Z=Vector((0,0,1))
trees=[BVHTree.FromPolygons([v.co for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons]) for o in source.objects if o.type=='MESH' and 'shell - editable' in o.name]
def surface(q,z):
 start=E+I*q+Z*z+T*.10;hits=[t.ray_cast(start,-T,.15) for t in trees];hits=[h for h in hits if h[0] is not None];assert hits,(q,z);hit=min(hits,key=lambda h:h[3]);return hit[0],hit[1]
ink=bpy.data.materials['LH original white printed markings'];vectors=json.loads((ROOT/'creative/research/switchgear-left/marking-vector-contours-v2.json').read_text());added=[]
placements={'high_beam':(.1405,.0160,.0063),'low_beam':(.1405,.0090,.0063),'horn':(.1286,-.0215,.0079)}
for name,glyph in vectors['glyphs'].items():
 points=[p for c in glyph['components'] for loop in c['loops'] for p in loop['points_px']];xmin=min(p[0] for p in points);xmax=max(p[0] for p in points);ymin=min(p[1] for p in points);ymax=max(p[1] for p in points);left,centre_z,width=placements[name];scale=width/(xmax-xmin);centre_y=(ymin+ymax)/2
 curve=bpy.data.curves.new('Original traced '+name+' contours - editable v2','CURVE');curve.dimensions='2D';curve.resolution_u=8;curve.render_resolution_u=12;curve.fill_mode='BOTH';curve.extrude=.000018
 loops=0
 for component in glyph['components']:
  for loop in component['loops']:
   path=loop['points_px'];spline=curve.splines.new('BEZIER');spline.bezier_points.add(len(path)-1);spline.use_cyclic_u=True
   for k,(p,b) in enumerate(zip(path,spline.bezier_points)):
    b.co=(left+(p[0]-xmin)*scale,centre_z+(centre_y-p[1])*scale,0)
    a=Vector(path[k-1])-Vector(p);c=Vector(path[(k+1)%len(path)])-Vector(p);angle=math.pi-math.acos(max(-1,min(1,a.normalized().dot(c.normalized()))));handle='AUTO' if angle<.7 else 'VECTOR';b.handle_left_type=handle;b.handle_right_type=handle
   loops+=1
 o=bpy.data.objects.new('EDITABLE '+name+' white ink outline v2',curve);editable.objects.link(o);curve.materials.append(ink);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();data=bpy.data.meshes.new_from_object(o.evaluated_get(deps),depsgraph=deps)
 for v in data.vertices:
  q,z,d=v.co;point,normal=surface(q,z);v.co=point+normal*(.000035+d)
 bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(data);bm.free();data.update();visible=bpy.data.objects.new('LH print '+name+' traced contours v2',data);source.objects.link(visible);visible['printed_marking']=True;visible['function_reference']='Related JB401400 native photo, current RDC variant not certified';o.hide_render=True;o.hide_set(True);added.append({'object':visible.name,'editable_curve':o.name,'source_components':len(glyph['components']),'contour_loops':loops,'width_m_estimated':width,'photo_bounds_px':[xmin,ymin,xmax,ymax],'five_rays_documented':glyph.get('documented_visible_rays')})
editable.hide_render=True
bpy.context.view_layer.update();after={name:signature(bpy.data.objects[name]) for name in rigid_names};assert before==after,'Rigid source meshes/normals/UVs/pivots changed'
bpy.ops.object.select_all(action='DESELECT')
for o in source.objects:o.select_set(True)
bpy.context.view_layer.objects.active=bpy.data.objects[rigid_names[0]];path=HERE/'switchgear-left-v2-inspection.glb';bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True,export_tangents=True)
subprocess.run(['node',str(HERE/'finalize_export_v2.mjs')],cwd=str(ROOT),check=True)
source_path=HERE/'switchgear-left-v2.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source_path),compress=True)
report=dict(base_report);report.update({'revision':'switchgear-left-v2','source_sha256':hashlib.sha256(source_path.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'parent_revision':'switchgear-left-v1','parent_source_sha256':base_report['source_sha256'],'parent_export_sha256':base_report['export_sha256'],'only_icon_contours_changed':True,'source_rigid_geometry_normals_UV_parenting_identical':before==after,'source_rigid_signature_sha256':before,'removed_icons':removed,'new_icon_contours':added,'glyph_trace_register':'creative/research/switchgear-left/marking-vector-contours-v2.json','inherited_geometric_checks_exact_rigid_identity':True,'art_accepted':False})
(HERE/'build-report-v2.json').write_text(json.dumps(report,indent=2)+'\n');(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');print('MARKING_V2_PROTECTION',report['source_sha256'],report['export_sha256'])
