import bpy,sys,json,hashlib,math
from pathlib import Path
R=Path('/workspace/wewa');old,new=sys.argv[sys.argv.index('--')+1:][:2];H=R/'assets-src/moto-components'/new;O=R/'creative/reviews'/new;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True);bpy.context.preferences.filepaths.save_version=0;source=next((R/'assets-src/moto-components'/old).glob('*.blend'));bpy.ops.wm.open_mainfile(filepath=str(source));obs=[o for o in bpy.data.objects if o.type=='MESH']
def geometry(m):return hashlib.sha256(repr(([tuple(v.co)for v in m.vertices],[tuple(p.vertices)for p in m.polygons])).encode()).hexdigest()
reports=[]
for ob in obs:
 m=ob.data;before=geometry(m)
 for f in m.polygons:f.use_smooth=True
 m.set_sharp_from_angle(angle=math.radians(38));m.update();reports.append({'object':ob.name,'position_topology_digest_before':before,'after':geometry(m),'unchanged':geometry(m)==before})
 bpy.context.view_layer.objects.active=ob
bpy.ops.wm.save_as_mainfile(filepath=str(H/'gray.blend'),compress=True);bpy.ops.object.select_all(action='DESELECT')
for ob in obs:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(H/'gray.glb'),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False)
(O/'normal-revision.json').write_text(json.dumps({'prior':old,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'method':'Fresh source corner normals via smooth faces and 38-degree authored sharp edges. No buffers edited; exact positions and topology conserved.','objects':reports,'art_accepted':False},indent=2))
