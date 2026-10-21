"""Original exterior plug housing; estimated empty interior, no terminals or pinout."""
from pathlib import Path
import bpy, bmesh, math, json, hashlib, sys
from mathutils import Vector, Matrix
from mathutils.kdtree import KDTree

H = Path(__file__).resolve().parent
R = H.parents[2]
O = R / 'creative/reviews/ignition-connector-v1'
P = json.loads((H / 'parameters.json').read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert not (H / 'preflight-manifest.json').exists()
for k in ['ignition', 'pigtail', 'instruments']:
    for n in ['source', 'report']:
        assert sha(R / P[k+'_'+n]) == P[k+'_'+n+'_sha256']
sys.path.insert(0, str(H.parent / 'throttle-control'))
from control_geometry import material, mesh_object, check_mesh, tree_world, csg, studio, export

# Copy only evaluated own world geometry, then discard every imported datablock.
bpy.ops.wm.read_factory_settings(use_empty=True)
tmp = bpy.data.collections.new('READONLY_WORLD_SNAPSHOT_INPUTS')
bpy.context.scene.collection.children.link(tmp)
snapshots = []
def snapshot(o, group):
    ev = o.evaluated_get(bpy.context.evaluated_depsgraph_get())
    m = ev.to_mesh(); m.calc_loop_triangles()
    row = {'name': o.name, 'group': group,
           'positions': [list(o.matrix_world @ v.co) for v in m.vertices],
           'triangles': [list(t.vertices) for t in m.loop_triangles]}
    ev.to_mesh_clear()
    return row

for k in ['ignition', 'pigtail', 'instruments']:
    report = json.loads((R / P[k+'_report']).read_text())
    names = ([r['name'] for r in report['preflight']['geometry']] if k == 'ignition'
             else [P['pigtail_object']] if k == 'pigtail'
             else [r['object'] for r in report['structural_bodies']] + ['INSTRUMENT_CLUSTER_MOUNT'])
    with bpy.data.libraries.load(str(R / P[k+'_source']), link=False) as (a, loaded):
        loaded.objects = names
    for o in loaded.objects:
        tmp.objects.link(o)
    bpy.context.scene.frame_set(1); bpy.context.view_layer.update()
    for o in loaded.objects:
        if o.type == 'MESH':
            snapshots.append(snapshot(o, k))

wire = next(q for q in snapshots if q['group'] == 'pigtail')
wv = [Vector(v) for v in wire['positions']]
# The own v2 tube has 48 outer + 48 inner points per axial station.
end = sum(wv[-96:-48], Vector()) / 48
prev = sum(wv[-192:-144], Vector()) / 48
T = (end-prev).normalized()
Z = -T
Y = (Vector((0, 0, 1))-Z*Z.z).normalized()
X = Y.cross(Z).normalized()
origin = end + T*(P['working_wireentry_Z_m']+P['working_wireentry_gap_m'])
M = Matrix(((X.x, Y.x, Z.x, origin.x), (X.y, Y.y, Z.y, origin.y),
            (X.z, Y.z, Z.z, origin.z), (0, 0, 0, 1)))

bpy.ops.wm.read_factory_settings(use_empty=True)
s = bpy.context.scene; s.unit_settings.system = 'METRIC'; s.unit_settings.scale_length = 1
def collection(name):
    c = bpy.data.collections.new(name); s.collection.children.link(c); return c
C = collection('WEWA_IGNITION_CONNECTOR_HOUSING')
G = collection('CONNECTOR_OWN_WORLD_SNAPSHOTS_NOT_EXPORTED')
A = collection('CONNECTOR_EDITABLE_CONSTRUCTION_NOT_EXPORTED')
stage = collection('CONNECTOR_STUDIO_NOT_EXPORTED')
gray = material('Connector geometry gray - finish not received', (.19, .19, .19), 0, .46)
guide = material('Own geometry guide gray - no photographs', (.075, .085, .095), 0, .55)
guides = []
for q in snapshots:
    o = mesh_object('GUIDE '+q['name'], q['positions'], q['triangles'], G, guide)
    o['source_object'] = q['name']; o['snapshot_group'] = q['group']; guides.append(o)

NA, NS = P['samples_per_corner'], P['samples_per_straight']
K = 4*(NA+NS)
def rounded_rectangle(width, height, radius):
    assert 0 < radius < min(width, height)/2
    cx, cy = width/2-radius, height/2-radius
    corners = [(cx, cy), (-cx, cy), (-cx, -cy), (cx, -cy)]
    out = []
    for i, (x, y) in enumerate(corners):
        a0 = i*math.pi/2
        for j in range(NA):
            a = a0+math.pi*j/(2*NA)
            out.append((x+radius*math.cos(a), y+radius*math.sin(a)))
        a = a0+math.pi/2
        start = Vector((x+radius*math.cos(a), y+radius*math.sin(a)))
        nx, ny = corners[(i+1)%4]
        stop = Vector((nx+radius*math.cos(a), ny+radius*math.sin(a)))
        for j in range(NS):
            p = start.lerp(stop, j/NS); out.append(tuple(p))
    assert len(out) == K
    return out

def rail_offset(x, y, z, height):
    if abs(y-height/2) > 1e-9 or not -.0116 < z < .0035:
        return 0
    ramp = min(1., (z+.0116)/.001, (.0035-z)/.001)
    return max(0., ramp)*sum(P['rail_height_m']*(1+math.cos(math.pi*(x-c)/P['rail_halfwidth_m']))/2
        for c in P['rail_centres_X_m'] if abs(x-c) < P['rail_halfwidth_m'])

outer = P['outer_profile_Z_width_height_corner_m']
inner = P['inner_profile_Z_width_height_corner_m']
vertices, faces = [], []
for profile, is_outer in [(outer, True), (inner, False)]:
    for z, width, height, radius in profile:
        for x, y in rounded_rectangle(width, height, radius):
            vertices.append((x, y+(rail_offset(x, y, z, height) if is_outer else 0), z))
offset = len(outer)*K
def join(a, b, reverse=False):
    for j in range(K):
        v = (a+j, a+(j+1)%K, b+(j+1)%K, b+j)
        faces.extend([(v[2], v[1], v[0]), (v[3], v[2], v[0])] if reverse
                     else [(v[0], v[1], v[2]), (v[0], v[2], v[3])])
for i in range(len(outer)-1): join(i*K, (i+1)*K)
for i in range(len(inner)-1): join(offset+i*K, offset+(i+1)*K, True)
join(0, offset, True)
join((len(outer)-1)*K, offset+(len(inner)-1)*K)
body = mesh_object('Editable stepped hollow connector housing', vertices, faces, A, gray)
check_mesh(body)

# A small observed exterior projection, with estimated underside/free gap.
# Its root overlaps the wall before a true union, rather than floating on it.
verts, fs = [], []
tp = P['tongue_Z_centreY_width_thickness_m']
for z, cy, width, thickness in tp:
    for x, y in rounded_rectangle(width, thickness, .00015):
        verts.append((x, y+cy, z))
for i in range(len(tp)-1):
    for j in range(K):
        a=i*K+j; b=i*K+(j+1)%K; c=(i+1)*K+(j+1)%K; d=(i+1)*K+j
        fs += [(a,b,c), (a,c,d)]
for i, reverse in [(0, True), (len(tp)-1, False)]:
    centre = len(verts); z, cy, _, _ = tp[i]; verts.append((0,cy,z))
    for j in range(K):
        f=(centre, i*K+j, i*K+(j+1)%K); fs.append(tuple(reversed(f)) if reverse else f)
tongue = mesh_object('Editable retaining-like outer tongue - geometry estimated', verts, fs, A, gray)
check_mesh(tongue)
o, csg_report = csg(body, [tongue], [], C, gray, R,
                    'Ignition plug housing - exterior only - hollow candidate')

# Only numerical seams may be removed; no global bevel/remesh of the thin wall.
m = o.data; before = [v.co.copy() for v in m.vertices]
bm = bmesh.new(); bm.from_mesh(m)
v0, a0 = bm.calc_volume(signed=True), sum(f.calc_area() for f in bm.faces)
bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-8)
bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=1e-10)
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
for e in bm.edges:
    if e.is_manifold and e.calc_face_angle(0) > .50: e.smooth=False
v1, a1 = bm.calc_volume(signed=True), sum(f.calc_area() for f in bm.faces)
bm.to_mesh(m); bm.free(); m.update(); m.calc_loop_triangles()
assert all(t.area > 0 for t in m.loop_triangles)
kd = KDTree(len(before))
for i, p in enumerate(before): kd.insert(p, i)
kd.balance(); displacement = max(kd.find(v.co)[2] for v in m.vertices)
assert displacement < 1e-8 and abs(v1/v0-1) < 1e-6 and abs(a1/a0-1) < 1e-6
cleanup = {'retained_vertex_nearest_original_max_m': displacement,
           'volume_relative_change':v1/v0-1, 'area_relative_change':a1/a0-1,
           'no_global_bevel_or_voxel_remesh':True}
root = bpy.data.objects.new('Connector conditional pigtail rest datum - not certified', None)
C.objects.link(root); root.matrix_world=M; o.parent=root
bpy.context.view_layer.update()

# Atlas is an original per-triangle chart for now; no photo image or normal map.
uv = m.uv_layers.new(name='Original local triangle charts - no photo')
for f in m.polygons:
    points=[m.vertices[i].co for i in f.vertices]; normal=f.normal
    axis=max(range(3), key=lambda i:abs(normal[i])); axes=[i for i in range(3) if i!=axis]
    for li, p in zip(f.loop_indices, points): uv.data[li].uv=(p[axes[0]]/.04+.5,p[axes[1]]/.04+.5)
geom=check_mesh(o)
tree=tree_world(o); rows=[]
for g in guides:
    rows.append({'guide':g['source_object'],'group':g['snapshot_group'],
                 'crossing_pairs':len(tree.overlap(tree_world(g)))})
passed=not any(q['crossing_pairs'] for q in rows)
mouths=[]
for name, start, direction in [('front-empty-housing',Vector((0,0,-.0144)),Vector((0,0,1))),
                               ('rear-wireentry',Vector((0,0,.0149)),Vector((0,0,-1)))]:
    hit=tree.ray_cast(root.matrix_world@start,(root.matrix_world.to_3x3()@direction).normalized(),.005)
    mouths.append({'mouth':name,'finite5mm_centre_ray_clear':hit[0]is None})
assert all(q['finite5mm_centre_ray_clear']for q in mouths)
G.hide_render=True; G.hide_viewport=True; A.hide_render=True; A.hide_viewport=True
studio(s, stage, origin)
for q in stage.objects:
    if q.type=='MESH':q.hide_render=True
    if q.type=='LIGHT':q.data.energy*=.04
s.camera.data.clip_start=.0001
source=H/'ignition-connector-v1-geometry.blend';glb=H/'ignition-connector-v1-geometry.glb'
export(glb,[root,o]);bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
report={'component_id':P['component_id'],'source_sha256':sha(source),'export_sha256':sha(glb),
        'collection':C.name,'root':root.name,'geometry':[geom],'triangles':len(m.loop_triangles),
        'conditional_root_world_matrix':[list(q)for q in root.matrix_world],
        'pigtail_free_end_world_m':list(end),'pigtail_actual_last_tangent_world':list(T),
        'working_wireentry_gap_m':P['working_wireentry_gap_m'],
        'input_guide_sources':{k:P[k+'_source_sha256']for k in['ignition','pigtail','instruments']},
        'conditional_surface_checks':rows,'conditional_interfaces_passed':passed,
        'mouth_finite_rays':mouths,'cleanup':cleanup,'CSG':{k:v for k,v in csg_report.items()if k not in['vertices','triangles']},
        'source_libraries':len(bpy.data.libraries),'source_file_images':len([i for i in bpy.data.images if i.source=='FILE'and i.filepath]),
        'all_dimensions_estimated':True,'exact_RDC_identity_confirmed':False,
        'contacts_or_pinout_modelled':False,'installed_fit_received':False,'art_accepted':False}
assert report['source_libraries']==report['source_file_images']==0
for k in['ignition','pigtail','instruments']:assert sha(R/P[k+'_source'])==P[k+'_source_sha256']
(H/'geometry-report.json').write_text(json.dumps(report,indent=2)+'\n')
(O/'geometry-source-check.json').write_text(json.dumps(report,indent=2)+'\n')
(O/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n')
print('CONNECTOR_GEOMETRY',json.dumps({k:report[k]for k in['source_sha256','export_sha256','triangles','geometry','cleanup','conditional_interfaces_passed','mouth_finite_rays']}),flush=True)
assert passed, {'conditional_context_crossings':[q for q in rows if q['crossing_pairs']]}
