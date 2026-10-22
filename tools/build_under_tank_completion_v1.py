"""Photo-inferred exterior completion. Dimensions are estimates, not Bajaj drawings.

Run: blender -b --python-exit-code 1 --python tools/build_under_tank_completion_v1.py
Coordinates below are glTF world metres (X left, Y up, Z forward).
"""
import hashlib
import json
import math
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets-src/moto-components/under-tank-completion-v1'
REVIEW = ROOT / 'creative/reviews/under-tank-completion-v1'
PLAN = ROOT / 'creative/research/under-tank-completion-v1/plan.json'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
parents = []
current = None


def xyz(p):
    return Vector((p[0], -p[2], p[1]))


def material(name, colour, metal, roughness):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*colour, 1)
    bsdf.inputs['Metallic'].default_value = metal
    bsdf.inputs['Roughness'].default_value = roughness
    return m


alloy = material('Cast aluminium - clean satin', (.44, .47, .49), .72, .34)
edge = material('Machined fastener zinc', (.42, .45, .47), .85, .24)
paint = material('Black mounting steel', (.018, .023, .028), .55, .29)
rubber = material('Rubber hose', (.013, .016, .02), 0, .64)
plastic = material('Moulded enclosure', (.024, .029, .034), 0, .42)
seam = material('Dark gasket edge', (.032, .038, .043), .1, .68)


def group(key):
    global current
    current = bpy.data.objects.new('COMPLETION [' + key + ']', None)
    scene.collection.objects.link(current)
    current['provenance'] = 'Bajaj RDC photographs; bounded visual estimate'
    current['dimensions_measured'] = False
    parents.append(current)


def finish(obj, name, mat, bevel=0):
    obj.name = name
    obj.parent = current
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Small manufactured edge radius', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
    for f in obj.data.polygons:
        f.use_smooth = True
    mod = obj.modifiers.new('Weighted planar normals', 'WEIGHTED_NORMAL')
    mod.keep_sharp = True
    return obj


def loft(name, profile, sections, mat, bevel=.003):
    """Closed casting extruded on X with independently scaled rounded shoulders.

    profile = (Y,Z); sections = (X, profile scale). Caps are triangulated on export.
    """
    centre = [sum(p[i] for p in profile)/len(profile) for i in (0, 1)]
    verts = [xyz((x, centre[0]+(y-centre[0])*s, centre[1]+(z-centre[1])*s))
             for x, s in sections for y, z in profile]
    n = len(profile)
    faces = [tuple(reversed(range(n))), tuple((len(sections)-1)*n+i for i in range(n))]
    for j in range(len(sections)-1):
        for i in range(n):
            k = (i+1) % n
            faces.append((j*n+i, j*n+k, (j+1)*n+k, (j+1)*n+i))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    bm = bmesh.new(); bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh); bm.free()
    ob = bpy.data.objects.new(name, mesh); scene.collection.objects.link(ob)
    return finish(ob, name, mat, bevel)


def cylinder(name, a, b, radius, mat, vertices=32, bevel=.0006):
    a, b = xyz(a), xyz(b)
    delta = b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius,
                                       depth=delta.length, location=(a+b)/2)
    ob = bpy.context.object
    ob.rotation_euler = delta.to_track_quat('Z', 'Y').to_euler()
    return finish(ob, name, mat, bevel)


routes = []
def hose(name, points, radius, mat=rubber):
    curve = bpy.data.curves.new(name, 'CURVE'); curve.dimensions = '3D'
    curve.resolution_u = 12; curve.bevel_depth = radius; curve.bevel_resolution = 3
    curve.use_fill_caps = True
    spline = curve.splines.new('BEZIER'); spline.bezier_points.add(len(points)-1)
    for bp, p in zip(spline.bezier_points, points):
        bp.co = xyz(p); bp.handle_left_type = 'AUTO'; bp.handle_right_type = 'AUTO'
    ob = bpy.data.objects.new(name, curve); scene.collection.objects.link(ob)
    ob.parent = current; curve.materials.append(mat)
    routes.append({'name': name, 'points_gltf_m': points, 'radius_m': radius,
                   'route_status': 'estimated; exterior static review only'})
    return ob


def bolt(name, x, y, z, side=1, radius=.006):
    cylinder(name+' washer', (x,y,z), (x+side*.0015,y,z), radius*1.35, edge)
    cylinder(name+' hex', (x+side*.0015,y,z), (x+side*.006,y,z), radius, edge, 6)


# 1. Close the centre casting, retaining the existing separately modelled side covers.
group('central-crankcase')
profile = [(-.554,-.063),(-.527,-.104),(-.529,-.172),(-.548,-.194),
           (-.536,-.246),(-.544,-.309),(-.566,-.351),(-.621,-.365),
           (-.688,-.342),(-.719,-.290),(-.727,-.145),(-.704,-.086),(-.642,-.060)]
loft('Closed central crankcase exterior', profile,
     [(-.105,.94),(-.094,1),(0,1),(.094,1),(.105,.94)], alloy, .005)
# Thin split line, visible on the upper/lower centre of the casting.
loft('Crankcase centre parting seam', profile, [(-.0007,1.002),(.0007,1.002)], seam, .0005)
for side in (-1,1):
    for i,(y,z) in enumerate([(-.552,-.249),(-.577,-.327),(-.684,-.305),(-.704,-.184)]):
        bolt(f'Crankcase {side} fastener {i}', side*.103,y,z,side,.0045)

# 2. Replace the concave incomplete sprocket-cover study with a continuous exterior.
group('left-output-cover')
outline = [(-.576,-.224),(-.566,-.257),(-.569,-.321),(-.594,-.373),
           (-.641,-.367),(-.689,-.324),(-.695,-.262),(-.669,-.229)]
loft('Output cover gasket', outline, [(.104,1),(.109,1)], seam, .002)
loft('Left transmission output cover continuous casting', outline,
     [(.108,.98),(.125,1),(.139,.86)], alloy, .004)
for i,(y,z) in enumerate([(-.591,-.261),(-.605,-.342),(-.674,-.301)]):
    bolt(f'Output cover bolt {i}',.137,y,z,1,.0048)

# 3. Lower dark enclosure visible under the side panels. Internals intentionally absent.
group('lower-electrical-enclosure')
outline = [(-.425,-.424),(-.432,-.624),(-.535,-.651),(-.589,-.579),(-.567,-.462)]
loft('Under-sidecover lower enclosure',outline,[(-.111,.95),(-.10,1),(.10,1),(.111,.95)],plastic,.006)
loft('Enclosure lower access lid', [(-.49,-.475),(-.49,-.596),(-.548,-.615),(-.568,-.566),(-.552,-.478)],
     [(.11,1),(.115,.94)],plastic,.003)
for side in (-1,1):
    for i,(y,z) in enumerate([(-.525,-.482),(-.541,-.590)]):
        bolt(f'Enclosure screw {side} {i}',side*.115,y,z,side,.0032)

# 4. Paired front mounting plates tie the motor nose to the down tube.
for side in (-1,1):
    group('front-engine-mount-'+str(side))
    outline=[(-.590,-.008),(-.582,-.045),(-.620,-.080),(-.672,-.072),(-.675,-.038)]
    x=side*.053
    loft('Front engine mounting plate '+str(side),outline,[(x-.002,1),(x+.002,1)],paint,.002)
    for i,(y,z) in enumerate([(-.600,-.027),(-.643,-.057)]):
        cylinder(f'Mount cross spacer {side} {i}',(0,y,z),(x,y,z),.009,paint)
        bolt(f'Front engine mount {side} {i}',x+side*.002,y,z,side,.006)

# 5. Visible upper stay near head, with the centre hidden under the tank tunnel.
group('upper-engine-stay')
for side in (-1,1):
    x=side*.042
    loft('Upper engine stay '+str(side),[(-.306,-.153),(-.321,-.126),(-.384,-.143),(-.397,-.163)],
         [(x-.002,1),(x+.002,1)],paint,.002)
    for i,(y,z) in enumerate([(-.326,-.146),(-.379,-.154)]):
        bolt(f'Upper stay {side} {i}',x+side*.002,y,z,side,.0045)

# 6. Coil and continuous high-tension lead to the existing cap's rear socket.
group('ignition-coil-and-lead')
cylinder('Ignition coil moulded body',(-.049,-.314,-.172),(-.049,-.314,-.237),.019,plastic)
cylinder('Ignition coil lead socket',(-.049,-.314,-.172),(-.049,-.314,-.160),.008,rubber)
loft('Coil mounting ear',[(-.300,-.185),(-.286,-.190),(-.286,-.227),(-.300,-.233)],
     [(-.052,1),(-.047,1)],paint,.001)
hose('HT lead coil to existing spark cap',[(-.049,-.314,-.161),(-.101,-.335,-.160),
     (-.133,-.376,-.132),(-.125,-.408,-.085),(-.1223,-.4234,-.0831)],.0035)

# 7. Fuel tap and carburettor are existing; connect their visible exterior ports.
group('fuel-feed')
cylinder('Fuel tap hose union',(.111,-.408,-.230),(.111,-.424,-.230),.0045,edge)
cylinder('Carb fuel inlet union',(.053,-.385,-.279),(.069,-.385,-.279),.004,edge)
hose('Fuel tap to carb hose',[(.111,-.420,-.230),(.117,-.443,-.247),
     (.095,-.440,-.281),(.079,-.405,-.284),(.067,-.385,-.279)],.0045)
for label,a,b in [('tap',(.111,-.423,-.230),(.111,-.429,-.230)),
                  ('carb',(.069,-.386,-.279),(.076,-.389,-.279))]:
    cylinder('Fuel hose retaining band '+label,a,b,.0051,edge,32,.0003)

# 8. Main loom behind the head, not a solid filler for the cooling-air opening.
group('under-tank-wiring')
hose('Main protected wiring loom',[(-.027,-.197,.119),(-.034,-.250,.040),
     (-.049,-.278,-.073),(-.058,-.300,-.238),(-.072,-.327,-.365),(-.081,-.422,-.485)],.006)
hose('Coil low tension branch',[(-.054,-.295,-.204),(-.060,-.313,-.220),(-.049,-.314,-.237)],.0024)
for i,(y,z) in enumerate([(-.282,-.100),(-.300,-.238),(-.330,-.367)]):
    cylinder('Loom clip '+str(i),(-.059,y-.003,z),(-.059,y+.003,z),.008,paint)

# 9. Throttle cable ends at existing grip guide and carburettor elbow.
group('throttle-cable')
hose('Throttle continuous outer cable',[(-.233,.073,.083),(-.183,.023,.134),
     (-.088,-.096,.138),(-.047,-.214,.037),(-.055,-.256,-.148),
     (.004,-.262,-.261),(.025,-.276,-.263)],.0026)

# Apply geometry modifiers and curves so exported triangles are what was inspected.
bpy.ops.object.select_all(action='DESELECT')
for ob in scene.objects:
    if ob.type in {'MESH','CURVE'}: ob.select_set(True)
bpy.context.view_layer.objects.active = next(o for o in scene.objects if o.type=='MESH')
bpy.ops.object.convert(target='MESH')
checks=[]
for ob in [o for o in scene.objects if o.type=='MESH']:
    bm=bmesh.new(); bm.from_mesh(ob.data)
    # Blender curve end caps duplicate ring vertices; weld only coincident seams.
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-7)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(ob.data)
    checks.append({'name':ob.name,'vertices':len(bm.verts),'faces':len(bm.faces),
                   'boundary_edges':sum(e.is_boundary for e in bm.edges),
                   'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),
                   'volume_m3':abs(bm.calc_volume(signed=True))})
    bm.free()
assert all(c['boundary_edges']==0 and c['non_manifold_edges']==0 and c['volume_m3']>0 for c in checks),checks
scene['scope']='Exterior visual reconstruction from official photos; all new dimensions estimated'
scene['art_accepted']=False
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'under-tank-completion.blend'),compress=True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'additions.glb'),export_format='GLB',
                         export_apply=True,export_cameras=False,export_lights=False)
report={'revision':'under-tank-completion-v1','component_groups':[p.name for p in parents],
        'mesh_checks':checks,'routes':routes,'new_dimensions':'estimated',
        'plan_sha256':hashlib.sha256(PLAN.read_bytes()).hexdigest(),
        'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'art_accepted':False}
(REVIEW/'native-check.json').write_text(json.dumps(report,indent=2)+'\n')
print('UNDER_TANK_NATIVE',len(parents),'groups',len(checks),'closed meshes')
