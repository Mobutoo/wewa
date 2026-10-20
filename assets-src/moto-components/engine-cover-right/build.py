"""Single original RH casting candidate; no filter cap, bolts, kick or invented interior ribs.
Annotated uncalibrated face samples constrain silhouette. Depths/walls are bounded estimates.
"""
from pathlib import Path
import json,math,sys,hashlib,subprocess,shutil,tempfile
import bpy,bmesh
from mathutils import Vector,Matrix
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'creative/reviews/engine-cover-right-v1'
sys.path.insert(0,str(HERE.parent/'throttle-control'));from control_geometry import material,mesh_object,cylinder,csg,check_mesh,studio,export
sys.path.insert(0,str(HERE.parent/'clutch-control'));from topology_cleanup_v2 import clean_evaluated
P=json.loads((HERE/'parameters.json').read_text());bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
source=bpy.data.collections.new('WEWA_ENGINE_COVER_RIGHT');s.collection.children.link(source)
construction=bpy.data.collections.new('ENGINE_COVER_RIGHT_RETAINED_CONSTRUCTION');s.collection.children.link(construction)
stage=bpy.data.collections.new('ENGINE_COVER_RIGHT_STUDIO_NOT_EXPORTED');s.collection.children.link(stage)
paint=material('Engine silver coated casting - estimated PBR',(.43,.45,.47),.20,.40)
# Closed periodic Catmull-Rom perimeter, not a disc; hidden stretches explicitly estimated.
uv=[Vector(((a-490)*P['pixel_scale_working_m'],(370-b)*P['pixel_scale_working_m'])) for a,b in P['outline_uv_px']]
N=544;RINGS=176
outline=[]
for j in range(N):
 t=j/N*len(uv);i=int(t);f=t-i;a,b,c,d=[uv[(i+k)%len(uv)] for k in [-1,0,1,2]]
 outline.append((2*b+(-a+c)*f+(2*a-5*b+4*c-d)*f*f+(-a+3*b-3*c+d)*f*f*f)*.5)
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
main=Vector(((447-490)*P['pixel_scale_working_m'],(370-365)*P['pixel_scale_working_m']))
fil=Vector(((576-490)*P['pixel_scale_working_m'],(370-360)*P['pixel_scale_working_m']))
def height(pos,t):
 # Broad low crown and softly filleted boss transitions, all depths estimated.
 edge=smooth((1-t)/.15);crown=.005+.015*edge
 dm=(pos-main).length;df=(pos-fil).length
 main_raise=.027*smooth((.063-dm)/.014)
 # Cap/gasket seating annulus is a planar candidate, not a boss intrusion.
 main_raise*=1-smooth((.047-df)/.006)
 seat_raise=.016*smooth((.049-df)/.009)
 # C1 soft maximum joins the two cast bosses without a sharp heightfield seam.
 blend=.005;h=max(blend-abs(main_raise-seat_raise),0)/blend
 crown+=max(main_raise,seat_raise)+h*h*blend*.25
 return crown
verts=[];faces=[]
def layer(inner):
 start=len(verts);verts.append((0,0,height(Vector((0,0)),0)-(.003 if inner else 0)))
 for k in range(1,RINGS+1):
  t=k/RINGS
  for q in outline:
   scale=max(0,1-.0035/q.length) if inner else 1
   p=q*t*scale;tt=t*scale;h=height(p,tt)-(.003 if inner else 0)
   verts.append((p.x,p.y,h))
 for j in range(N):
  tri=(start,start+1+j,start+1+(j+1)%N);faces.append(tri[::-1] if inner else tri)
 for k in range(1,RINGS):
  a=start+1+(k-1)*N;b=a+N
  for j in range(N):
   quad=(a+j,b+j,b+(j+1)%N,a+(j+1)%N);faces.append(quad[::-1] if inner else quad)
 return [start+1+(RINGS-1)*N+j for j in range(N)]
outer=layer(False);inner=layer(True)
# Full-width annular back rim, cavity remains genuinely open from the rear.
ob=[];ib=[]
for j,q in enumerate(outline):
 ob.append(len(verts));verts.append((q.x,q.y,0))
 p=q*(1-.0035/q.length);ib.append(len(verts));verts.append((p.x,p.y,0))
for j in range(N):
 k=(j+1)%N
 faces.extend([(outer[j],ob[j],ob[k],outer[k]),(ob[j],ib[j],ib[k],ob[k]),(ib[j],inner[j],inner[k],ib[k])])
base=mesh_object('Original continuous hollow asymmetric casting loft',verts,faces,construction,paint)
# Visible provisional stations only; no full mounting count inferred.
features=[];drills=[]
for k,(px,py) in enumerate(P['visible_fixation_candidate_uv_px']):
 u=(px-490)*P['pixel_scale_working_m'];v=(370-py)*P['pixel_scale_working_m']
 pos=Vector((u,v));near=min(outline,key=lambda a:abs(math.atan2(math.sin(math.atan2(a.y,a.x)-math.atan2(v,u)),math.cos(math.atan2(a.y,a.x)-math.atan2(v,u)))))
 depth=height(pos,pos.length/near.length)+.001
 features.append(cylinder('Visible fixation collar candidate '+str(k+1),(u,v,depth/2),.0064,depth,construction,paint,axis=(0,0,1),n=80))
 drills.append(cylinder('Visible fixation bore candidate '+str(k+1),(u,v,.016),P['fastener_bore_working_m'],.10,construction,axis=(0,0,1),n=80))
drills.append(cylinder('Filter seat actual open bore - diameter estimated',(fil.x,fil.y,.025),P['filter_bore_radius_working_m'],.14,construction,axis=(0,0,1),n=192))
def row(obj):
 deps=bpy.context.evaluated_depsgraph_get();ev=obj.evaluated_get(deps);m=ev.to_mesh();m.calc_loop_triangles();r={'name':obj.name,'vertices':[list(obj.matrix_world@v.co) for v in m.vertices],'triangles':[list(t.vertices) for t in m.loop_triangles]};ev.to_mesh_clear();return r
with tempfile.TemporaryDirectory(prefix='wewa-cover-') as tmp:
 inp=Path(tmp)/'in.json';out=Path(tmp)/'out.json';inp.write_text(json.dumps({'base':row(base),'features':[row(o) for o in features],'drills':[row(o) for o in drills]}));subprocess.run([shutil.which('python'),str(HERE/'cover_csg.py'),str(inp),str(out)],check=True);operations=json.loads(out.read_text())
body=mesh_object('RH clutch cover hollow casting - editable candidate',operations['vertices'],operations['triangles'],source,paint)
# Radius is a finishing fillet, not geometry hidden by a material.
# A global Bevel on dense CSG triangles was rejected:55 non-manifold edges.
# Broad casting rolls are in the loft itself; unmeasured bore radii remain unclaimed.
normal=body.modifiers.new('Cast face weighted normals','WEIGHTED_NORMAL');normal.keep_sharp=True;normal.weight=50
bpy.context.view_layer.update();cleanup=clean_evaluated(body,construction)
# Dense curved loft uses ordinary interpolated normals; area-weighted normals
# exaggerated radial triangulation at the boss-to-seat transition in the preview.
body.modifiers.clear()
datum=bpy.data.objects.new('Engine RH cover provisional datum',None);source.objects.link(datum)
x,y,z=P['datum_world_m'];datum.matrix_world=Matrix(((0,0,-1,x),(-1,0,0,y),(0,1,0,z),(0,0,0,1)))
body.parent=datum;body['all_dimensions_estimated']=True;body['exact_RDC_fitment_certified']=False;body['art_accepted']=False
construction.hide_render=True;construction.hide_viewport=True;bpy.context.view_layer.update();checks=check_mesh(body)
# Actual rear cavity and filter openness are checked via BVH ray tests in local space.
from mathutils.bvhtree import BVHTree
mesh=body.to_mesh();tree=BVHTree.FromPolygons([v.co for v in mesh.vertices],[tuple(f.vertices) for f in mesh.polygons]);body.to_mesh_clear()
ray=tree.ray_cast(Vector((fil.x,fil.y,-.04)),Vector((0,0,1)),.14);assert ray[0] is None,('Filter bore blocked',ray)
roof=tree.ray_cast(Vector((-.03,0,-.04)),Vector((0,0,1)),.14);assert roof[0] is not None and roof[0].z>.015,('Rear hollow cavity absent',roof)
export(HERE/'engine-cover-right-inspection.glb',[datum,body]);points=[body.matrix_world@Vector(v) for v in body.bound_box];target=sum(points,Vector())/len(points)
studio(s,stage,target)
for o in stage.objects:
 if o.type=='MESH':o.location.z=min(v.z for v in points)-.003
 if o.type=='LIGHT':o.data.energy*=.08
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'engine-cover-right-v1.blend'),compress=True)
report={'id':P['id'],'source_sha256':hashlib.sha256((HERE/'engine-cover-right-v1.blend').read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((HERE/'engine-cover-right-inspection.glb').read_bytes()).hexdigest(),'collection':source.name,'geometry':[checks],'topology_cleanup':cleanup,'filter_bore_ray_clear':True,'rear_cavity_roof_local_w_m':roof[0].z,'datum_world_m_estimated':P['datum_world_m'],'basis_local_u_v_w_world':[[0,-1,0],[0,0,1],[-1,0,0]],'bounds_world_m':{'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)]},'gasket_interface_and_internal_geometry_recovered':False,'estimated_visible_fixation_count':len(P['visible_fixation_candidate_uv_px']),'complete_fixation_count_known':False,'material_measured':False,'all_dimensions_estimated':True,'art_accepted':False,'physical_iphone_tested':False}
(OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');(HERE/'build-report.json').write_text(json.dumps({'preflight':report,'CSG':{k:v for k,v in operations.items() if k not in ['vertices','triangles']}},indent=2)+'\n');print('WEWA_RH_COVER_PREFLIGHT',json.dumps(report))
