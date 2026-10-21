"""P14 independently bounded split clamping collar; no invented spline teeth or installation fit."""
import bpy,sys,json,math,bmesh
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source,bounds,sha,write
R=Path(__file__).resolve().parents[1];name='gear-selector-split-hub-v1';H=R/'assets-src/moto-components'/name;O=R/'creative/reviews'/name;H.mkdir(parents=True,exist_ok=True)
P={'schema':1,'package':'P14','component_id':'MOTO-GEAR-SELECTOR-SPLIT-HUB-001','source':'creative/research/powertrain-completion-p14-v1/plan.json','outer_diameter_m':.027,'outer_diameter_range_m':[.023,.032],'plain_bore_diameter_m':.0134,'bore_diameter_range_m':[.011,.018],'axial_length_m':.026,'length_range_m':[.017,.034],'slot_width_m':.002,'slot_width_range_m':[.0012,.0035],'slot_stop_z_m':.022,'slot_stop_z_range_m':[.016,.024],'all_dimensions_estimated':True,'angular_samples':192,'scope':'Photo-observed split collar, open plain bore and finite rounded slit. Spline teeth/count unreadable and omitted. Bolt ears/hardware and root union to previous arm remain separate; no certified fit/clocking.','material':{'name':'Proposed dark coated selector collar','base_color_linear':[.018,.021,.024,1],'metallic':.55,'roughness':.33},'package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
# Chamfered closed annular section, then actual finite slit booleans; no generic solid-cylinder substitute.
profile=[(.0072,0),(.0130,0),(.0135,.0005),(.0135,.0255),(.0130,.026),(.0072,.026),(.0067,.0255),(.0067,.0005)];V=[];F=[];N=192
for r,z in profile:
 for i in range(N):a=math.tau*i/N;V.append((r*math.cos(a),r*math.sin(a),z))
for k in range(len(profile)):
 a=k*N;b=((k+1)%len(profile))*N
 for i in range(N):j=(i+1)%N;F.append((a+i,a+j,b+j,b+i))
ob=mesh_object('SELECTOR_SPLIT_CLAMP_COLLAR_PLAIN_BORE',V,F)
def cut(tool):
 bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Actual slit cut','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,.011,.010));tool=bpy.context.object;tool.dimensions=(.002,.022,.024);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);cut(tool)
bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.001,depth=.022,location=(0,.011,.022),rotation=(math.pi/2,0,0));cut(bpy.context.object)
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
for f in bm.faces:
 f.smooth=abs(f.normal.z)<.9 and abs(f.normal.x)<.99
for e in bm.edges:e.smooth=not(e.is_manifold and e.calc_face_angle(0)>math.radians(35))
bm.to_mesh(ob.data);bm.free();ob.data.update();ob['scope']=P['scope'];finish_source(H,O,P)
c,size,lo,hi=bounds();bpy.context.scene.camera.data.ortho_scale=2.15*size;bpy.ops.wm.save_as_mainfile(filepath=str(H/'child-gray.blend'),compress=True);report=json.loads((O/'geometry-check.json').read_text());report['source_sha256']=sha(H/'child-gray.blend');write(O,'geometry-check.json',report)
