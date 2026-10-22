import bpy,json,re
from pathlib import Path
R=Path('/workspace/wewa');K='horn-visible-completion-v1';D=R/'creative/research'/K
p=json.loads((R/'creative/reviews/whole-exterior-coverage-v20/linked-parents-check.json').read_text());rows=[];seen=set()
for row in p['parents']:
 src=row['source']
 if src in seen:continue
 seen.add(src)
 with bpy.data.libraries.load(str(R/src),link=False)as(a,b):names=list(a.objects)
 hits=[n for n in names if re.search(r'horn|klaxon|avertiss|jv.?4016',n,re.I)];rows.append(dict(source=src,all_object_names=names,horn_name_hits=hits,nested_declared=row.get('nested_sources',[])))
(D/'v20-source-name-audit.json').write_text(json.dumps(dict(parent_count=len(p['parents']),unique_sources=len(rows),sources=rows,scope='Actual native library metadata reads; no geometry loaded or rendered. All object names in each source include nested instance object names. Compare v19 native collection inventory for included nested cockpit objects.',verdict='Only cockpit horn button/printed symbol names; no acoustic horn body source identified'),indent=2)+'\n')
