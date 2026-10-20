"""Photo-informed cable lever/perch builder. Dimensional estimates stay explicit.
Called separately for clutch and front cable brake; not a mirrored hydraulic kit.
"""
import sys,json,math,hashlib
from pathlib import Path
from collections import Counter
import bpy,bmesh,numpy as np
from mathutils import Vector,Matrix
from mathutils.geometry import delaunay_2d_cdt
from mathutils.bvhtree import BVHTree

def build(HERE):
 ROOT=HERE.parents[2];sys.path.insert(0,str(HERE.parent/'throttle-control'))
 from control_geometry import material,mesh_object,lathe,cylinder,box,csg,check_mesh,tree_world,studio,export
 P=json.loads((HERE/'parameters-v2.json').read_text());folder=HERE.name;prefix='Clutch' if folder=='clutch-control' else 'Front cable brake';OUT=ROOT/'creative/reviews'/(folder+'-v2');OUT.mkdir(parents=True,exist_ok=True)
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
 source=bpy.data.collections.new('WEWA_'+folder.upper().replace('-','_'));scene.collection.children.link(source)
 construction=bpy.data.collections.new(prefix+' editable construction');scene.collection.children.link(construction)
 guides=bpy.data.collections.new(prefix+' immutable interface guides');scene.collection.children.link(guides)
 stage=bpy.data.collections.new(prefix+' studio not exported');scene.collection.children.link(stage)
 black=material(prefix+' black coated casting - estimated',(.012,.014,.018),.10,.24);steel=material(prefix+' machined steel - estimated',(.35,.38,.42),.88,.26)
 # Construct the face from an uncalibrated related-part outline, with a dense
 # constrained interior before varying the thickness. No non-planar n-gon caps.
 land=P['outline_uf_m'];outline=[]
 for i in range(len(land)):
  a,b,c,d=[np.array(land[j%len(land)]) for j in [i-1,i,i+1,i+2]]
  for k in range(8):
   t=k/8;outline.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
 area=sum(outline[i][0]*outline[(i+1)%len(outline)][1]-outline[(i+1)%len(outline)][0]*outline[i][1] for i in range(len(outline)))
 constraints=list(range(len(outline)))
 if area<0:constraints.reverse()
 coords=[Vector((float(u),float(f))) for u,f in outline]
 for u in np.arange(-.018,.153,.0012):
  for f in np.arange(-.010,.036,.0012):coords.append(Vector((float(u),float(f))))
 verts2,_,cap,*_=delaunay_2d_cdt(coords,[],[constraints],1,1e-8,False)
 def inside(u,f):
  odd=False
  for i in range(len(outline)):
   a,b=outline[i],outline[(i+1)%len(outline)]
   if (a[1]>f)!=(b[1]>f) and u<(b[0]-a[0])*(f-a[1])/(b[1]-a[1])+a[0]:odd=not odd
  return odd
 cap=[face for face in cap if inside(sum(verts2[i].x for i in face)/len(face),sum(verts2[i].y for i in face)/len(face))]
 cap_area=sum(abs(sum(verts2[face[j]].x*verts2[face[(j+1)%len(face)]].y-verts2[face[(j+1)%len(face)]].x*verts2[face[j]].y for j in range(len(face))))/2 for face in cap);assert abs(cap_area-abs(area)/2)<1e-8
 ids=sorted({i for face in cap for i in face});mapping={old:i for i,old in enumerate(ids)};verts2=[verts2[i] for i in ids];cap=[tuple(mapping[i] for i in f) for f in cap];count=len(verts2)
 def half_thickness(u):
  t=max(0,min(1,u/.065));return .0033*(1-t)+.0022*t
 verts=[(u,f,sign*half_thickness(u)) for sign in [-1,1] for u,f in verts2];faces=[tuple(reversed(f)) for f in cap]+[tuple(i+count for i in f) for f in cap]
 edges=Counter(tuple(sorted((f[j],f[(j+1)%len(f)]))) for f in cap for j in range(len(f)))
 for (a,b),n in edges.items():
  if n==1:faces.append((a,b,b+count,a+count))
 base=mesh_object(prefix+' dense outlined blade construction',verts,faces,construction,black)
 ball=P['ball_centre_radius_working_m'];bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=ball[2],location=(ball[0],ball[1],0));tip=bpy.context.object;tip.name=prefix+' integrated safety ball'
 for collection in list(tip.users_collection):collection.objects.unlink(tip)
 construction.objects.link(tip)
 pivot_hole=cylinder(prefix+' pivot bore construction',(0,0,0),P['pivot_bore_radius_working_m'],.030,construction,axis=(0,0,1),n=96)
 capture=cylinder(prefix+' estimated cable barrel seat',(.012,.023,0),.0028,.030,construction,axis=(0,0,1),n=80)
 cable_slot=box(prefix+' cable entry slot',(-.007,.023,0),(.040,.0016,.030),construction,bevel=0)
 lever,lever_csg=csg(base,[tip],[pivot_hole,capture,cable_slot],source,black,ROOT,prefix+' lever - moving candidate')
 bevel=lever.modifiers.new('Formed blade edge radii - working estimate','BEVEL');bevel.width=.00065;bevel.segments=4;bevel.limit_method='ANGLE';bevel.angle_limit=.35;bevel.harden_normals=True
 # Curved cast branches connect the clamp to two separated pivot ears.
 def sweep(name,points,radii):
  samples=[];rr=[]
  for a,b,ra,rb in zip(points,points[1:],radii,radii[1:]):
   steps=max(2,math.ceil((Vector(b)-Vector(a)).length/.0015))
   for k in range(steps):t=k/steps;samples.append(Vector(a).lerp(Vector(b),t));rr.append(ra*(1-t)+rb*t)
  samples.append(Vector(points[-1]));rr.append(radii[-1]);v=[];f=[];n=32
  for i,p in enumerate(samples):
   tangent=(samples[min(i+1,len(samples)-1)]-samples[max(0,i-1)]).normalized();a=tangent.cross(Vector((0,0,1)))
   if a.length<.01:a=tangent.cross(Vector((0,1,0)))
   a.normalize();b=tangent.cross(a).normalized()
   for j in range(n):angle=math.tau*j/n;v.append(tuple(p+rr[i]*(a*math.cos(angle)+b*math.sin(angle))))
  f=[tuple(reversed(range(n))),tuple(range((len(samples)-1)*n,len(samples)*n))]
  for i in range(len(samples)-1):
   for j in range(n):f.append((i*n+j,(i+1)*n+j,(i+1)*n+(j+1)%n,i*n+(j+1)%n))
  return mesh_object(name,v,f,construction,black)
 ring=lathe(prefix+' clamp ring construction',[(-.034,.01125),(-.034,.0175),(-.022,.0175),(-.022,.01125)],construction,black,n=128);ring.location=(0,-.045,-.004)
 features=[sweep(prefix+' curved perch main web',[(-.028,-.030,-.004),(-.025,-.020,-.001),(-.022,-.012,0)],[.004,.0037,.0035])]
 for sign in [-1,1]:
  features.append(sweep(prefix+(' lower' if sign<0 else ' upper')+' curved fork branch',[(-.022,-.012,0),(-.016,-.008,sign*.0065),(-.008,-.004,sign*.0065),(0,0,sign*.0065)],[.0034,.0020,.0019,.0030]))
  features.append(cylinder(prefix+' pivot ear '+str(sign),(0,0,sign*.0065),.0087,.003,construction,black,axis=(0,0,1),n=96))
  features.append(cylinder(prefix+' clamp bolt lug '+str(sign),(-.028,-.062,sign*.004),.0045,.004,construction,black,axis=(0,0,1),n=64))
 socket=lathe(prefix+' cable adjuster socket',[(-.025,.00425),(-.025,.0075),(-.017,.0075),(-.017,.00425)],construction,black,n=96);socket.location=(0,.021,0);features.append(socket)
 features.append(sweep(prefix+' cable socket upper bridge',[(-.008,-.003,.008),(-.017,.010,.010),(-.021,.021,.009)],[.0022,.0023,.0023]))
 mirror=lathe(prefix+' estimated mirror mounting boss',[(-.006,.0044),(-.006,.0075),(.006,.0075),(.006,.0044)],construction,black,n=96);mirror.rotation_euler.y=-math.pi/2;mirror.location=(-.028,-.020,.009);features.append(mirror)
 features.append(cylinder(prefix+' boss connecting pad',(-.028,-.020,.001),.005,.008,construction,black,axis=(0,0,1),n=64))
 drills=[box(prefix+' clamp pinch split',(-.028,-.064,-.004),(.020,.026,.0014),construction,bevel=0),cylinder(prefix+' perch pivot drilling',(0,0,0),.00315,.040,construction,axis=(0,0,1),n=96),cylinder(prefix+' clamp bolt drilling',(-.028,-.062,0),.00215,.030,construction,axis=(0,0,1),n=64),cylinder(prefix+' mirror bore drilling',(-.028,-.020,.006),.0044,.030,construction,axis=(0,0,1),n=96)]
 perch,perch_csg=csg(ring,features,drills,source,black,ROOT,prefix+' cast perch - fixed candidate')
 bevel=perch.modifiers.new('Cast perch edge radii - estimated','BEVEL');bevel.width=.00045;bevel.segments=3;bevel.limit_method='ANGLE';bevel.angle_limit=.35;bevel.harden_normals=True
 # Hollow screw barrel with a geometric helical appearance; no pitch is
 # attributed to Bajaj. It remains an unqualified visual working thread.
 section=[(-.042,.0016),(-.042,.0037)]
 for i in range(111):section.append((-.0415+i*.0002,.0040))
 section +=[(-.019,.0037),(-.019,.0016)]
 adjuster=lathe(prefix+' hollow cable barrel adjuster',section,source,steel,n=96);adjuster.location=(0,.021,0)
 for v in adjuster.data.vertices:
  x,y,z=v.co;r=math.hypot(y,z)
  if -.0414<x<-.020 and r>.0038:
   angle=math.atan2(z,y);phase=(x/.001-angle/math.tau)%1;profile=abs(phase-.5)*2;radius=.0040-.00022*(1-profile);v.co.y*=radius/r;v.co.z*=radius/r
 nut=lathe(prefix+' adjuster locknut',[(-.035,.0042),(-.035,.0065),(-.0315,.0065),(-.0315,.0042)],source,steel,n=96);nut.location=(0,.021,0)
 for v in nut.data.vertices:
  radius=math.hypot(v.co.y,v.co.z)
  if radius>.006:
   angle=math.atan2(v.co.z,v.co.y);radius_hex=.0065*math.cos(math.pi/6)/math.cos((angle%(math.tau/6))-math.pi/6);v.co.y*=radius_hex/radius;v.co.z*=radius_hex/radius
 # Pin and its head are a single fused original solid; lower nut is separate.
 shaft=cylinder(prefix+' pivot pin shaft construction',(0,0,0),.003,.020,construction,steel,axis=(0,0,1),n=64);head=cylinder(prefix+' pivot pin head construction',(0,0,.010),.005,.004,construction,steel,axis=(0,0,1),n=64)
 pin,_=csg(shaft,[head],[],source,steel,ROOT,prefix+' pivot pin - fixed candidate')
 lower_nut=lathe(prefix+' lower pivot nut',[(-.002,.0032),(-.002,.0053),(.002,.0053),(.002,.0032)],source,steel,n=96);lower_nut.rotation_euler.y=-math.pi/2;lower_nut.location=(0,0,-.011)
 # All visible meshes transform to world-aligned offsets. Recalculate normals
 # after the handedness reflection, avoiding a negative-scale glTF node.
 inward=Vector(P['axis_inward_vector']).normalized();outward=-inward;up=Vector((0,0,1));forward=Vector((0,-1,0));forward=(forward-inward*forward.dot(inward)).normalized();M=Matrix(((outward.x,forward.x,0),(outward.y,forward.y,0),(0,0,1)))
 pivot=Vector(P['endpoint_m'])+inward*P['pivot_q_working_m']+forward*P['pivot_forward_offset_working_m']+up*P['pivot_height_offset_working_m']
 objects=[lever,perch,adjuster,nut,pin,lower_nut]
 bpy.context.view_layer.update()
 for o in objects:
  local=o.matrix_world.copy()
  for v in o.data.vertices:v.co=M@(local@v.co)
  o.rotation_euler=(0,0,0);o.location=pivot;o.scale=(1,1,1);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
  for e in bm.edges:e.smooth=e.is_manifold and e.calc_face_angle(0)<.70
  bm.to_mesh(o.data);bm.free()
  normal=o.modifiers.new('Preserve planar casting and machined annulus normals','WEIGHTED_NORMAL');normal.keep_sharp=True;normal.weight=50;normal.mode='FACE_AREA_WITH_ANGLE'
 for o in construction.objects:o.hide_render=True;o.hide_set(True)
 from topology_cleanup_v2 import clean_evaluated
 cleanup=[clean_evaluated(o,construction) for o in [lever,perch]]
 bpy.context.view_layer.update();checks=[check_mesh(o) for o in objects]
 def link(path,name):
  with bpy.data.libraries.load(str(path),link=True) as (available,loaded):assert name in available.objects;loaded.objects=[name]
  o=loaded.objects[0];guides.objects.link(o);o.hide_render=True;return o
 side='Left' if folder=='clutch-control' else 'Right'
 grip=link(HERE.parent/'handlebar-grips/handlebar-grips-v2.blend',side+' rubber grip - editable candidate');bar=link(HERE.parent/'handlebar/handlebar-v1.blend','Handlebar bare continuous tube - editable candidate');bpy.context.view_layer.update()
 static_trees={o.name:tree_world(o) for o in objects if o!=lever};static_trees['grip']=tree_world(grip);static_trees['bar']=tree_world(bar)
 poses=[];sign=1 if folder=='clutch-control' else -1
 for angle in P['working_pull_angles_degrees']:
  lever.rotation_euler.z=sign*math.radians(angle);bpy.context.view_layer.update();tree=tree_world(lever);crossings={name:len(tree.overlap(other)) for name,other in static_trees.items()};distances=[]
  for i in range(0,len(lever.data.vertices),max(1,len(lever.data.vertices)//600)):
   hit=static_trees['grip'].find_nearest(lever.matrix_world@lever.data.vertices[i].co)
   if hit[0] is not None:distances.append(hit[3])
  row={'working_pull_degrees':angle,'surface_crossings':crossings,'sparse_vertex_to_grip_surface_min_m':min(distances),'full_hausdorff_or_tolerance_test':False};poses.append(row);assert not any(crossings.values()),row
 # Positive screen-side pull is encoded in the physical world Z sign.
 for frame,angle in [(1,0),(13,6),(25,12)]:lever.rotation_euler.z=sign*math.radians(angle);lever.keyframe_insert(data_path='rotation_euler',frame=frame)
 lever.animation_data.action.name=prefix+' 0 to 12 degree inspection pull - estimated';scene.frame_start=1;scene.frame_end=25;scene.render.fps=24;scene.frame_set(1);bpy.context.view_layer.update()
 guides.hide_render=True
 for o in guides.objects:o.hide_set(True)
 export(HERE/(folder+'-v2-inspection.glb'),objects,animations=True)
 target=pivot+outward*.065+forward*.008;studio(scene,stage,target)
 lever['physical_pivot_world_m']=list(pivot);lever['scope']='Cable lever, estimated partial pull only; no full cable actuation or exact RDC fitment';lever['art_accepted']=False
 source_path=HERE/(folder+'-v2.blend');bpy.ops.wm.save_as_mainfile(filepath=str(source_path),compress=True)
 report={'component_id':P['component_id'],'revision':P['revision'],'source_sha256':hashlib.sha256(source_path.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((HERE/(folder+'-v2-inspection.glb')).read_bytes()).hexdigest(),'physical_side':P['physical_side'],'geometry':checks,'motion_poses':poses,'pivot_world_m':list(pivot),'pull_world_Z_sign':sign,'support_clamp_q_range_estimated_m':[.170,.182],'mirror_boss_axis_world_m':list(pivot+M@Vector((-.028,-.020,.009))),'mirror_bore_estimated_m':.0088,'cable_adjuster_axis_world':list(outward),'estimated_cable_seat_world_m':list(pivot+M@Vector((.012,.023,0))),'outline_area_before_solid_m2':cap_area,'all_dimensions_and_partial_motion_estimated':True,'mechanical_full_stroke_verified':False,'boot_created':False,'hydraulic_parts_created':False,'physical_iphone_tested':False,'art_accepted':False}
 report['mesh_cleanup']=cleanup
 report['supersedes_rejected_revision']=folder+'-v1: degenerate triangles in evaluated congés'
 report['cable_adjuster_axis_world']=list(inward)
 report['cable_adjuster_axis_definition']='Out of fixed adjuster housing toward sheath, not nipple-seat direction'
 report['estimated_sheath_outlet_world_m']=list(pivot+M@Vector((-.042,.021,0)))
 report['estimated_cable_seat_definition']='Nipple seat in moving lever at rest; not the sheath terminal'
 (OUT/'source-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');(HERE/'build-report-v2.json').write_text(json.dumps({'preflight':report,'lever_CSG':{k:v for k,v in lever_csg.items() if k not in ['vertices','triangles']},'perch_CSG':{k:v for k,v in perch_csg.items() if k not in ['vertices','triangles']}},indent=2)+'\n');print('WEWA_LEVER_CONTROL_PREFLIGHT',json.dumps(report))
