"""Decode actual embedded native GLB image payloads, not shader-node promises."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[3];O=R/'creative/reviews/engine-intake-manifold-v1'
D=Path('/workspace/wewa-assets/work-in-progress/engine-intake-manifold/exported-v1-textures')
report=json.loads((O/'material-export-check.json').read_text())
UV=np.asarray(json.loads((D/'actual_UV_vertices_and_triangle_centres.json').read_text()),dtype=np.float64)
rows=[]
for texture in report['textures']:
    path=Path(texture['extracted_actual_embedded_bytes']);assert hashlib.sha256(path.read_bytes()).hexdigest()==texture['sha256']
    a=np.asarray(Image.open(path).convert('RGB'),dtype=np.float64)/255.;h,w=a.shape[:2]
    # glTF's upper-left UV origin matches the actual native PNG row order.
    x=np.clip(UV[:,0]*w-.5,0,w-1);y=np.clip(UV[:,1]*h-.5,0,h-1)
    ix=np.floor(x).astype(int);iy=np.floor(y).astype(int);jx=np.minimum(ix+1,w-1);jy=np.minimum(iy+1,h-1)
    fx=(x-ix)[:,None];fy=(y-iy)[:,None]
    b=(a[iy,ix]*(1-fx)+a[iy,jx]*fx)*(1-fy)+(a[jy,ix]*(1-fx)+a[jy,jx]*fx)*fy
    row={**texture,'size_px':[w,h],'actual_UV_sample_count':len(UV),'UV_sample_min_rgb':b.min(axis=0).tolist(),
         'UV_sample_max_rgb':b.max(axis=0).tolist(),'UV_sample_std_rgb':b.std(axis=0).tolist(),
         'UV_outside_unit_square':int(np.any((UV<0)|(UV>1),axis=1).sum()),'sampled_not_exhaustive_filtering_proof':True}
    if texture['role']=='normal':
        assert min(b[:,0].std(),b[:,1].std())>.001,'Actual normal payload is constant'
        assert b[:,2].min()>.9,'Normal texture has dark holes on actual UV samples'
    else:
        assert b[:,1].std()>.001,'Actual roughness payload is constant'
        assert b[:,1].min()>.4 and b[:,1].max()<.61,'Actual mesh UVs touch unpainted padding'
        row['effective_metallic_max']=float(b[:,2].max()*report['native_exported_material']['metallic'])
        row['effective_metallic_min']=float(b[:,2].min()*report['native_exported_material']['metallic'])
        assert row['effective_metallic_min']>.99,'Cast alloy lost its native metallic factor'
    rows.append(row)
result={'source_sha256':report['source_sha256'],'export_sha256':report['export_sha256'],'textures':rows,
        'pixel_payloads_decoded':True,'original_grain_not_photo_pixels':True,'OEM_grain_or_material_measured':False,'art_accepted':False}
(O/'actual-embedded-map-pixel-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
