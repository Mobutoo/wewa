"""Working USB materials/UV after gray shape review; original project maps only."""
import bpy,hashlib,json
from pathlib import Path

def apply_materials(objects,here):
 out=[];tile=.010
 for key,o in objects.items():
  mesh=o.data;mesh.update();uv=mesh.uv_layers.new(name='USB metric box projection estimated 10mm tile');axes=[]
  for face in mesh.polygons:
   dominant=max(range(3),key=lambda k:abs(face.normal[k]));pair={0:(1,2),1:(2,0),2:(0,1)}[dominant];sign=1 if face.normal[dominant]>=0 else-1;axes.append(dominant)
   for loop in face.loop_indices:
    co=mesh.vertices[mesh.loops[loop].vertex_index].co;uv.data[loop].uv=(co[pair[0]]/tile,sign*co[pair[1]]/tile)
  mesh.calc_loop_triangles();areas=[]
  for tri in mesh.loop_triangles:
   a,b,c=[uv.data[i].uv for i in tri.loops];areas.append(abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))/2)
  assert min(areas)>0,(key,min(areas))
  material=bpy.data.materials.new('USB '+key+' working black polymer v2');material.use_nodes=True;n=material.node_tree.nodes;links=material.node_tree.links;bs=n.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.008,.009,.010,1)if key=='surround'else(.007,.008,.009,1);bs.inputs['Roughness'].default_value=1;bs.inputs['Metallic'].default_value=1
  def image(name,file):
   tex=n.new('ShaderNodeTexImage');tex.name=name;im=bpy.data.images.load(str(file),check_existing=True);im.colorspace_settings.name='Non-Color';im.pack();tex.image=im;tex.extension='REPEAT';return tex
  normal=image('Original project micrograin normal - not photo',here/'textures-v2/usb/original-polymer-normal.png');normalnode=n.new('ShaderNodeNormalMap');normalnode.space='TANGENT';normalnode.inputs['Strength'].default_value=.65 if key=='surround'else .85;links.new(normal.outputs['Color'],normalnode.inputs['Color']);links.new(normalnode.outputs['Normal'],bs.inputs['Normal']);mr=image('Original USB metallic roughness pixels',here/('textures-v2/usb/'+key+'-metallic-roughness.png'));sep=n.new('ShaderNodeSeparateColor');links.new(mr.outputs['Color'],sep.inputs['Color']);links.new(sep.outputs['Green'],bs.inputs['Roughness']);links.new(sep.outputs['Blue'],bs.inputs['Metallic']);mesh.materials.clear();mesh.materials.append(material)
  material['surface_identity']='Estimated render materials; visible nested boundaries do not establish actual OEM material split';material['grain_tile_m_working']=tile;material['UV_method']='Per-face dominant-plane box projection at10mm repeat; isotropic micrograin, UV seams and local distortion not measured surface grain';out.append({'object':o.name,'material':material.name,'UV_projection':'per-face dominant plane, local coordinates in metres /10mm','UV_min_triangle_area':min(areas),'UV_exact_collapsed_triangles':sum(a==0 for a in areas),'normal_scale':normalnode.inputs['Strength'].default_value,'metallic_map_B_zero':True})
 return out
