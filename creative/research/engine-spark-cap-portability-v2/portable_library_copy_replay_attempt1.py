"""Blender CLI: inspect/fingerprint, change only in-checkout Library paths, save a NEW companion.
--source --output --original-root --component-collection --report are mandatory paths/names.
Does not change Image paths, pack data, render, export or save the original source.
"""
import argparse,sys,json,hashlib,os
from pathlib import Path
import bpy,numpy as np

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def value(x):
 if isinstance(x,(str,int,float,bool))or x is None:return x
 try:return [value(v)for v in x]
 except TypeError:return str(x)
def digest(x,dtype=None):
 a=np.asarray(x,dtype=dtype);return {'shape':list(a.shape),'dtype':str(a.dtype),'sha256':hashlib.sha256(a.tobytes()).hexdigest()}
def mesh_fingerprint(me):
 me.calc_loop_triangles();fields={'positions':digest([tuple(v.co)for v in me.vertices],np.float32),'loop_vertex_indices':digest([l.vertex_index for l in me.loops],np.int32),'triangles':digest([tuple(t.vertices)for t in me.loop_triangles],np.int32),'polygon_material_indices':digest([p.material_index for p in me.polygons],np.int32),'corner_normals':digest([tuple(n.vector)for n in me.corner_normals],np.float32),'UV':{u.name:digest([tuple(v.uv)for v in u.data],np.float32)for u in me.uv_layers},'attributes':[]}
 for att in me.attributes:
  prop=next((p for p in ['value','vector','color','uv']if len(att.data)and hasattr(att.data[0],p)),None)
  if not prop and len(att.data):raise RuntimeError('Unsupported attribute '+att.name+' '+att.data_type)
  fields['attributes'].append({'name':att.name,'domain':att.domain,'type':att.data_type,'data':digest([getattr(v,prop)for v in att.data])})
 return fields
def material_fingerprint(m):
 if m is None:return None
 nodes=[];links=[]
 if m.use_nodes:
  for n in sorted(m.node_tree.nodes,key=lambda n:n.name):
   d={'name':n.name,'type':n.bl_idname,'inputs':[{'identifier':i.identifier,'name':i.name,'default':value(i.default_value)if hasattr(i,'default_value')else None}for i in n.inputs]}
   for prop in ['operation','blend_type','distribution','subsurface_method','interpolation','extension','projection','uv_map','attribute_name','vector_type','space','invert','normalize']:
    if hasattr(n,prop):d[prop]=value(getattr(n,prop))
   if hasattr(n,'image')and n.image:
    i=n.image;d['image']={'name':i.name,'filepath':i.filepath,'colorspace':i.colorspace_settings.name,'size':list(i.size),'packed':bool(i.packed_file),'packed_sha256':hashlib.sha256(i.packed_file.data).hexdigest()if i.packed_file else None}
   if hasattr(n,'color_ramp'):d['color_ramp']={'interpolation':n.color_ramp.interpolation,'elements':[[e.position,list(e.color)]for e in n.color_ramp.elements]}
   nodes.append(d)
  links=sorted([l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier]for l in m.node_tree.links)
 return {'name':m.name,'use_nodes':m.use_nodes,'diffuse_color':list(m.diffuse_color),'metallic':m.metallic,'roughness':m.roughness,'nodes':nodes,'links':links}
def fingerprint(collection):
 bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();rows=[]
 for o in sorted(bpy.data.collections[collection].all_objects,key=lambda o:o.name):
  e=o.evaluated_get(deps);row={'object':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'object_local':o.library is None,'hide_render':o.hide_render,'matrix_basis':[list(r)for r in o.matrix_basis],'matrix_parent_inverse':[list(r)for r in o.matrix_parent_inverse],'matrix_world_evaluated':[list(r)for r in e.matrix_world]}
  if o.type=='MESH':
   row['mesh_name']=o.data.name;row['mesh_local']=o.data.library is None;row['raw_mesh']=mesh_fingerprint(o.data);me=e.to_mesh(preserve_all_data_layers=True,depsgraph=deps)
   try:row['evaluated_mesh']=mesh_fingerprint(me)
   finally:e.to_mesh_clear()
   row['materials']=[material_fingerprint(m)for m in o.data.materials]
  rows.append(row)
 return {'collection':collection,'objects':rows}
def libraries():
 rows=[]
 for l in bpy.data.libraries:
  p=Path(bpy.path.abspath(l.filepath,library=l.parent)).resolve();rows.append({'name':l.name,'filepath':l.filepath,'parent':l.parent.name if l.parent else None,'is_indirect':l.is_library_indirect,'resolved':str(p),'exists':p.is_file(),'sha256':sha(p)if p.is_file()else None})
 return sorted(rows,key=lambda r:r['name'])
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for arg in ['source','output','original-root','component-collection','report']:p.add_argument('--'+arg,required=True)
 p.add_argument('--checkout-root',help='Current checkout containing source and dependencies; defaults to original-root. Supports an old absolute path prefix in a moved working source.')
 a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=Path(a.source).resolve();output=Path(a.output).resolve();root=Path(a.original_root).resolve();checkout=Path(a.checkout_root).resolve()if a.checkout_root else root;report=Path(a.report).resolve();assert source.is_file()and source.is_relative_to(checkout);assert output!=source and not output.exists();before_sha=sha(source)
 bpy.ops.wm.open_mainfile(filepath=str(source));before=fingerprint(a.component_collection);links_before=libraries();collection_scope=[{'name':c.name,'hidden_viewport':c.hide_viewport,'linked_object_names':[o.name for o in c.all_objects if o.library]}for c in bpy.data.collections if any(o.library for o in c.all_objects)];remaps=[]
 # Resolve every link BEFORE changing any strings, including possible parent contexts.
 resolved={l.name:Path(bpy.path.abspath(l.filepath,library=l.parent)).resolve()for l in bpy.data.libraries}
 for lib in bpy.data.libraries:
  target=resolved[lib.name]
  if target.is_relative_to(root):rel=target.relative_to(root)
  elif target.is_relative_to(checkout):rel=target.relative_to(checkout)
  else:continue
  original_target=target;target=checkout/rel;assert target.is_file(),target
  # Refuse ambiguous indirect edits: they belong to another immutable source file.
  if lib.parent is not None:raise RuntimeError('Indirect Library requires explicit companion for its owner: '+lib.name)
  new='//'+os.path.relpath(target,output.parent).replace(os.sep,'/');remaps.append({'name':lib.name,'before':lib.filepath,'after':new,'target_repo_relative':str(rel),'target_sha256':sha(target)});lib.filepath=new
  if original_target!=target:lib.reload() # Resolve context data from the current checkout, never the old absolute prefix.
 assert fingerprint(a.component_collection)==before,'Component changed before save';output.parent.mkdir(parents=True,exist_ok=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(output),check_existing=False,relative_remap=False,copy=True)
 assert sha(source)==before_sha
 bpy.ops.wm.open_mainfile(filepath=str(output));after=fingerprint(a.component_collection);links_after=libraries();result={'tool_sha256':sha(__file__),'source':str(source),'source_sha256':before_sha,'output':str(output),'output_sha256':sha(output),'original_root':str(root),'checkout_root':str(checkout),'component_collection':a.component_collection,'scope':'Only Library filepath strings remapped. Component source stays local, context guides stay linked. Image paths unchanged; packed image bytes compared. No render/export.','before':before,'after':after,'component_exact_before_after':before==after,'libraries_before':links_before,'libraries_after':links_after,'remaps':remaps,'linked_context_collections':collection_scope,'original_source_unchanged':sha(source)==before_sha}
 report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(result,indent=2)+'\n');assert before==after,'Component after-save/open fingerprint differs';assert all(v['filepath'].startswith('//')for v in links_after if Path(v['resolved']).is_relative_to(checkout));print('PORTABLE_COMPANION_EXACT',sha(output),len(remaps),flush=True)
if __name__=='__main__':main()
