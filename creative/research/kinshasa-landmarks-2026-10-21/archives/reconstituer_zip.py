"""Reconstitue le ZIP original et vérifie son intégrité SHA-256 (Python 3)."""
import hashlib,json
from pathlib import Path
base=Path(__file__).resolve().parent
meta=json.loads((base/'archive_manifest.json').read_text())
target=base/meta['filename']
for part in meta['parts']:
    data=(base/part['name']).read_bytes()
    if len(data)!=part['bytes'] or hashlib.sha256(data).hexdigest()!=part['sha256']:
        raise ValueError('Partie manquante ou altérée : '+part['name'])
with target.open('wb') as out:
    for part in meta['parts']:
        out.write((base/part['name']).read_bytes())
if target.stat().st_size!=meta['bytes'] or hashlib.sha256(target.read_bytes()).hexdigest()!=meta['sha256']:
    raise ValueError('Intégrité du ZIP incorrecte')
print('ZIP reconstitué et vérifié :',target)
