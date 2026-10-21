"""New immutable source revision: analytic normals for modeled head cylinder and side-mouth cylinder only."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/wewa');old='front-completion-p23-rear-axle-v1';key='front-completion-p23-rear-axle-v2';H=R/'assets-src/moto-components'/key;O=R/'creative/reviews'/key;H.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True);source=R/'assets-src/moto-components'/old/'rear-axle-gray.blend';bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.preferences.filepaths.save_version=0;ob=next(o for o in bpy.data.objects if o.type=='MESH');m=ob.data;assert all(len(p.vertices)==3 for p in m.polygons)
def signature():return hashlib.sha256(json.dumps({'vertices':[list(v.co)for v in m.vertices],'faces':[list(p.vertices)for p in m.polygons]},separators=(',',':')).encode()).hexdigest()
before=signature();corners=[n.vector.copy()for n in m.corner_normals];norms=[];counts={'head_outer':0,'mouth_inner':0,'geometric_fallback':0}
for p in m.polygons:
 pts=[m.vertices[i].co for i in p.vertices];c=p.center;rr=math.hypot(c.x,c.y);radial=Vector((c.x/rr,c.y/rr,0))if rr>1e-10 else Vector((1,0,0));outer=all(abs(math.hypot(v.x,v.y)-.0118)<3e-6 and .00069<v.z<.00731 for v in pts)and p.normal.dot(radial)>.5;mouth=(not outer)and all(abs(math.hypot(v.y,v.z-.004)-.0025)<1.2e-6 and v.x>=-1e-7 for v in pts)and abs(p.normal.x)<.1
 aa,bb,cc=pts;x=[float(bb[k])-float(aa[k])for k in range(3)];y=[float(cc[k])-float(aa[k])for k in range(3)];cross=(x[1]*y[2]-x[2]*y[1],x[2]*y[0]-x[0]*y[2],x[0]*y[1]-x[1]*y[0]);length=math.sqrt(sum(v*v for v in cross));geom=Vector(tuple(v/length for v in cross))
 if outer or mouth:p.use_smooth=True
 for li in p.loop_indices:
  v=m.vertices[m.loops[li].vertex_index].co;n=corners[li]
  if outer:n=Vector((v.x,v.y,0)).normalized();counts['head_outer']+=1
  elif mouth:n=Vector((0,-v.y,-(v.z-.004))).normalized();counts['mouth_inner']+=1
  if n.dot(geom)<.2:n=geom;counts['geometric_fallback']+=1
  norms.append(tuple(n))
m.normals_split_custom_set(norms);m.update();after=signature();assert before==after
bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.wm.save_as_mainfile(filepath=str(H/'rear-axle-gray.blend'),compress=True);bpy.ops.export_scene.gltf(filepath=str(H/'rear-axle-gray.glb'),export_format='GLB',use_selection=True,export_tangents=False,export_animations=False);P=json.loads((R/'assets-src/moto-components'/old/'parameters.json').read_text());P['normal_method']='Analytic source head radial normals and inward side-mouth cylinder normals, geometric triangle guard; other source normals retained';P['parent_source_sha256']=hashlib.sha256(source.read_bytes()).hexdigest();(H/'parameters.json').write_text(json.dumps(P,indent=2));(O/'normal-revision.json').write_text(json.dumps({'positions_and_topology_unchanged':True,'geometry_signature_before':before,'geometry_signature_after':after,'parent_source':str(source.relative_to(R)),'parent_source_sha256':P['parent_source_sha256'],'source_normal_changes':counts,'method':P['normal_method'],'no_export_buffer_patch':True},indent=2));print(counts)
