"""Original clean dark polymer proposal; no photo texture or measured compound."""
from pathlib import Path
import bpy,json,hashlib,sys,array
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/ignition-connector-v2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
B=json.loads((H/'geometry-report-v2.json').read_text());G=json.loads((O/'geometry-preview-review-v2.json').read_text())
assert G['ready_for_representative_material'] and G['source_sha256']==B['source_sha256']
assert not(H/'preflight-manifest-v2.json').exists()
source0=H/'ignition-connector-v2-geometry.blend';assert sha(source0)==B['source_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source0));o=bpy.data.objects[B['geometry'][0]['name']];m=o.data
def signature():
    m.calc_loop_triangles();d={}
    for name,seq,key,n in [('positions',m.vertices,'co',3),('corner_normals',m.corner_normals,'vector',3)]:
        a=array.array('f',[0.]*(len(seq)*n));seq.foreach_get(key,a);d[name]=hashlib.sha256(a.tobytes()).hexdigest()
    d['UV']=[]
    for layer in m.uv_layers:
        a=array.array('f',[0.]*(len(layer.data)*2));layer.data.foreach_get('uv',a);d['UV'].append(hashlib.sha256(a.tobytes()).hexdigest())
    d['indices']=hashlib.sha256(array.array('I',[i for t in m.loop_triangles for i in t.vertices]).tobytes()).hexdigest()
    d['object_matrix']=[list(q)for q in o.matrix_world];d['root_matrix']=[list(q)for q in o.parent.matrix_world]
    return d
before=signature();mat=m.materials[0].copy();mat.name='Original dark injection housing proposal - compound unknown';m.materials.clear();m.materials.append(mat)
p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.008,.010,.012,1);p.inputs['Metallic'].default_value=0;p.inputs['Roughness'].default_value=.37
assert signature()==before
sys.path.insert(0,str(H.parent/'throttle-control'));from control_geometry import export
source=H/'ignition-connector-v2.blend';glb=H/'ignition-connector-v2-inspection.glb'
export(glb,[o.parent,o]);bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
r={**B,'geometry_source_sha256':B['source_sha256'],'geometry_export_sha256':B['export_sha256'],'source_sha256':sha(source),'export_sha256':sha(glb),'source_protected_geometry_signatures':before,'source_geometry_exact':True,'material':{'linear_basecolor':[.008,.010,.012],'metallic':0,'roughness':.37,'status':'Original estimated clean dark polymer proposal based on qualitative PF232605 photo. No measured compound, roughness or grain amplitude. Native crop does not resolve reliable micro-height; no invented normal map.','texture_images':0},'art_accepted':False}
(H/'build-report-v2.json').write_text(json.dumps(r,indent=2)+'\n');(O/'source-material-check.json').write_text(json.dumps(r,indent=2)+'\n')
assert sha(source0)==B['source_sha256'];print('MATERIAL_CONNECTOR_V2',sha(source),sha(glb))
