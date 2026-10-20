"""Compare authored PNG texels to actual images embedded in panel v2 glTF."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='wewa-material-parity-') as temp:
 script="""import {NodeIO} from '@gltf-transform/core';import fs from 'node:fs/promises';
 const root=(await new NodeIO().read(process.argv[1])).getRoot();
 for(const texture of root.listTextures())await fs.writeFile(process.argv[2]+'/'+texture.getName()+'.png',texture.getImage());
 const material=root.listMaterials()[0];console.log(JSON.stringify({normal_scale:material.getNormalScale(),basecolor_factor:material.getBaseColorFactor()}));"""
 export=ROOT/'assets-src/moto-components/front-brake-plate/front-brake-plate-v2-inspection.glb'
 shader=json.loads(subprocess.check_output(['node','--input-type=module','-e',script,str(export),temp],cwd=ROOT,text=True))
 maps=[]
 for name in ['cast-grain-normal','cast-metallic-roughness']:
  path=ROOT/'assets-src/moto-components/front-brake-plate/textures-v2'/(name+'.png')
  a=np.asarray(Image.open(path).convert('RGB')).astype(int);b=np.asarray(Image.open(Path(temp)/(name+'.png')).convert('RGB')).astype(int)
  row={'map':name,'source_export_pixels_identical':bool(np.array_equal(a,b)),'maximum_channel_difference_8bit':int(np.abs(a-b).max()),'channel_min':a.min(axis=(0,1)).tolist(),'channel_max':a.max(axis=(0,1)).tolist(),'channel_stddev':a.std(axis=(0,1)).tolist()}
  assert row['source_export_pixels_identical'],row
  if name.endswith('normal'):assert min(row['channel_stddev'][:2])>1,'Flat normal map'
  else:assert row['channel_stddev'][1]>1 and row['channel_min'][2]==179,'Incorrect PBR packing'
  maps.append(row)
 assert abs(shader['normal_scale']-.65)<1e-6,shader
 report={'scope':'Encoded PBR texture equality, not pixel-identical shading under different renderers/lights','export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'maps':maps,'shader':shader,'source_normal_strength':.65,'common_physical_uv_tile_m':.010,'format_and_data_parity_passed':True,'visual_parity_accepted':False,'physical_iphone_tested':False,'art_accepted':False}
 (ROOT/'creative/reviews/front-brake-plate-v2/material-parity-check.json').write_text(json.dumps(report,indent=2)+'\n')
 print('WEWA_PBR_DATA_PARITY',json.dumps(report))
