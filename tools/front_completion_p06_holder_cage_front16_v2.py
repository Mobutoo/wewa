"""New DF201058 exposed molded cage; photo-constrained diagnostic, no hidden back."""
import bpy,bmesh,math,json,runpy
from pathlib import Path
R=Path('/workspace/wewa');K='front-completion-p06-holder-cage-front16-v2';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K
H.mkdir(exist_ok=False);O.mkdir(exist_ok=False);bpy.ops.wm.read_factory_settings(use_empty=True)
u=runpy.run_path(str(R/'tools/front_completion_front10_mesh_helpers_v1.py'));N=384
def delta(a,b):return (a-b+math.pi)%(2*math.pi)-math.pi
def bump(a,c,half):
 t=abs(delta(a,math.radians(c)))/math.radians(half)
 return 0 if t>=1 else u['smooth'](min(1,(1-t)*5))
# Each observed lobe/key is specified separately, no unseen circumferential pattern.
lobes=[(28,43,.0024),(151,45,.0028),(273,41,.0022)]
keys=[(89,8,.0020),(209,7,.0017),(331,9,.0021)]
def outer(a):return sum(h*bump(a,c,w) for c,w,h in lobes+keys)
def bore(a):return .0012*bump(a,6,12)+.0008*bump(a,116,10)+.0010*bump(a,242,14)
# Outer exposed skin and front steps; bottom closure is temporary for booleans and removed.
profile=[(.0210,-.0030,'o'),(.0210,-.0003,'o'),(.0208,.0003,'o'),(.0170,.0003,''),(.0153,.0003,''),(.0149,.0007,''),(.0147,.0027,''),(.0144,.0033,''),(.0119,.0033,'i'),(.0115,.0029,'i'),(.0115,-.0030,'i')]
v=[]
for rr,z,kind in profile:
 for j in range(N):
  a=2*math.pi*j/N;r=rr+(outer(a) if kind=='o' else bore(a) if kind=='i' else 0);v.append((r*math.cos(a),r*math.sin(a),z))
f=[]
for i in range(len(profile)):
 for j in range(N):a=i*N+j;b=i*N+(j+1)%N;c=((i+1)%len(profile))*N;f.append((a,b,c+(j+1)%N,c+j))
ob=u['mesh_object']('DF201058_FRONT_CAGE_EXPOSED_MOLDED_SKIN_NO_CONTACTS_OR_HIDDEN_BACK',v,f);u['orient'](ob)
cuts=[]
def slot(angle,r,width,length,label):
 a=math.radians(angle);bpy.ops.mesh.primitive_cube_add(size=1,location=(r*math.cos(a),r*math.sin(a),0));c=bpy.context.object;c.rotation_euler.z=a;c.dimensions=(length,width,.030);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);u['boolean'](ob,c,'DIFFERENCE');cuts.append({'angle_deg':angle,'radius_m':r,'tangent_width_m':width,'radial_length_m':length,'label':label})
# Exposed contact windows: two broad openings and two narrow retaining apertures, not contacts.
slot(-4,.0149,.0060,.0039,'Large contact window A from poses0..3')
slot(-41,.0151,.0051,.0037,'Large contact window B from poses0..3')
slot(101,.0158,.0057,.0020,'Metal-retainer window, metal excluded')
slot(266,.0157,.0054,.0014,'Narrow retaining aperture')
# Three independently visible perimeter keys with adjacent molding gaps, finite bounded contours.
for spec in [(79,.0220,.0014,.008),(99,.0224,.0015,.008),(200,.0223,.0013,.008),(219,.0220,.0016,.008),(321,.0221,.0015,.008),(341,.0222,.0014,.008)]:slot(*spec,'Visible perimeter key side gap')
# Three source-observed shallow arc channels, individually authored, working depth only.
channels=[(8,66,.0189,.00055),(128,184,.0192,.00050),(247,307,.0187,.00060)]
for aa,bb,rr,rad in channels:
 verts=[];faces=[];nt=80;nc=16
 for i in range(nt+1):
  a=math.radians(aa+(bb-aa)*i/nt)
  for j in range(nc):
   q=2*math.pi*j/nc;r=rr+rad*math.cos(q);verts.append((r*math.cos(a),r*math.sin(a),.0003+rad*math.sin(q)))
 for i in range(nt):
  for j in range(nc):a=i*nc+j;b=i*nc+(j+1)%nc;faces.append((a,b,b+nc,a+nc))
 faces.append(tuple(reversed(range(nc))));faces.append(tuple(nt*nc+j for j in range(nc)))
 cutter=u['mesh_object']('Individually observed shallow front arc channel',verts,faces);u['boolean'](ob,cutter,'DIFFERENCE')

# Remove temporary hidden planar closure: two or more source-bounded review loops remain open.
bm=bmesh.new();bm.from_mesh(ob.data);back=[p for p in bm.faces if all(abs(v.co.z+.003)<1e-7 for v in p.verts)];bmesh.ops.delete(bm,geom=back,context='FACES');bm.to_mesh(ob.data);bm.free();ob.data.update()
bm=bmesh.new();bm.from_mesh(ob.data);nb=sum(e.is_boundary for e in bm.edges);bm.free();audit=u['clean_audit'](ob,expected_boundary=nb)
for p in ob.data.polygons:
 if abs(p.normal.z)>.999999:p.use_smooth=False
(H/'parameters.json').write_text(json.dumps({'package':'P06','code':'DF201058','source':'front16 PH holder poses0..4and7 actually read, package exact code pose7','all_working_dimensions_estimated':True,'profile_r_z_kind_m':profile,'individually_authored_lobes':lobes,'individually_authored_keys':keys,'cutouts':cuts,'bounds_m':{'maximum_radius':[.021,.028],'height':[.004,.010],'plate_gauge':[.001,.004]},'scope':'Exposed front molded cage and visible bore/aperture walls. Three independently authored source-visible shallow arc channels; working depths estimated. Hidden backside removed, no duplicated boot/lead/plug, no contacts or internal mechanism.','target_socket_fit':False,'material':'Gray-white polymer hypothesis, no resin certified'},indent=2))
(O/'geometry-check.json').write_text(json.dumps({'objects':[audit],'removed_temporary_back_faces':len(back),'exterior_study_only':True},indent=2))
(O/'child-plan.json').write_text(json.dumps({'package':'P06','component_id':'MOTO-HOLDER-DF201058-FRONT-CAGE-EXTERIOR-STUDY-001','child':'DF201058 front molded cage exposed skin','scope':'Photo-constrained exposed molded front face, stepped bore, asymmetric perimeter and actual apertures. Estimated dimensions and local depth; no hidden back, internal mechanism, contacts, boot, loom or plug duplication. Diagnostic form comparison required.','protocols':['front_completion_p06_holder_cage_front16_v2.py','front_completion_front10_mesh_helpers_v1.py','front_completion_front14_render_v1.py'],'remaining':['Inner bore local notch depth and keyed contour require calibrated comparison','Calibrated dimensions and exact target assembly','Hidden rear attachments/contact connectivity']},indent=2))
u['gray_save'](H,'holder-cage',[ob])
