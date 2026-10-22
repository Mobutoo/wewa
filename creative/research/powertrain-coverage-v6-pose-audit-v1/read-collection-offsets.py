"""Read four individual intake collection offsets only; never load whole72 or save sources."""
import bpy,json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent;R=D.parents[2];j=json.loads((D/'native-collection-inventory-v6-snapshot.json').read_text());rows=[];wanted=['engine-intake-insulator-v2','engine-intake-manifold','engine-intake-sleeve','engine-intake-clamp-band'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for e in j['inputs']:
 if e['key']not in wanted:continue
 p=R/e['source_blend'];before=sha(p);assert before==e['blend_sha256'];bpy.ops.wm.open_mainfile(filepath=str(p));c=bpy.data.collections[e['catalog_collection']];offset=list(c.instance_offset);assert sha(p)==before
 rows.append(dict(key=e['key'],source=e['source_blend'],source_sha256=before,collection=c.name,instance_offset=offset,zero_offset=all(abs(x)<1e-12 for x in offset),source_unchanged=True))
assert len(rows)==4
(D/'collection-offsets.json').write_text(json.dumps(dict(scope='Read four sources sequentially, metadata only. Other eight selected-object coverage collections are newly created by v6 builder at default zero offset. No whole72 load, no render or source save.',parents=rows),indent=2)+'\n')
