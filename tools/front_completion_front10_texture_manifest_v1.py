"""Read actual packed GLB image channels and material texture bindings, no visual acceptance."""
from pathlib import Path
from PIL import Image
import json,struct,io,hashlib,sys
R=Path('/workspace/wewa');p=R/sys.argv[1];out=R/sys.argv[2];b=p.read_bytes();o=12;j=None;binary=None
while o<len(b):
 n,t=struct.unpack_from('<II',b,o);chunk=b[o+8:o+8+n]
 if t==0x4e4f534a:j=json.loads(chunk)
 if t==0x004e4942:binary=chunk
 o+=8+n
images=[]
for i,img in enumerate(j.get('images',[])):
 v=j['bufferViews'][img['bufferView']];data=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];im=Image.open(io.BytesIO(data));im.load();channels={}
 for name,ch in zip(im.getbands(),im.split()):
  hist=ch.histogram();channels[name]={'minimum':ch.getextrema()[0],'maximum':ch.getextrema()[1],'unique_values':sum(bool(n)for n in hist),'histogram':{str(i):n for i,n in enumerate(hist)if n}}
 images.append({'image_index':i,'name':img.get('name'),'mimeType':img.get('mimeType'),'sha256':hashlib.sha256(data).hexdigest(),'resolution':list(im.size),'mode':im.mode,'actual_channels':channels})
materials=[{'index':i,'name':m.get('name'),'pbr':m.get('pbrMetallicRoughness'),'normalTexture':m.get('normalTexture')}for i,m in enumerate(j.get('materials',[]))]
rows=[]
for mesh in j.get('meshes',[]):
 for prim in mesh['primitives']:rows.append({'mesh':mesh.get('name'),'material':prim.get('material'),'attributes':prim['attributes']})
out.write_text(json.dumps({'GLB':str(p.relative_to(R)),'sha256':hashlib.sha256(b).hexdigest(),'images':images,'textures':j.get('textures',[]),'materials':materials,'primitive_bindings':rows,'scope':'Actual packed image bytes, decoded channel histograms and material/attribute bindings. No grain/UV-scale/photometry/art acceptance inferred.'},indent=2));print(len(images),'packed images inspected')
