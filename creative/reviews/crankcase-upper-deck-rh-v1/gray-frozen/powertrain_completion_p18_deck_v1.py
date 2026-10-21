"""P18 first bounded exterior fragment: photographed right upper crankcase land, not invented whole case."""
import bpy,sys,json,math,bmesh
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from powertrain_completion_common import mesh_object,finish_source
R=Path(__file__).resolve().parents[1];H=R/'assets-src/moto-components/crankcase-upper-deck-rh-v1';O=R/'creative/reviews/crankcase-upper-deck-rh-v1';H.mkdir(parents=True,exist_ok=True)
# Top-plane landmarks from physical JH541007-7800715338. This is a projection trace with bounded scale.
outline=[[239,367],[396,395],[455,430],[455,696],[267,736],[236,693],[242,635]]
# Saddle open edge; only observed machined top land modeled, underside cut is a review boundary.
for i in range(1,65):
 theta=math.pi/2-math.pi*i/64;outline.append([242+74*math.cos(theta),551+84*math.sin(theta)])
outline += [[236,451]]
holes=[[305,465],[308,638],[424,467],[429,577]];scale=.00042;T=.006
P={'schema':1,'package':'P18','component_id':'MOTO-CRANKCASE-UPPER-DECK-RH-001','source':'creative/research/powertrain-completion-p18-v1/physical-source-supplement-v2.json','outline_pixels':outline,'hole_centres_pixels':holes,'pixel_axis_mapping':'X=(v-550)*scale,Y=(u-346)*scale,Z outward top; not installed axes','selected_projection_scale_m_px':scale,'scale_range_m_px':[.00034,.00052],'deck_thickness_m':T,'deck_thickness_range_m':[.004,.008],'hole_radius_m':.0038,'hole_radius_range_m':[.003,.005],'counterbore_radius_m':.0055,'counterbore_depth_m':.0015,'counterbore_status':'Two visible stepped left bores only, bounded radii; no threads','gallery_pixels':[353,430,391,685],'gallery_corner_radius_pixels':7,'camera_calibrated':False,'all_dimensions_estimated':True,'scope':'Photographed upper right external land fragment with open saddle/gallery and four bores. Finite plate thickness is estimated cut boundary, not full central crankcase depth, internals or cylinder fit. Existing covers/cylinder/head retained separately.','material':{'name':'Proposed clean machined/cast silver land','base_color_linear':[.38,.40,.42,1],'metallic':.65,'roughness':.40},'package_complete':False,'art_accepted':False}
(H/'parameters.json').write_text(json.dumps(P,indent=2)+'\n');bpy.ops.wm.read_factory_settings(use_empty=True)
def xy(uv):u,v=uv;return ((v-550)*scale,(u-346)*scale)
pts=[xy(p)for p in outline];area=sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(pts,pts[1:]+pts[:1]));
if area<0:pts.reverse()
def plate(name,pts,zlo,zhi):
 n=len(pts);V=[(x,y,z)for z in [zlo,zhi]for x,y in pts];F=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]
 for i in range(n):j=(i+1)%n;F.append((i,j,n+j,n+i))
 return mesh_object(name,V,F)
ob=plate('RH_CRANKCASE_UPPER_EXTERIOR_LAND_FRAGMENT',pts,-T,0)
def difference(cut,name):
 bpy.context.view_layer.objects.active=ob;m=ob.modifiers.new(name,'BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True)
for i,p in enumerate(holes):
 x,y=xy(p);bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=.0038,depth=.04,location=(x,y,-.003),rotation=(0,0,.013+i*.003));difference(bpy.context.object,'Observed through bore '+str(i))
 if i<2:
  bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=.0055,depth=.006,location=(x,y,.0015),rotation=(0,0,.017+i*.003));difference(bpy.context.object,'Bounded visible counterbore '+str(i))
# Rounded rectangular through gallery, independent of the large saddle void.
poly=[]
for u,v,start in [(384,437,270),(384,678,0),(360,678,90),(360,437,180)]:
 for i in range(17):a=math.radians(start+i*90/16);poly.append(xy([u+7*math.cos(a),v+7*math.sin(a)]))
a=sum(p[0]*q[1]-q[0]*p[1]for p,q in zip(poly,poly[1:]+poly[:1]));
if a<0:poly.reverse()
cut=plate('Gallery cut construction',poly,-.02,.02);difference(cut,'Observed long gallery opening')
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
for f in bm.faces:f.smooth=abs(f.normal.z)<.95
for e in bm.edges:e.smooth=not(e.is_manifold and e.calc_face_angle(0)>math.radians(40))
bm.to_mesh(ob.data);bm.free();ob.data.update()
if hasattr(ob.data,'set_sharp_from_angle'):ob.data.set_sharp_from_angle(angle=math.radians(40))
ob['scope']=P['scope'];finish_source(H,O,P)
