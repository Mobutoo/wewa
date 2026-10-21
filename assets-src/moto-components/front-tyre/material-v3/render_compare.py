"""Same inspection geometry/light/camera, original nodes versus baked atlas.

All material switches are in memory. Existing source and old revisions are never
saved. Native resolution macros precede any final96/receipt claim.
"""
from pathlib import Path
import bpy,json,hashlib,sys,time
import numpy as np
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/front-tyre-v3'
sys.path.insert(0,str(H))
from camera_preflight import check_component_camera
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=H/'front-tyre-v3.blend';glb=H/'front-tyre-v3-inspection.glb'
build=json.loads((O/'material-build-report.json').read_text());check=json.loads((O/'geometry-material-buffer-check.json').read_text())
assert sha(source)==build['source_sha256']and sha(glb)==build['export_sha256']==check['export_sha256']and check['technical_passed']
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;o=bpy.data.collections['WEWA_FRONT_TYRE_V3_PORTABLE_RUBBER'].objects[0]
mapped=o.data.materials[0];native=bpy.data.materials[build['original_donor_material_retained']]
images=[]
for im in bpy.data.images:
    if im.type!='IMAGE':continue
    actual=Path(bpy.path.abspath(im.filepath));row={'name':im.name,'uri':im.filepath,'NonColor':im.colorspace_settings.name=='Non-Color',
       'packed':im.packed_file is not None,'companion_exists':actual.exists(),'companion_sha256':sha(actual)if actual.exists()else None,'size_px':list(im.size)}
    assert row['NonColor']and row['packed']and row['uri'].startswith('//')and row['companion_exists'];images.append(row)
assert len(images)==2 and not bpy.data.libraries
# The actual old/new GLB geometry check has already tested exact POSITION/N/UV0,
# indices and matrix. Here assert the actual saved native digest as well.
m=o.data;m.calc_loop_triangles();h=hashlib.sha256()
for collection,prop,width,dtype in [(m.vertices,'co',3,np.float32),(m.corner_normals,'vector',3,np.float32),(m.uv_layers[0].data,'uv',2,np.float32),(m.loops,'vertex_index',1,np.int32),(m.loop_triangles,'loops',3,np.int32)]:
    a=np.empty(len(collection)*width,dtype=dtype);collection.foreach_get(prop,a);h.update(a.tobytes())
h.update(np.array([p.use_smooth for p in m.polygons],dtype=np.uint8).tobytes());h.update(np.array(o.matrix_world,dtype=np.float64).tobytes())
assert h.hexdigest()==build['source_native_POSITION_N_UV_topology_matrix_digest']
(O/'source-portability-check.json').write_text(json.dumps({'source_sha256':sha(source),'export_sha256':sha(glb),'external_libraries':[],
 'images':images,'saved_source_native_geometry_digest_matches':True,'old_native_donor_retained_for_same_mesh_comparison':native.name,'art_accepted':False},indent=2)+'\n')
s.cycles.samples=24;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
views=[('tread-detail',(.075,-.17,.69),(.012,-.10,.562),.050,True),
       ('sidewall-detail',(.15,-.17,.52),(.035,-.12,.49),.040,True)]
jobs=[(kind,name,eye,target,scale,crop)for name,eye,target,scale,crop in views for kind in ['native','atlas']]
jobs.append(('atlas','whole-quarter',(.7,-.9,.65),(0,0,.29),.77,False))
fixture={'script_sha256':sha(Path(__file__)),'source_sha256':sha(source),'export_sha256':sha(glb),
 'samples':24,'resolution_px':[1400,1100],'exposure_EV':s.view_settings.exposure,'gamma':s.view_settings.gamma,'view_transform':s.view_settings.view_transform,
 'look':s.view_settings.look,'world_color_linear':list(s.world.node_tree.nodes['Background'].inputs['Color'].default_value),
 'world_strength':s.world.node_tree.nodes['Background'].inputs['Strength'].default_value,
 'lights':[{'name':x.name,'location_m':list(x.location),'rotation_rad':list(x.rotation_euler),'shape':x.data.shape,'power_W':x.data.energy,'size_m':x.data.size}for x in s.objects if x.type=='LIGHT']}
report={**fixture,'scope':'Same correctedG3geometry native original procedural nodes versus newly baked atlas; no detailed-master substitution, no source-save, no exactcontinuousshader or mobile parity claim.','views':[],'art_accepted':False}
for kind,name,eye,target,scale,crop in jobs:
    o.data.materials[0]=native if kind=='native'else mapped
    s.camera.location=eye;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale
    bpy.context.view_layer.update();pre=check_component_camera(s,[o],allow_crop=crop,margin=.005)
    fn='compare-'+kind+'-'+name;png=O/(fn+'.png');cp=O/(fn+'.json')
    config={**fixture,'kind':kind,'name':name,'camera_eye_m':eye,'camera_target_m':target,'ortho_scale_m':scale,'allow_intentional_crop':crop,'camera_preflight':pre}
    signature=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()
    if cp.exists():
        q=json.loads(cp.read_text());assert q['config_signature']==signature and q['PNG_sha256']==sha(png)
        report['views'].append(q);print('REUSED_VERIFIED_COMPARE_VIEW',fn,flush=True);continue
    s.render.filepath=str(png);bpy.ops.render.render(write_still=True)
    q={**config,'config_signature':signature,'PNG_sha256':sha(png),'PNG_bytes':png.stat().st_size,'source_saved':False}
    cp.write_text(json.dumps(q,indent=2)+'\n');report['views'].append(q)
    (O/'comparison-render-report.json').write_text(json.dumps(report,indent=2)+'\n')
assert sha(source)==build['source_sha256']and sha(glb)==build['export_sha256']
(O/'comparison-render-report.json').write_text(json.dumps(report,indent=2)+'\n');print('FRONT_TYRE_NATIVE_ATLAS_COMPARISON_COMPLETE',flush=True)
