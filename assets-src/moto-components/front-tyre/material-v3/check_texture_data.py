"""Read actual source PNG pixels, raw IHDR and exported sampler defaults."""
from pathlib import Path
import json,struct,hashlib
import numpy as np
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[3];O=R/'creative/reviews/front-tyre-v3'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
binary=(H/'front-tyre-v3-inspection.glb').read_bytes();n=struct.unpack_from('<I',binary,12)[0];g=json.loads(binary[20:20+n]);rows=[]
for p in sorted((H/'textures').glob('*.png')):
    with Image.open(p)as image:a=np.asarray(image);mode=image.mode
    r={'path':str(p.relative_to(R)),'sha256':sha(p),'size_px':[a.shape[1],a.shape[0]],'raw_IHDR_bit_depth':p.read_bytes()[24],
       'raw_IHDR_color_type':p.read_bytes()[25],'mode':mode,'RGB_min':a.min((0,1)).tolist(),'RGB_max':a.max((0,1)).tolist(),'RGB_mean':a.mean((0,1)).tolist()}
    assert r['raw_IHDR_bit_depth']==8 and r['mode']=='RGB'
    if 'normal'in p.name:
        v=a.astype(np.float32)/127.5-1;length=np.linalg.norm(v,axis=2)
        r['decoded_normal_length']={'min':float(length.min()),'max':float(length.max()),'mean':float(length.mean())}
        r['fraction_nonflat_RG']=float(((a[:,:,0]!=128)|(a[:,:,1]!=128)).mean())
        assert r['fraction_nonflat_RG']>.5 and r['decoded_normal_length']['min']>.98
    else:
        r['AO_R_all255']=bool((a[:,:,0]==255).all());r['metallic_B_all0']=bool((a[:,:,2]==0).all())
        assert r['AO_R_all255']and r['metallic_B_all0']
    rows.append(r)
samplers=[{**s,'effective_wrapS':s.get('wrapS',10497),'effective_wrapT':s.get('wrapT',10497)}for s in g.get('samplers',[])]
assert samplers and all(s.get('magFilter')==9729 and s.get('minFilter')==9987 and s['effective_wrapS']==s['effective_wrapT']==10497 for s in samplers)
r={'source_sha256':sha(H/'front-tyre-v3.blend'),'export_sha256':sha(H/'front-tyre-v3-inspection.glb'),'script_sha256':sha(Path(__file__)),
 'images':rows,'actual_glTF_samplers_with_specification_defaults':samplers,'actual_glTF_textures':g['textures'],'actual_glTF_materials':g['materials'],
 'export_warning':'More than one shader node tex image used for a texture; sampler follows first node. Author constructs both image nodes Linear/Repeat; actualGLB uses linear filtering/repeat for both maps.',
 'normal_image_rows':'Raw native bottomup pixels explicitly reversed to PNGtopdown, no view transform. ActualGLB image bytes equal and UV0 preserved.',
 'native_reflectance_or_exact_continuous_shader_received':False,'art_accepted':False}
(O/'texture-pixel-data-check.json').write_text(json.dumps(r,indent=2)+'\n');print('TYRE_V3_ACTUAL_PNG_DATA',len(rows))
