"""Change only the distal pigtail route; retain the lower two manufactured sheaths."""
from pathlib import Path
import bpy, json, math, hashlib, sys, array
from mathutils import Vector, Euler
from mathutils.bvhtree import BVHTree
H=Path(__file__).resolve().parent; R=H.parents[2]; O=R/'creative/reviews/cockpit-cables-v3'
P=json.loads((H/'parameters-v3.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not(H/'preflight-manifest-v3.json').exists()
for k in ['baseline_source','baseline_export','baseline_parameters','baseline_report',
          'ignition_parameters','connector_snapshot_source','visor_source']:
    assert sha(R/P[k])==P[k+'_sha256']
sys.path.insert(0,str(H.parent/'throttle-control'))
from control_geometry import check_mesh, tree_world, mesh_object, material, studio, export
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
# Appending ONLY the local parts collection does not load the old linked guide scene.
with bpy.data.libraries.load(str(R/P['baseline_source']),link=False)as(a,l):
    l.collections=[P['source_collection']]
C=l.collections[0];s.collection.children.link(C)
bpy.context.view_layer.update();parts=list(C.all_objects)
assert len(parts)==3 and all(o.type=='MESH'for o in parts)
loop=next(o for o in parts if o.name==P['loop_object']);lower=[o for o in parts if o!=loop]
def signatures(o):
    m=o.data;m.calc_loop_triangles();d={}
    for name,seq,key,n in [('positions',m.vertices,'co',3),('corner_normals',m.corner_normals,'vector',3)]:
        v=array.array('f',[0.]*(len(seq)*n));seq.foreach_get(key,v);d[name]=hashlib.sha256(v.tobytes()).hexdigest()
    d['triangle_indices']=hashlib.sha256(array.array('I',[i for t in m.loop_triangles for i in t.vertices]).tobytes()).hexdigest()
    d['UV']=[[[float(x)for x in p.uv]for p in uv.data]for uv in m.uv_layers]
    d['matrix_world']=[list(q)for q in o.matrix_world]
    return d
protected={o.name:signatures(o)for o in lower}
old_loop=[v.co.copy()for v in loop.data.vertices]
BP=json.loads((R/P['baseline_parameters']).read_text())
IP=json.loads((R/P['ignition_parameters']).read_text())
rot=Euler(tuple(math.radians(v)for v in IP['datum_rotation_euler_xyz_degrees_estimated'])).to_matrix()
origin=Vector(IP['datum_origin_world_m_estimated'])
old_land=[origin+rot@Vector(v)for v in BP['ignition_pigtail']['local_control_points_m_estimated']]
land=old_land[:4]+[Vector(v)for v in P['new_last_two_world_controls_m_estimated']]
points=[]
for i in range(len(land)-1):
    a,b,c,d=[land[max(0,min(len(land)-1,j))]for j in[i-1,i,i+1,i+2]]
    for k in range(18):
        t=k/18
        points.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
points.append(land[-1]);N=48;normal=None;verts=[]
for i,p in enumerate(points):
    tangent=(points[min(i+1,len(points)-1)]-points[max(i-1,0)]).normalized()
    if normal is None:
        normal=tangent.cross(Vector((1,0,0)))
        if normal.length<.01:normal=tangent.cross(Vector((0,1,0)))
    normal=(normal-tangent*normal.dot(tangent)).normalized();binormal=tangent.cross(normal).normalized()
    for radius in[BP['ignition_pigtail']['outer_radius_m_estimated'],BP['ignition_pigtail']['inner_radius_m_estimated']]:
        for j in range(N):
            a=math.tau*j/N;verts.append(p+radius*(normal*math.cos(a)+binormal*math.sin(a)))
assert len(verts)==len(old_loop)
fixed=P['actual_unchanged_initial_axial_stations']*2*N
# Literal protected prefix, including any old float32 frame roundoff.
verts[:fixed]=old_loop[:fixed]
for v,co in zip(loop.data.vertices,verts):v.co=co
loop.data.update();bpy.context.view_layer.update()
assert all(tuple(a)==tuple(b.co)for a,b in zip(old_loop[:fixed],loop.data.vertices[:fixed]))
assert all(signatures(o)==protected[o.name]for o in lower)

# Own baked geometry guides from the refused housing study, no imported images/links.
with bpy.data.libraries.load(str(R/P['connector_snapshot_source']),link=False)as(a,l):
    l.collections=['CONNECTOR_OWN_WORLD_SNAPSHOTS_NOT_EXPORTED']
G=l.collections[0];G.name='CABLES_V3_OWN_WORLD_SNAPSHOTS_NOT_EXPORTED';s.collection.children.link(G)
G.hide_viewport=False
for o in list(G.objects):
    if o['snapshot_group']=='pigtail':bpy.data.objects.remove(o,do_unlink=True)
guide=material('Own world geometry guides only - no photos',(.10,.11,.12),0,.55)
with bpy.data.libraries.load(str(R/P['visor_source']),link=False)as(a,l):
    l.collections=['WEWA_INSTRUMENT_VISOR']
temp=l.collections[0];s.collection.children.link(temp);bpy.context.view_layer.update()
visor_rows=[]
for o in temp.all_objects:
    if o.type!='MESH':continue
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles()
    visor_rows.append((o.name,[list(o.matrix_world@v.co)for v in m.vertices],[list(t.vertices)for t in m.loop_triangles]))
    ev.to_mesh_clear()
for o in list(temp.all_objects):bpy.data.objects.remove(o,do_unlink=True)
bpy.data.collections.remove(temp)
for name,vs,fs in visor_rows:
    o=mesh_object('GUIDE '+name,vs,fs,G,guide);o['source_object']=name;o['snapshot_group']='visor'
bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
bpy.context.view_layer.update()
checks=[check_mesh(o)for o in parts];counts={}
for o in parts:
    o.data.calc_loop_triangles();assert all(t.area>0 for t in o.data.loop_triangles)
    counts[o.name]=len(o.data.loop_triangles)
tree=tree_world(loop);rows=[]
for g in G.objects:
    rows.append({'guide':g['source_object'],'group':g['snapshot_group'],
                 'surface_crossing_pairs':len(tree.overlap(tree_world(g)))})
pairs=[]
for i,a in enumerate(parts):
    for b in parts[i+1:]:pairs.append({'a':a.name,'b':b.name,'crossing_pairs':len(tree_world(a).overlap(tree_world(b)))})
# Distinct BVHs over retained triangles; coplanar contacts are outside this test.
m=loop.data;m.calc_loop_triangles();vs=[tuple(v.co)for v in m.vertices];fs=[tuple(t.vertices)for t in m.loop_triangles]
sets=[set(f)for f in fs];ta=BVHTree.FromPolygons(vs,fs,all_triangles=True);tb=BVHTree.FromPolygons(vs,fs,all_triangles=True)
self_pairs=[(a,b)for a,b in ta.overlap(tb)if a<b and not sets[a].intersection(sets[b])]
passed=not self_pairs and not any(q['surface_crossing_pairs']for q in rows)and not any(q['crossing_pairs']for q in pairs)
radii=[]
for a,b,c in zip(points,points[1:],points[2:]):
    cross=(b-a).cross(c-a).length
    if cross>1e-12:radii.append((b-a).length*(c-b).length*(c-a).length/(2*cross))
mouths=[]
for i,di in[(0,points[1]-points[0]),(-1,points[-2]-points[-1])]:
    di.normalize();hit=tree.ray_cast(points[i]+di*1e-6,di,.0015)
    mouths.append({'end':'start'if i==0 else'conditional_connector_review_cut','finite_1_5mm_ray_clear':hit[0]is None})
assert all(q['finite_1_5mm_ray_clear']for q in mouths)
G.hide_render=True;G.hide_viewport=True
stage=bpy.data.collections.new('CABLES_V3_STUDIO_NOT_EXPORTED');s.collection.children.link(stage)
studio(s,stage,Vector((.03,-.11,0)))
for o in stage.objects:
    if o.type=='MESH':o.hide_render=True
    if o.type=='LIGHT':o.data.energy*=.04
source=H/'cockpit-cables-v3.blend';glb=H/'cockpit-cables-v3-inspection.glb'
export(glb,parts,animations=False);bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
report={'component_id':P['component_id'],'revision':P['revision'],'source_sha256':sha(source),'export_sha256':sha(glb),
        'geometry':checks,'triangle_counts_by_object':counts,'protected_lower_source_signatures':protected,
        'lower_two_source_geometry_normals_UV_indices_matrices_identical':all(signatures(o)==protected[o.name]for o in lower),
        'actual_initial_axial_stations_unchanged':P['actual_unchanged_initial_axial_stations'],
        'first_four_landmark_controls_unchanged':[list(v)for v in land[:4]]==[list(v)for v in old_land[:4]],
        'actual_controls_world_m':[list(v)for v in land],
        'pigtail_arc_length_m_estimated':sum((b-a).length for a,b in zip(points,points[1:])),
        'pigtail_min_discrete_curve_radius_m':min(radii),'radius_is_manufacturer_limit':False,
        'conditional_interface_checks':rows,'part_pair_checks':pairs,'self_nonadjacent_crossings':len(self_pairs),
        'mouth_finite_rays':mouths,'conditional_interfaces_passed':passed,
        'source_libraries':len(bpy.data.libraries),'source_file_images':len([i for i in bpy.data.images if i.source=='FILE'and i.filepath]),
        'all_dimensions_estimated':True,'full_harness_created':False,'route_and_pose_are_artistic_estimates':True,
        'contacts_or_pinout_created':False,'installed_fit_received':False,'art_accepted':False}
assert report['source_libraries']==report['source_file_images']==0
for k in ['baseline_source','baseline_export','baseline_parameters','baseline_report','ignition_parameters','connector_snapshot_source','visor_source']:
    assert sha(R/P[k])==P[k+'_sha256']
(H/'build-report-v3.json').write_text(json.dumps(report,indent=2)+'\n')
(O/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n')
print('PIGTAIL_V3',json.dumps({k:report[k]for k in['source_sha256','export_sha256','pigtail_arc_length_m_estimated','pigtail_min_discrete_curve_radius_m','conditional_interfaces_passed','self_nonadjacent_crossings','lower_two_source_geometry_normals_UV_indices_matrices_identical']}),flush=True)
assert passed,{'guide_crossings':[q for q in rows if q['surface_crossing_pairs']],'pair_crossings':pairs,'self_crossings':len(self_pairs)}
