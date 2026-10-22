"""Collect actual loaded native dependencies plus actual glTF resources, without copying binary assets."""
import bpy,json,sys,hashlib
from pathlib import Path
from urllib.parse import unquote
R=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:];native=R/args[0];gltf=R/args[1];out=R/args[2];assert Path(bpy.data.filepath).resolve()==native.resolve();files={};sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def add(p,kind):
 p=Path(p).resolve();assert p.is_relative_to(R),('Nonportable external dependency',str(p));assert p.is_file(),str(p);rel=str(p.relative_to(R));row=files.setdefault(rel,dict(path=rel,bytes=p.stat().st_size,sha256=sha(p),usage=[]));
 if kind not in row['usage']:row['usage'].append(kind)
add(native,'native')
for lib in bpy.data.libraries:
 p=Path(bpy.path.abspath(lib.filepath))
 if not p.is_file()and lib.parent:p=Path(bpy.path.abspath(lib.filepath,library=lib.parent))
 add(p,'native')
packed=[]
for image in bpy.data.images:
 if image.type in ['RENDER_RESULT','COMPOSITING']or not image.filepath:continue
 if image.packed_file or len(image.packed_files):packed.append(image.name);continue
 add(bpy.path.abspath(image.filepath,library=image.library),'native')
add(gltf,'runtime');data=json.loads(gltf.read_text())
for row in data.get('buffers',[])+data.get('images',[]):
 u=row.get('uri')
 if u and not u.startswith('data:'):add(gltf.parent/unquote(u),'runtime')
proof=Path(str(gltf)+'.proof.json')
if proof.exists():add(proof,'runtime')
for x in [R/'package.json',R/'package-lock.json',R/'tools/motorcycle-complete-review/index.html',R/'tools/motorcycle-complete-review/viewer.js']:
 if x.exists():add(x,'viewer_optional')
out.parent.mkdir(exist_ok=True,parents=True);out.write_text(json.dumps(dict(schema=1,repository='Mobutoo/wewa',native_model=str(native.relative_to(R)),runtime_model=str(gltf.relative_to(R)),scope='Exact existing model resources needed to reconstruct source/native or runtime layout; original reference photographs not included',files=sorted(files.values(),key=lambda f:f['path']),packed_native_images=packed,art_accepted=False),indent=2)+'\n');print('PORTABLE_MODEL_RESOURCES',len(files),sum(r['bytes']for r in files.values()))
