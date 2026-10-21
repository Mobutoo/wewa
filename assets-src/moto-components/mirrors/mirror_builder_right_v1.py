"""Original mirror construction. Conditional references and dimensions stay explicit."""
import bpy,bmesh,json,math,tempfile,subprocess,shutil,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]

def build(side='right',phase='shell'):
 assert side=='right','Right-only revision; immutable LH builder is not modified'
 P=json.loads((HERE/('parameters-'+side+'.json')).read_text());prefix='LH' if side=='left' else 'RH';revision='mirror-'+side+'-v1';OUT=ROOT/'creative/reviews'/revision;OUT.mkdir(parents=True,exist_ok=True)
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
 source=bpy.data.collections.new('WEWA_MIRROR_'+side.upper());scene.collection.children.link(source)
 construction=bpy.data.collections.new(prefix+' mirror editable construction');scene.collection.children.link(construction)
 studio=bpy.data.collections.new(prefix+' mirror studio not exported');scene.collection.children.link(studio)
 C=Vector(P['head_centre_world_working_m']);N=Vector(P['head_normal_toward_rider_working']).normalized();up=Vector((0,0,1));U=Vector((1 if side=='left' else -1,0,0));U=(U-N*U.dot(N)).normalized();V=U.cross(N);V=V if V.z>0 else -V
 def head(p):return C+U*p[0]+V*p[1]+N*p[2]
 def mesh(name,verts,faces,col=construction):
  data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(data);bm.free();o=bpy.data.objects.new(name,data);col.objects.link(o);return o
 def tri(o):
  o.data.calc_loop_triangles();return {'name':o.name,'vertices':[list(o.matrix_world@v.co) for v in o.data.vertices],'triangles':[list(t.vertices) for t in o.data.loop_triangles]}
 def boolean(name,base,features,drills):
  with tempfile.TemporaryDirectory(prefix='wewa-mirror-') as t:
   inp=Path(t)/'in.json';out=Path(t)/'out.json';inp.write_text(json.dumps({'base':tri(base),'features':[tri(o) for o in features],'drills':[tri(o) for o in drills]}));subprocess.run([shutil.which('python'),str(HERE/'csg_worker.py'),str(inp),str(out)],check=True);r=json.loads(out.read_text())
  o=mesh(name,r['vertices'],r['triangles'],source);history.append({k:v for k,v in r.items() if k not in ['vertices','triangles']});return o
 def sweep_profile(name,origin,axis,profile,n=96,col=construction,closed_profile=False):
  origin=Vector(origin);axis=Vector(axis).normalized();a=axis.cross(Vector((0,0,1)))
  if a.length<.1:a=axis.cross(Vector((0,1,0)))
  a.normalize();b=axis.cross(a);verts=[]
  for q,r in profile:
   verts.extend(tuple(origin+axis*q+r*(a*math.cos(j*math.tau/n)+b*math.sin(j*math.tau/n))) for j in range(n))
  faces=[]
  for k in range(len(profile)-1):
   for j in range(n):faces.append((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j))
  if closed_profile:
   for j in range(n):faces.append(((len(profile)-1)*n+j,(len(profile)-1)*n+(j+1)%n,(j+1)%n,j))
  else:faces.extend([tuple(reversed(range(n))),tuple(range((len(profile)-1)*n,len(profile)*n))])
  return mesh(name,verts,faces,col)
 def cylinder(name,origin,axis,radius,depth):return sweep_profile(name,origin,axis,[(-depth/2,radius),(depth/2,radius)])
 def sphere(name,centre,radius):
  bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,radius=radius,location=centre);o=bpy.context.object;o.name=name
  for c in list(o.users_collection):c.objects.unlink(o)
  construction.objects.link(o);bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);return o
 def catmull_closed(points,steps=12):
  points=[Vector(p) for p in points];out=[]
  for i in range(len(points)):
   p0,p1,p2,p3=[points[j%len(points)] for j in [i-1,i,i+1,i+2]]
   # Centripetal knots prevent overshoot/loops at unevenly spaced landmarks.
   knots=[0]
   for a,b in [(p0,p1),(p1,p2),(p2,p3)]:knots.append(knots[-1]+max((b-a).length**.5,1e-9))
   t0,t1,t2,t3=knots
   for t in np.linspace(t1,t2,steps,endpoint=False):
    a1=(t1-t)/(t1-t0)*p0+(t-t0)/(t1-t0)*p1;a2=(t2-t)/(t2-t1)*p1+(t-t1)/(t2-t1)*p2;a3=(t3-t)/(t3-t2)*p2+(t-t2)/(t3-t2)*p3
    b1=(t2-t)/(t2-t0)*a1+(t-t0)/(t2-t0)*a2;b2=(t3-t)/(t3-t1)*a2+(t-t1)/(t3-t1)*a3
    out.append(tuple((t2-t)/(t2-t1)*b1+(t-t1)/(t2-t1)*b2))
  return out
 pixels=P['source_contour']['points_px'];us=[p[0] for p in pixels];vs=[p[1] for p in pixels];midu=(max(us)+min(us))/2;midv=(max(vs)+min(vs))/2
 outline=catmull_closed([((u-midu)/(max(us)-min(us))*P['head_width_working_m']*(1 if side=='left' else -1),(midv-v)/(max(vs)-min(vs))*P['head_height_working_m']) for u,v in pixels]);area=sum(outline[j-1][0]*p[1]-p[0]*outline[j-1][1] for j,p in enumerate(outline))/2
 if area<0:outline.reverse()
 def pchip(xs,ys,x):
  xs=np.array(xs);ys=np.array(ys);h=np.diff(xs);d=np.diff(ys)/h;m=np.zeros(len(xs));m[0]=d[0];m[-1]=d[-1]
  for k in range(1,len(xs)-1):
   if d[k-1]*d[k]>0:
    w1=2*h[k]+h[k-1];w2=h[k]+2*h[k-1];m[k]=(w1+w2)/(w1/d[k-1]+w2/d[k])
  k=min(max(np.searchsorted(xs,x)-1,0),len(xs)-2);t=(x-xs[k])/h[k];return (2*t**3-3*t*t+1)*ys[k]+(t**3-2*t*t+t)*h[k]*m[k]+(-2*t**3+3*t*t)*ys[k+1]+(t**3-t*t)*h[k]*m[k+1]
 outer=[(0,-.029),(.12,-.0288),(.32,-.027),(.55,-.024),(.75,-.019),(.90,-.012),(.97,-.0075),(1,-.0045)]
 inner=[(0,-.0262),(.12,-.026),(.31,-.0242),(.53,-.021),(.73,-.016),(.88,-.0092),(.94,-.0055),(.97,-.004)]
 rings=[(r,pchip(*zip(*outer),r)) for r in np.linspace(.025,1,36)]+[(1,-.001),(.999,0),(.990,.0004),(.97,-.0015)]+[(r,pchip(*zip(*inner),r)) for r in np.linspace(.97,.025,36)]
 vertices=[]
 for r,d in rings:
  # Rear crown shifts inboard, matching the visible compound bulge at neck.
  shiftu=-.016*(1-r*r);shiftv=-.006*(1-r*r)
  vertices.extend((u*r+shiftu,v*r+shiftv,d) for u,v in outline)
 count=len(outline);faces=[]
 for k in range(len(rings)-1):
  for j in range(count):faces.append((k*count+j,k*count+(j+1)%count,(k+1)*count+(j+1)%count,(k+1)*count+j))
 for ring,depth in [(0,-.029),(len(rings)-1,-.0262)]:
  centre=len(vertices);vertices.append((-.016,-.006,depth))
  for j in range(count):faces.append((centre,ring*count+j,ring*count+(j+1)%count))
 history=[];body=mesh(prefix+' mirror compound hollow shell construction',vertices,faces)
 ball=Vector(P['head_ball_working_local_uvd_m']);axis=Vector(P['head_neck_axis_working_local_uvd']).normalized()
 def curved_neck(name,profile):
  # Move the cavity into the hollow head, avoiding an unsupported back-wall exit.
  a=Vector((0,0,1));b=axis.cross(a).normalized();verts=[];n=96
  for q,r,d in profile:
   centre=ball+axis*q+Vector((0,0,d));verts.extend(tuple(centre+r*(a*math.cos(j*math.tau/n)+b*math.sin(j*math.tau/n))) for j in range(n))
  faces=[]
  for k in range(len(profile)-1):
   for j in range(n):faces.append((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j))
  faces.extend([tuple(reversed(range(n))),tuple(range((len(profile)-1)*n,len(profile)*n))]);return mesh(name,verts,faces)
 neck=curved_neck(prefix+' integral socket outside construction',[(.001,.0105,0),(.007,.011,0),(.022,.012,0),(.033,.012,.001),(.044,.010,.004),(.055,.007,.006),(.063,.006,.006)])
 hole=curved_neck(prefix+' curved neck working bore construction',[(-.02,.0047,0),(0,.0047,0),(.007,.0047,0),(.022,.0047,0),(.033,.0047,.001),(.044,.0047,.004),(.055,.0047,.006),(.075,.0047,.006)]);pocket=sphere(prefix+' spherical socket clearance construction',ball,P['ball_radius_working_m']+P['ball_clearance_working_m'])
 # The related RH photo shows a small circular opening near the inboard rear shoulder.
 # Its function, exact coordinates, size and current RDC applicability remain unknown.
 # Cut a real passage through the estimated rear skin, avoiding a decal/depression substitute.
 observed=P['observed_small_hole'];uv=observed['position_local_uv_working_m']
 inspection_hole=cylinder(prefix+' observed rear circular passage cutter - function unknown',(uv[0],uv[1],-.028),(0,0,1),observed['radius_working_m'],.040)
 shell=boolean(prefix+' mirror compound shell and socket - candidate',body,[neck],[hole,pocket,inspection_hole]);body_local=[v.co.copy() for v in shell.data.vertices]
 # Preserve original section/CSG geometry. No global bevel after booleans.
 for vertex in shell.data.vertices:vertex.co=head(vertex.co)
 bm=bmesh.new();bm.from_mesh(shell.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(shell.data);bm.free();shell.data.update()
 material=bpy.data.materials.new(prefix+' original mirror shell clay');material.use_nodes=True;material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.20,.22,.24,1);material.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.45;shell.data.materials.append(material)
 for f in shell.data.polygons:f.use_smooth=True
 shell.data.set_sharp_from_angle(angle=.60)
 # Initial G3 shell study precedes glass, stem, rubber covers and materials.
 objects=[shell];checks=[]
 # G3/G4 next observable pieces: finite curved glass, rear reflective coat, seal.
 if phase in ['head','full']:
  def inward_outline(distance):
   result=[]
   for j,p in enumerate(outline):
    tangent=Vector(outline[(j+1)%len(outline)])-Vector(outline[j-1]);tangent.normalize();result.append(tuple(Vector(p)+Vector((-tangent.y,tangent.x))*distance))
   return result
  def glass_sag(u,v):
   R=P['glass_sphere_radius_working_m'];return R-math.sqrt(max(R*R-u*u-v*v,0))
  def curved_plate(name,edge,front_offset,thickness):
   # Both surfaces share real distributed radial samples; no nonplanar n-gon.
   count=len(edge);verts=[];faces=[];rr=np.linspace(.035,1,30)
   for rear in [False,True]:
    for r in rr:
     for u,v in edge:
      x=u*r;y=v*r;d=.0002-glass_sag(x,y)+front_offset-(thickness if rear else 0);verts.append((x,y,d))
   rings=len(rr)
   for side_index in [0,1]:
    start=side_index*rings*count
    for k in range(rings-1):
     for j in range(count):faces.append((start+k*count+j,start+k*count+(j+1)%count,start+(k+1)*count+(j+1)%count,start+(k+1)*count+j))
    centre=len(verts);verts.append((0,0,.0002+front_offset-(thickness if side_index else 0)))
    for j in range(count):faces.append((centre,start+j,start+(j+1)%count))
   a=(rings-1)*count;b=(2*rings-1)*count
   for j in range(count):faces.append((a+j,a+(j+1)%count,b+(j+1)%count,b+j))
   o=mesh(name,verts,faces,source)
   for vertex in o.data.vertices:vertex.co=head(vertex.co)
   bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(o.data);bm.free();return o
  glass=curved_plate(prefix+' convex mirror glass - finite thickness candidate',inward_outline(P['glass_inset_working_m']),0,P['glass_thickness_working_m'])
  coating=curved_plate(prefix+' rear metallic reflector - original candidate',inward_outline(P['glass_inset_working_m']+.00010),-P['glass_thickness_working_m']-.00002,.00006)
  seal_outer=inward_outline(P['seal_outer_inset_working_m']);seal_inner=inward_outline(P['seal_inner_inset_working_m']);verts=[];faces=[]
  for edge,depth in [(seal_outer,-.00035),(seal_inner,-.00035),(seal_inner,-.00085),(seal_outer,-.00085)]:
   for u,v in edge:verts.append(head((u,v,.0002-glass_sag(u,v)+depth)))
  for k in range(4):
   for j in range(count):faces.append((k*count+j,k*count+(j+1)%count,((k+1)%4)*count+(j+1)%count,((k+1)%4)*count+j))
  seal=mesh(prefix+' continuous mirror edge seal - estimated',verts,faces,source)
  def material(name,color,metallic,roughness):
   m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metallic;p.inputs['Roughness'].default_value=roughness;return m
  clear=material(prefix+' mirror glass dielectric - estimated IOR1.52',(.94,.98,.96),0,.020);p=clear.node_tree.nodes['Principled BSDF'];p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.52
  glass.data.materials.append(clear);coating.data.materials.append(material(prefix+' original rear mirror metallic layer',(.78,.79,.80),1,.025));seal.data.materials.append(material(prefix+' matte rubber edge seal',(.006,.007,.008),0,.56))
  for o in [glass,coating,seal]:
   for face in o.data.polygons:face.use_smooth=True
   o.data.set_sharp_from_angle(angle=.60)
  objects.extend([glass,coating,seal])
  # Original microtexture at a declared physical scale, never photographic pixels.
  npx=256;rng=np.random.default_rng(221003 if side=='left' else 221004);f=np.fft.fftfreq(npx);fx,fy=np.meshgrid(f,f);noise=np.fft.ifft2(np.fft.fft2(rng.normal(size=(npx,npx)))*np.exp(-2*math.pi**2*1.5**2*(fx*fx+fy*fy))).real;noise=(noise-noise.mean())/noise.std();rough=np.clip(.45+.016*noise,.40,.52);texdir=HERE/('textures-'+side);texdir.mkdir(exist_ok=True)
  def generated_image(name,filename,rgb):
   im=bpy.data.images.new(prefix+' '+name,width=npx,height=npx,alpha=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.concatenate((rgb,np.ones((npx,npx,1))),axis=-1).astype(np.float32).ravel());im.filepath_raw=str(texdir/filename);im.file_format='PNG';im.save();im.pack();return im
  rough_image=generated_image('original mirror polymer roughness 10mm','polymer-metallic-roughness.png',np.stack((np.ones_like(rough),rough,np.zeros_like(rough)),axis=-1))
  dy,dx=np.gradient(noise*.000002,.010/npx);normal=np.stack((-dx,-dy,np.ones_like(dx)),axis=-1);normal/=np.linalg.norm(normal,axis=-1)[...,None];normal_image=generated_image('original mirror grain RMS2um 10mm','polymer-normal.png',normal*.5+.5)
  plastic=material(prefix+' original black moulded mirror polymer',(.004,.005,.006),0,.45);nodes=plastic.node_tree.nodes;links=plastic.node_tree.links;p=nodes['Principled BSDF'];texture=nodes.new('ShaderNodeTexImage');texture.image=rough_image;sep=nodes.new('ShaderNodeSeparateColor');links.new(texture.outputs['Color'],sep.inputs['Color']);links.new(sep.outputs['Green'],p.inputs['Roughness']);links.new(sep.outputs['Blue'],p.inputs['Metallic']);t=nodes.new('ShaderNodeTexImage');t.image=normal_image;nm=nodes.new('ShaderNodeNormalMap');links.new(t.outputs['Color'],nm.inputs['Color']);links.new(nm.outputs['Normal'],p.inputs['Normal']);shell.data.materials.clear();shell.data.materials.append(plastic)
  def physical_uv(o):
   o.data.update();uv=o.data.uv_layers.new(name='Physical10mm dominant plane UV')
   for f in o.data.polygons:
    axis=max(range(3),key=lambda j:abs(f.normal[j]));sign=1 if f.normal[axis]>=0 else -1
    for li in f.loop_indices:
     co=o.data.vertices[o.data.loops[li].vertex_index].co;pair=(sign*co.y,co.z) if axis==0 else (-sign*co.x,co.z) if axis==1 else (sign*co.x,co.y);uv.data[li].uv=(pair[0]/.010,pair[1]/.010)
  for o in objects:physical_uv(o)
  # Source true studio reflections, no baked photograph and no retailer marking.
  def card(name,centre,width,height,color):
   verts=[centre+U*x+V*y for x,y in [(-width/2,-height/2),(width/2,-height/2),(width/2,height/2),(-width/2,height/2)]];o=mesh(name,verts,[(0,1,2,3)],studio);o.data.materials.append(material(name+' material',color,0,.7));return o
  card(prefix+' reflection white geometry card',C+N*.62+U*.16+V*.11,.13,.42,(.70,.72,.74));card(prefix+' reflection dark geometry card',C+N*.65-U*.13+V*.04,.10,.45,(.015,.02,.03));card(prefix+' reflection warm geometry card',C+N*.67+U*.31-V*.03,.17,.40,(.35,.21,.09))

 if phase=='full':
  linked=HERE.parent/('clutch-control/clutch-control-v2.blend' if side=='left' else 'front-brake-control/front-brake-control-v2.blend');linked_report=json.loads((linked.parent/'build-report-v2.json').read_text());mount=Vector(linked_report.get('preflight',linked_report)['mirror_boss_axis_world_m']);P['mount_boss_centre_world_m']=list(mount);P['linked_mount_source_sha256']=hashlib.sha256(linked.read_bytes()).hexdigest();ball_world=head(ball);A=(U*axis.x+V*axis.y+N*axis.z).normalized()
  enamel=material(prefix+' original black enamel on steel stem',(.006,.007,.009),0,.19);metal=material(prefix+' estimated steel fasteners',(.35,.38,.41),1,.22);rubber=material(prefix+' original matte neck and base covers',(.006,.007,.008),0,.56);neck_plastic=material(prefix+' original satin articulation cover',(.006,.007,.008),0,.30)
  for m in [neck_plastic,rubber]:
   nodes=m.node_tree.nodes;links=m.node_tree.links;t=nodes.new('ShaderNodeTexImage');t.image=normal_image;nm=nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.5;links.new(t.outputs['Color'],nm.inputs['Color']);links.new(nm.outputs['Normal'],nodes['Principled BSDF'].inputs['Normal'])
  def annular(name,origin,direction,profile,matl):
   o=sweep_profile(name,origin,direction,profile,n=96,col=source,closed_profile=True);o.data.materials.append(matl);return o
  def filleted(points,radii):
   points=[Vector(p) for p in points];path=[points[0]]
   def line_to(p):
    start=path[-1];length=(p-start).length
    for k in range(1,max(1,math.ceil(length/.0015))+1):path.append(start+(p-start)*k/max(1,math.ceil(length/.0015)))
   for k in range(1,len(points)-1):
    p=points[k];a=(points[k-1]-p).normalized();b=(points[k+1]-p).normalized();theta=math.acos(max(-1,min(1,a.dot(b))));distance=min(radii[k-1]/math.tan(theta/2),(points[k-1]-p).length*.35,(points[k+1]-p).length*.35);radius=distance*math.tan(theta/2);start=p+a*distance;end=p+b*distance;centre=p+(a+b).normalized()*radius/math.sin(theta/2);normal=(start-centre).cross(end-centre).normalized();start_direction=(start-centre).normalized();end_direction=(end-centre).normalized();arc=math.acos(max(-1,min(1,start_direction.dot(end_direction))));line_to(start)
    for step in range(1,max(4,math.ceil(arc/math.radians(4)))+1):path.append(centre+Matrix.Rotation(arc*step/max(4,math.ceil(arc/math.radians(4))),3,normal)@(start-centre))
   line_to(points[-1]);return path
  stem_points=[mount+up*.022,mount+up*.053,ball_world-A*.035,ball_world];path=filleted(stem_points,[.012,.008]);verts=[];faces=[];radial=64;previous=None
  for k,c in enumerate(path):
   tangent=(path[min(k+1,len(path)-1)]-path[max(k-1,0)]).normalized();a=tangent.cross(Vector((0,1,0))) if previous is None else previous-tangent*previous.dot(tangent)
   if a.length<.01:a=tangent.cross(Vector((1,0,0)))
   a.normalize();b=tangent.cross(a).normalized();previous=a
   for j in range(radial):verts.append(tuple(c+P['rod_radius_working_m']*(a*math.cos(j*math.tau/radial)+b*math.sin(j*math.tau/radial))))
  for k in range(len(path)-1):
   for j in range(radial):faces.append((k*radial+j,k*radial+(j+1)%radial,(k+1)*radial+(j+1)%radial,(k+1)*radial+j))
  faces.extend([tuple(reversed(range(radial))),tuple(range((len(path)-1)*radial,len(path)*radial))]);rod=mesh(prefix+' continuous bent rod construction',verts,faces)
  # Editable centreline accompanies the actual closed solid, not a substitute for it.
  curve=bpy.data.curves.new(prefix+' original bent stem centreline','CURVE');curve.dimensions='3D';spline=curve.splines.new('POLY');spline.points.add(len(path)-1)
  for p,co in zip(spline.points,path):p.co=(*co,1)
  guide=bpy.data.objects.new(curve.name,curve);construction.objects.link(guide)
  verts=[];faces=[];n=72;z0=-.004;z1=.024;pitch=P['stud_thread_pitch_working_m'];levels=math.ceil((z1-z0)/pitch*12)
  for k in range(levels+1):
   z=z0+(z1-z0)*k/levels
   for j in range(n):
    angle=j*math.tau/n;phase_h=((z-z0)/pitch-angle/math.tau)%1;value=1 if phase_h<.15 or phase_h>=.95 else 1-(phase_h-.15)/.30 if phase_h<.45 else 0 if phase_h<.65 else (phase_h-.65)/.30;r=.00335+.00065*value;verts.append(tuple(mount+Vector((r*math.cos(angle),r*math.sin(angle),z))))
  for k in range(levels):
   for j in range(n):faces.append((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j))
  faces.extend([tuple(reversed(range(n))),tuple(range(levels*n,(levels+1)*n))]);stud=mesh(prefix+' cosmetic helical stud construction - thread unknown',verts,faces);bearing_ball=sphere(prefix+' estimated steel articulation ball construction',ball_world,P['ball_radius_working_m']);stem=boolean(prefix+' continuous steel stem ball and cosmetic stud - candidate',rod,[stud,bearing_ball],[]);stem.data.materials.append(enamel)
  # The same closed steel body has a local exposed-metal region on the estimated stud.
  stem.data.materials.append(metal)
  for f in stem.data.polygons:
   centre=sum((stem.data.vertices[i].co for i in f.vertices),Vector())/len(f.vertices)
   if centre.z<mount.z+.022:f.material_index=1
  washer=annular(prefix+' mirror base washer - estimated',mount,up,[(.0061,.0043),(.0061,.0072),(.0071,.0072),(.0071,.0043)],metal)
  # Closed hex nut: axial chamfers are formed in the section, no post-CSG bevel.
  count_hex=96;hexagon=[Vector((math.cos((k+.5)*math.tau/6),math.sin((k+.5)*math.tau/6))) for k in range(6)];outer=[]
  for j in range(count_hex):
   f=j/count_hex*6;k=int(f);t=f-k;outer.append((hexagon[k]*(1-t)+hexagon[(k+1)%6]*t)*(.014/(2*math.cos(math.pi/6))))
  profiles=[('outer',.0073,.94),('outer',.0077,1),('outer',.0129,1),('outer',.0133,.94),('inner',.0133,.0043),('inner',.0073,.0043)];verts=[];faces=[]
  for kind,z,val in profiles:
   for j in range(count_hex):
    p=outer[j]*val if kind=='outer' else outer[j].normalized()*val;verts.append(tuple(mount+Vector((p.x,p.y,z))))
  for k in range(len(profiles)):
   for j in range(count_hex):faces.append((k*count_hex+j,k*count_hex+(j+1)%count_hex,((k+1)%len(profiles))*count_hex+(j+1)%count_hex,((k+1)%len(profiles))*count_hex+j))
  nut=mesh(prefix+' mirror base hex nut - estimated thread-free bore',verts,faces,source);nut.data.materials.append(metal)
  base_cover=annular(prefix+' hollow mirror mounting cover - estimated',mount,up,[(.020,.0083),(.0202,.0085),(.0265,.0085),(.0267,.0083),(.0267,.0067),(.0269,.0065),(.0388,.0065),(.039,.0063),(.039,.0046),(.020,.0046)],rubber)
  lower_cover=annular(prefix+' fixed hollow lower neck cover - estimated',ball_world,A,[(-.029,.006),(-.0285,.0063),(-.020,.0092),(-.019,.0095),(-.0185,.0102),(-.017,.0102),(-.0165,.0096),(-.0155,.0096),(-.015,.0102),(-.0135,.0102),(-.013,.0096),(-.008,.0096),(-.008,.0053),(-.029,.0053)],rubber)
  upper_cover=annular(prefix+' moving hollow upper neck cover - estimated',ball_world,A,[(-.011,.0143),(-.0108,.0145),(.0098,.0140),(.010,.0138),(.010,.0114),(.008,.0114),(.004,.0130),(-.011,.0130)],neck_plastic)
  fullpieces=[stem,washer,nut,base_cover,lower_cover,upper_cover]
  for o in fullpieces:
   for f in o.data.polygons:f.use_smooth=True
   o.data.set_sharp_from_angle(angle=.65);physical_uv(o)
  headpieces=objects+[upper_cover];pivot=bpy.data.objects.new(prefix+' mirror head adjustment PIVOT',None);source.objects.link(pivot);pivot.location=ball_world;bpy.context.view_layer.update()
  for o in headpieces:
   o.parent=pivot;o.matrix_parent_inverse=pivot.matrix_world.inverted()
  base_cover.data.materials.clear();base_cover.data.materials.append(neck_plastic)
  objects.extend(fullpieces);bpy.context.view_layer.update()
  P['linked_mount_source_path']=str(linked.relative_to(ROOT));P['linked_mount_source_sha256']=hashlib.sha256(linked.read_bytes()).hexdigest();P['stem_centreline_world_m']=[list(x)for x in path];P['ball_world_m']=list(ball_world);P['neck_axis_world']=list(A);P['head_pitch_axis_world']=list(U)
  (HERE/('parameters-'+side+'.json')).write_text(json.dumps(P,indent=2)+'\n')

 for o in objects:
  bm=bmesh.new();bm.from_mesh(o.data);unseen=set(bm.verts);components=0
  while unseen:
   components+=1;stack=[unseen.pop()]
   while stack:
    for e in stack.pop().link_edges:
     for v in e.verts:
      if v in unseen:unseen.remove(v);stack.append(v)
  row={'object':o.name,'vertices':len(bm.verts),'faces':len(bm.faces),'components':components,'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_m3':bm.calc_volume(signed=True)};bm.free();assert row['components']==1 and not row['non_manifold_edges'] and row['volume_m3']>0,row;checks.append(row)
 for o in construction.objects:o.hide_render=True;o.hide_set(True)
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 if phase=='full':pivot.select_set(True)
 bpy.context.view_layer.objects.active=shell
 stem='mirror-'+side+('-shell-study-v1' if phase=='shell' else '-head-study' if phase=='head' else '-v1');bpy.ops.export_scene.gltf(filepath=str(HERE/(stem+'.glb')),export_format='GLB',use_selection=True,export_apply=True,export_tangents=True)
 # Neutral studio in true geometry; no photographic backplate.
 def mat(name,color,rough=.8):
  m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;return m
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,.04));floor=bpy.context.object;floor.name=prefix+' mirror studio floor'
 for c in list(floor.users_collection):c.objects.unlink(floor)
 studio.objects.link(floor);floor.data.materials.append(mat(prefix+' mirror studio neutral',(.075,.085,.10)))
 scene.world=bpy.data.worlds.new(prefix+' mirror neutral world');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.30,.34,.40,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.35
 for name,location,power,size in [('KEY',C+U*.22+up*.35-N*.30,15,.30),('FILL',C-U*.25+up*.15+N*.25,8,.30),('EDGE',C+U*.05+up*.30+N*.35,10,.22)]:
  data=bpy.data.lights.new(prefix+' mirror '+name,'AREA');data.energy=power;data.shape='DISK';data.size=size;o=bpy.data.objects.new(data.name,data);studio.objects.link(o);o.location=location;o.rotation_euler=(C-location).to_track_quat('-Z','Y').to_euler()
 cam=bpy.data.objects.new(prefix+' mirror CAMERA',bpy.data.cameras.new(prefix+' mirror CAMERA'));studio.objects.link(cam);scene.camera=cam;cam.location=C-N*.48+U*.12+up*.10;cam.rotation_euler=(C-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=75
 scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.cycles.denoiser='OPENIMAGEDENOISE';scene.cycles.denoising_use_gpu=False;scene.render.resolution_x=900;scene.render.resolution_y=700;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
 source_path=HERE/(stem+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(source_path),compress=True)
 report={'component_id':P['component_id'],'phase':phase+' isolated candidate, exact identity/dimensions unresolved','source_sha256':hashlib.sha256(source_path.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((HERE/(stem+'.glb')).read_bytes()).hexdigest(),'geometry':checks,'CSG':history,'head_frame_world':{'centre_m':list(C),'outward_U':list(U),'up_V':list(V),'normal_toward_rider_N':list(N),'left_positive_X':side=='left'},'mount_boss_world_m':P['mount_boss_centre_world_m'],'ball_world_m':P.get('ball_world_m'),'linked_mount_source_path':P.get('linked_mount_source_path'),'linked_mount_source_sha256':P.get('linked_mount_source_sha256'),'all_dimensions_estimated':True,'exact_current_RDC_identity_confirmed':False,'art_accepted':False};(OUT/('shell-study-v1-check.json' if phase=='shell' else 'head-study-check.json' if phase=='head' else 'source-geometry-check.json')).write_text(json.dumps(report,indent=2)+'\n');print('MIRROR_SHELL_STUDY',json.dumps(report))
