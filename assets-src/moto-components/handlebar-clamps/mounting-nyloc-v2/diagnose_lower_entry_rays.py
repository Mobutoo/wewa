import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
root=Path('/workspace/wewa-github');h=root/'assets-src/moto-components/handlebar-clamps/mounting-nyloc-v2';source=h/'handlebar-mount-nyloc-v2.blend';bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;c=s.camera;c.location=(.030,.033,-.026);c.rotation_euler=(Vector((0,0,.004))-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=.029;bpy.context.view_layer.update();metal=next(o for o in bpy.data.collections['WEWA_HANDLEBAR_MOUNT_NYLOC_ISOLATED'].objects if o.name.startswith('Locknut'));m=metal.data;tree=BVHTree.FromPolygons([v.co for v in m.vertices],[list(p.vertices)for p in m.polygons],all_triangles=True);frame=c.data.view_frame(scene=s);left=min(q.x for q in frame);right=max(q.x for q in frame);bottom=min(q.y for q in frame);top=max(q.y for q in frame);rotation=c.matrix_world.to_3x3();direction=rotation@Vector((0,0,-1));rows=[]
def radial(z,a):
 phase=(z/.0015-a/math.tau)%1;f=0 if phase<.125 else(phase-.125)/.3125 if phase<.4375 else 1 if phase<.5625 else(.875-phase)/.3125 if phase<.875 else 0;minor=.00506-5*math.sqrt(3)*.0015/16;nominal=minor+(.00506-minor)*f;ease=max(0,min(1,(z-.00035)/.00055,(.0069-z)/.00055));return nominal*ease+.0052*(1-ease),phase,ease
for y in[650,675,690,700,725,750,775,800,820]:
 for x in[480,540,600,660,720]:
  origin=c.matrix_world@Vector((left+(right-left)*x/1200,top-(top-bottom)*y/1000,0));hit,n,face,distance=tree.ray_cast(origin,direction,1)
  if hit is None:continue
  r=math.hypot(hit.x,hit.y);expected,phase,ease=radial(hit.z,math.atan2(hit.y,hit.x));rows.append({'pixel':[x,y],'source_xyz_m':list(hit),'radius_m':r,'z_mm':hit.z*1000,'phase':phase,'ease':ease,'radius_minus_analytic_thread_m':r-expected,'source_face_index':face,'face_normal':list(n),'material_index':m.polygons[face].material_index})
curves=[]
for z in[.00035,.0009,.00095,.001,.0011]:
 points=[]
 for i in range(289):
  a=math.tau*i/288;r,phase,ease=radial(z,a);q=Vector((r*math.cos(a),r*math.sin(a),z));p=world_to_camera_view(s,c,q);points.append([p.x*1200,(1-p.y)*1000])
 curves.append({'z_m':z,'projected_analytic_curve_pixels':points})
r={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((h/'handlebar-mount-nyloc-v2-inspection.glb').read_bytes()).hexdigest(),'image_dimensions_px':[1200,1000],'source_or_buffer_modified':False,'ray_samples':rows,'analytical_runout_curves':curves,'runout_function':'Linear clipped blend from radius5.2mm atz.35mm to full profile atz.90mm; dimensions estimated','diagnostic_not_art_acceptance':True};(root/'creative/research/handlebar-clamps/nyloc-v2-lower-entry-diagnostic.json').write_text(json.dumps(r,indent=2)+'\n');print('RAY_SAMPLES',json.dumps(rows))
