"""One original JK113008 visible-envelope exemplar; diagnostic underside omission, no seat/retention invention."""
import bpy,math,json,sys,hashlib
from pathlib import Path
from collections import Counter
from mathutils import Vector
R=Path('/workspace/wewa');K='passenger-footrest-rubber-jk113008-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;D=R/'creative/research'/K
sys.path.insert(0,str(R/'tools'));import powertrain_completion_common_open_v1 as common
COL='WEWA_PASSENGER_FOOTREST_RUBBER_JK113008_V1';OBJECT='JK113008_PASSENGER_RUBBER_VISIBLE_ENVELOPE_ONLY'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def rounded_profile(points):
 result=[points[0]]
 for a,b,c in zip(points,points[1:],points[2:]):
  u=tuple(.2*a[i]+.8*b[i]for i in range(2));v=tuple(.8*b[i]+.2*c[i]for i in range(2));result.append(u)
  for j in range(1,9):
   t=j/8;result.append(tuple((1-t)**2*u[i]+2*(1-t)*t*b[i]+t*t*v[i]for i in range(2)))
 result.append(points[-1]);return result

def build():
 assert (D/'dedup-and-G1.json').exists();bpy.ops.wm.read_factory_settings(use_empty=True)
 near=rounded_profile([(.003,.0132),(.001,.0132),(.00025,.0134),(0,.014),(0,.0195),(.0003,.0205),(.001,.021),(.002,.0209),(.004,.0193),(.007,.0167),(.010,.015)])
 centers=[.014+i*(.072/13)for i in range(14)]
 def radius(x):
  h=0
  for c in centers:
   t=abs(x-c)/.0022
   if t<.4:q=1
   elif t<1:q=.5*(1+math.cos(math.pi*(t-.4)/.6))
   else:q=0
   h=max(h,.0016*q)
  return .015+h
 body=[(.010+.080*i/540,radius(.010+.080*i/540))for i in range(1,541)]
 far=rounded_profile([(.090,.015),(.093,.0155),(.096,.0185),(.098,.0205),(.099,.021),(.100,.0207)])[1:]
 profile=near+body+far;segments=192;V=[];F=[]
 for x,r in profile:
  for j in range(segments):a=math.radians(-45+360*j/segments);V.append((x,r*math.cos(a),r*math.sin(a)))
 for i in range(len(profile)-1):
  body_only=len(near)-1<=i<len(near)+len(body)-1
  for j in range(segments):
   if body_only and j>=144:continue
   a=i*segments+j;an=i*segments+(j+1)%segments;b=a+segments;bn=an+segments;F.append((a,an,bn,b))
 used=sorted({v for f in F for v in f});mapping={v:i for i,v in enumerate(used)};V=[V[v]for v in used];F=[tuple(mapping[v]for v in f)for f in F]
 edge_counts=Counter(tuple(sorted((a,b)))for f in F for a,b in zip(f,f[1:]+f[:1]));boundary=sum(n==1 for n in edge_counts.values())
 ob=common.mesh_object(OBJECT,V,F);col=bpy.data.collections.new(COL);bpy.context.scene.collection.children.link(col)
 for c in list(ob.users_collection):c.objects.unlink(ob)
 col.objects.link(ob);ob['physical_id']='MOTO-PASSENGER-FOOTREST-RUBBER-001';ob['code']='JK113008';ob['diagnostic_open_boundary']='Body lower90deg omitted diagnostically; observed near collar kept circumferentially complete; no physical slot/seat claim'
 P={'schema':1,'package':'P16','component_id':'MOTO-PASSENGER-FOOTREST-RUBBER-001','part_code':'JK113008','revision':K,'collection':COL,'frame':'Unplaced local X longitudinal, entry datumX0 and distalX+.100; Y lateral, Z review-up. Body lower90deg omitted diagnostically, collars complete; no installed clocking.','length_m':.100,'length_range_m':[.080,.120],'body_diameter_m':.030,'body_diameter_range_m':[.024,.038],'rib_crest_diameter_m':.0332,'rib_height_m':.0016,'rib_height_range_m':[.0008,.0026],'flared_rim_diameter_m':.042,'rim_diameter_range_m':[.034,.052],'rib_centres_m':centers,'rib_count':14,'rib_count_range':[13,15],'rib_count_status':'Working photo inference only; not a mould/count measurement','angular_extent_degrees':[-45,315],'body_visible_angular_extent_degrees':[-45,225],'collars_complete_circumference':True,'unobserved_lower_sector_degrees':[225,315],'diagnostic_omission_axial_range_m':[.010,.090],'angular_extent_status':'Diagnostic review omission, not an actual open-side/slot claim or measured azimuth','visible_near_mouth_return_depth_m':.003,'mouth_return_status':'Short visible near-mouth lip only, cross section/depth estimated; no full inner bore, seat, thickness wall or retention lands manufactured','distal_face':'Unobserved distal closure/seat omitted; open exterior edge, not claimed through-bore','source_profile_x_radius_m':profile,'angular_segments':segments,'expected_boundary_edges':boundary,'all_dimensions_estimated':True,'dimension_basis':'Uncalibrated image aspect and explicit author working bounds; no scale, OEM mm values or metal-fit derivation','source':'creative/research/'+K+'/dedup-and-G1.json','material':{'name':'Proposed clean black passenger step rubber, chemistry unmeasured','base_color_linear':[.012,.013,.015,1],'metallic':0,'roughness':.64},'scope':'Single distinct passenger visible-envelope exemplar, cylindrical ribbed body and flared ends. No DF161413 geometry reused, no counterpart repeated, no hidden seat/retainer or real underside slot invented.','package_complete':False,'art_accepted':False}
 write(H/'parameters.json',P);common.finish_source(H,O,P)
 # Preserve versioned helper geometry checks; set deliberately useful whole-exemplar camera margin before gray review.
 bpy.context.scene.camera.data.ortho_scale=.155;bpy.ops.wm.save_as_mainfile(filepath=str(H/'child-gray.blend'),compress=True)
 d=json.loads((O/'geometry-check.json').read_text());d.update(source_sha256=sha(H/'child-gray.blend'),open_boundaries_deliberate=True,unknown_lower_band_not_classified=True,source_builder_sha256=sha(Path(__file__)));write(O/'geometry-check.json',d)

def stage(mode):
 if mode=='material':
  assert json.loads((O/'gray-review.json').read_text())['read_for_exterior_study'];common.stage(K,K,'material');return
 if mode=='preview':assert json.loads((O/'gray-review.json').read_text())['read_for_exterior_study']
 if mode=='final':assert json.loads((O/'preview-review.json').read_text())['read_for_exterior_study']
 source=H/('child-gray.blend'if mode=='gray'else'child-candidate.blend');bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.render.resolution_x=1000;s.render.resolution_y=750;s.camera.data.ortho_scale=.155
 center=Vector((.05,0,0));views=[('side',(.005,-.19,.115)),('mouth',(-.12,-.14,.10)),('underside',(.02,-.04,-.19))]
 if mode=='preview':views=views[:2]
 if mode=='final':views=[views[0],views[1],('neutral',(.16,-.13,.095)),views[2]]
 rows=[];before=common.digest(bpy.data.objects[OBJECT].data);(O/'raw').mkdir(exist_ok=True)
 for label,eye in views:
  s.camera.location=Vector(eye);common.look(s.camera,center);s.cycles.samples=96 if mode=='final'else 16
  if label=='neutral':
   for light in bpy.data.lights:light.energy=0
   world=bpy.data.worlds.new('Independent neutral uniform white environment');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1);world.node_tree.nodes['Background'].inputs[1].default_value=.65;s.world=world;s.view_settings.look='None'
  stem=mode+'-'+label;s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath=str(O/'raw'/(stem+'.exr'));bpy.ops.render.render(write_still=True);s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(O/(stem+'.png')),scene=s)
  rows.append(dict(name=stem,view=stem,png=stem+'.png',exr='raw/'+stem+'.exr',PNG_sha256=sha(O/(stem+'.png')),EXR_sha256=sha(O/'raw'/(stem+'.exr')),samples=s.cycles.samples,actually_saved=True,resolution_px=[1000,750],camera=list(eye),look=s.view_settings.look))
 assert common.digest(bpy.data.objects[OBJECT].data)==before
 write(O/(mode+'-render-report.json'),dict(source_sha256=sha(source),views=rows,protocol_sha256=sha(Path(__file__)),helper_path='tools/powertrain_completion_common_open_v1.py',helper_sha256=sha(R/'tools/powertrain_completion_common_open_v1.py'),geometry_unchanged=True,art_accepted=False,fit_qualified=False))
if __name__=='__main__':
 mode=sys.argv[-1]
 if mode=='build':build()
 elif mode in ['gray','material','preview','final']:stage(mode)
 else:raise ValueError(mode)
