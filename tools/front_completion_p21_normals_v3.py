"""Explicit source normals from the modeled bore and helical tool surface, never GLB buffer repair."""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');old='front-completion-p21-carrier-v2';key='front-completion-p21-carrier-v3';H=R/'assets-src/moto-components'/key;O=R/'creative/reviews'/key;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'assets-src/moto-components'/old/'carrier-gray.blend'));bpy.context.preferences.filepaths.save_version=0;ob=next(o for o in bpy.data.objects if o.type=='MESH');m=ob.data;bm=bmesh.new();bm.from_mesh(m);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.update();
for face in m.polygons:face.use_smooth=True
m.update();corners=[n.vector.copy() for n in m.corner_normals];norms=[];changed=0
for p in m.polygons:
 aa,bb,cc=[m.vertices[i].co for i in p.vertices[:3]];xx=[float(bb[k])-float(aa[k]) for k in range(3)];yy=[float(cc[k])-float(aa[k]) for k in range(3)];geom=Vector((xx[1]*yy[2]-xx[2]*yy[1],xx[2]*yy[0]-xx[0]*yy[2],xx[0]*yy[1]-xx[1]*yy[0])).normalized()
 c=p.center;angle=min([0,math.pi/2,math.pi,3*math.pi/2],key=lambda a:math.hypot(c.x-.047*math.cos(a),c.y-.047*math.sin(a)));cx=.047*math.cos(angle);cy=.047*math.sin(angle);midr=math.hypot(c.x-cx,c.y-cy)
 for li in p.loop_indices:
  n=corners[li];v=m.vertices[m.loops[li].vertex_index].co;dx=v.x-cx;dy=v.y-cy;r=math.hypot(dx,dy)
  if midr<.0041 and r>1e-9:
   radial=Vector((dx/r,dy/r,0));n0=p.normal.copy()
   if midr<.003501:n=-radial
   elif .0225<c.z<.0273:
    a=math.atan2(dy,dx);z0=.0232+.0012*(a-.17)/(2*math.pi);zhelix=z0+round((v.z-z0)/.0012)*.0012;tangent=Vector((-radial.y*.0035,radial.x*.0035,.0012/(2*math.pi))).normalized();offset=(r-.0035)*radial+Vector((0,0,v.z-zhelix));offset-=offset.dot(tangent)*tangent;n=-offset.normalized() if offset.length>1e-10 else n0
   else:n=n0
   if n.dot(n0)<.25:n=n0
   changed+=1
  if n.dot(geom)<.2:n=geom
  if p.normal.z>.98 and c.z>.02699 and c.z<.02701:n=Vector((0,0,1))
  norms.append(tuple(n))
for p in m.polygons:p.use_smooth=True
m.normals_split_custom_set(norms);m.update();bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.wm.save_as_mainfile(filepath=str(H/'carrier-gray.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/'carrier-gray.glb'),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False);P=json.loads((R/'assets-src/moto-components'/old/'parameters.json').read_text());P['normal_method']='Source loop normals derived from bore radial and swept helical tool surface; geometric face fallback where analytic continuation disagrees; body v2 normals preserved';(H/'parameters.json').write_text(json.dumps(P,indent=2));(O/'normal-revision.json').write_text(json.dumps({'surface_positions_changed':False,'final_source_ngons_triangulated':True,'changed_corner_normals':changed,'method':P['normal_method'],'v2_source_sha256':hashlib.sha256((R/'assets-src/moto-components'/old/'carrier-gray.blend').read_bytes()).hexdigest()},indent=2))
